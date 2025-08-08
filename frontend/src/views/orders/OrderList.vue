<template>
  <div class="order-list-container">
    <div class="page-header">
      <h2>订单管理</h2>
      <el-button type="primary" @click="handleAddOrder" :icon="Plus">
        新建订单
      </el-button>
    </div>

    <!-- 搜索卡片 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="订单编号">
          <el-input 
            v-model="searchForm.order_number" 
            placeholder="请输入订单编号" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="客户订单号">
          <el-input 
            v-model="searchForm.customer_order_number" 
            placeholder="请输入客户订单号" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="客户">
          <el-select 
            v-model="searchForm.customer" 
            placeholder="请选择客户" 
            clearable 
            filterable
            style="width: 200px"
          >
            <el-option 
              v-for="customer in customerOptions" 
              :key="customer.id"
              :label="customer.name" 
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="请选择状态" 
            clearable 
            style="width: 150px"
          >
            <el-option 
              v-for="option in ORDER_STATUS_OPTIONS" 
              :key="option.value"
              :label="option.label" 
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单表格 -->
    <el-card class="table-card">
      <el-table 
        :data="orderList" 
        v-loading="loading" 
        stripe 
        border
        style="width: 100%"
      >
        <el-table-column prop="order_number" label="订单编号" width="150" fixed="left" />
        <el-table-column prop="customer_order_number" label="客户订单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="150" />
        <el-table-column prop="order_date" label="下单日期" width="120" />
        <el-table-column prop="delivery_date" label="交货日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link 
              @click="handleDelete(scope.row)"
              v-if="scope.row.status === 'pending' || scope.row.status === 'cancelled'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { 
  getOrderList, 
  updateOrder, 
  deleteOrder,
  getCustomerList 
} from '@/api/orders'
import type { Order, Customer } from '@/types/orders'
import { ORDER_STATUS_OPTIONS, getStatusTagType, getStatusLabel } from '@/types/orders'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  order_number: '',
  customer_order_number: '',
  customer: null as number | null,
  status: ''
})

// 表格数据
const loading = ref(false)
const orderList = ref<Order[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 客户选项
const customerOptions = ref<Customer[]>([])

onMounted(() => {
  fetchOrderList()
  fetchCustomers()
})

// 获取订单列表
const fetchOrderList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      order_number: searchForm.order_number || undefined,
      customer_order_number: searchForm.customer_order_number || undefined,
      customer: searchForm.customer || undefined,
      status: searchForm.status || undefined
    }
    
    console.log('开始获取订单列表, 参数:', params)
    
    const res: any = await getOrderList(params)
    console.log('订单列表API响应:', res)
    
    if (res) {
      // 检查是否是分页响应格式
      if (typeof res === 'object' && 'results' in res && 'count' in res) {
        console.log('分页模式 - 结果数:', res.count, '当前页数据:', res.results.length)
        orderList.value = res.results || []
        total.value = res.count || 0
      } else if (Array.isArray(res)) {
        console.log('数组模式 - 数据长度:', res.length)
        orderList.value = res
        total.value = res.length
      } else if (typeof res === 'object' && res.data) {
        // 检查是否有data字段包装
        if (Array.isArray(res.data)) {
          orderList.value = res.data
          total.value = res.data.length
        } else if (typeof res.data === 'object' && 'results' in res.data) {
          orderList.value = res.data.results || []
          total.value = res.data.count || 0
        }
      } else {
        console.warn('未知的数据格式:', res)
        orderList.value = [] as Order[]
        total.value = 0
      }
    } else {
      console.warn('API返回数据为空:', res)
      orderList.value = [] as Order[]
      total.value = 0
    }
    
    console.log('最终订单列表长度:', orderList.value.length)
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
    orderList.value = [] as Order[]
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 获取客户列表
const fetchCustomers = async () => {
  try {
    console.log('开始获取客户选项列表')
    const res = await getCustomerList({ is_active: true })
    console.log('客户选项API响应:', res)
    
    if (res) {
      if (Array.isArray(res)) {
        customerOptions.value = res
      } else if (typeof res === 'object' && 'results' in res) {
        customerOptions.value = res.results || []
      } else if (typeof res === 'object' && res.data) {
        if (Array.isArray(res.data)) {
          customerOptions.value = res.data
        } else if (typeof res.data === 'object' && 'results' in res.data) {
          customerOptions.value = res.data.results || []
        }
      } else {
        customerOptions.value = []
      }
      console.log('客户选项列表长度:', customerOptions.value.length)
    } else {
      console.warn('客户选项API返回数据为空:', res)
      customerOptions.value = [] as Customer[]
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
    customerOptions.value = [] as Customer[]
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchOrderList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.order_number = ''
  searchForm.customer_order_number = ''
  searchForm.customer = null
  searchForm.status = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchOrderList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchOrderList()
}

// 新建订单
const handleAddOrder = () => {
  router.push('/orders/create')
}

// 编辑订单
const handleEdit = (row: Order) => {
  router.push(`/orders/${row.id}/edit`)
}

// 删除订单
const handleDelete = async (row: Order) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除订单"${row.order_number}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteOrder(row.id)
    ElMessage.success('删除成功')
    fetchOrderList()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN')
}
</script>

<style scoped>
.order-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style> 