<template>
  <div class="outbound-list-container">
    <div class="page-header">
      <h2>出库单管理</h2>
      <el-button type="primary" @click="handleAddOutbound">
        <el-icon><Plus /></el-icon>新增出库单
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="出库单号">
          <el-input
            v-model="searchForm.outbound_number"
            placeholder="输入出库单号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="客户">
          <el-select
            v-model="searchForm.customer"
            placeholder="选择客户"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="item in customerOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="outboundList" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="outbound_number" label="出库单号" min-width="150" />
        <el-table-column prop="order_number" label="关联订单" min-width="150">
          <template #default="scope">
            {{ scope.row.order_number || '无' }}
          </template>
        </el-table-column>
        <el-table-column prop="outbound_date" label="出库日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="scope">
            {{ scope.row.created_at ? new Date(scope.row.created_at).toLocaleString('zh-CN') : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleView(scope.row)"
              text
            >
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleEdit(scope.row)"
              text
              v-if="scope.row.status === 'draft'"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleConfirm(scope.row)"
              text
              v-if="scope.row.status === 'draft'"
            >
              确认出库
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="handleCancel(scope.row)"
              text
              v-if="scope.row.status === 'confirmed'"
            >
              取消出库
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              text
              v-if="scope.row.status === 'draft'"
            >
              <el-icon><Delete /></el-icon>删除
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { getOutboundList, deleteOutbound, getCustomerList, confirmOutbound, cancelOutbound } from '@/api/inventory'
import type { ProductOutbound, Customer } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  outbound_number: '',
  customer: undefined as number | undefined,
  status: undefined as string | undefined,
  start_date: undefined as string | undefined,
  end_date: undefined as string | undefined
})

// 日期范围
const dateRange = ref<[string, string] | null>(null)

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val) {
    searchForm.start_date = val[0]
    searchForm.end_date = val[1]
  } else {
    searchForm.start_date = undefined
    searchForm.end_date = undefined
  }
})

// 客户选项
const customerOptions = ref<Customer[]>([])

// 数据列表
const outboundList = ref<ProductOutbound[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 获取客户列表
const fetchCustomers = async () => {
  try {
    const res = await getCustomerList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        customerOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
  }
}

// 获取出库单列表
const fetchOutboundList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    const res = await getOutboundList(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        outboundList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取出库单列表失败:', error)
    ElMessage.error('获取出库单列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchOutboundList()
}

// 重置搜索
const handleReset = () => {
  searchForm.outbound_number = ''
  searchForm.customer = undefined
  searchForm.status = undefined
  searchForm.start_date = undefined
  searchForm.end_date = undefined
  dateRange.value = null
  currentPage.value = 1
  fetchOutboundList()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchOutboundList()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchOutboundList()
}

// 新增出库单
const handleAddOutbound = () => {
  router.push('/inventory/outbound-create')
}

// 查看详情
const handleView = (row: ProductOutbound) => {
  router.push(`/inventory/outbound-detail/${row.id}`)
}

// 编辑出库单
const handleEdit = (row: ProductOutbound) => {
  router.push(`/inventory/outbound-edit/${row.id}`)
}

// 确认出库
const handleConfirm = (row: ProductOutbound) => {
  ElMessageBox.confirm(
    `确定要确认出库单 "${row.outbound_number}" 吗？确认后将减少相应产品库存`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await confirmOutbound(row.id)
      ElMessage.success('确认出库成功')
      fetchOutboundList()
    } catch (error: any) {
      console.error('确认出库失败:', error)
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`确认出库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('确认出库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 取消出库
const handleCancel = (row: ProductOutbound) => {
  ElMessageBox.confirm(
    `确定要取消出库单 "${row.outbound_number}" 吗？取消后将恢复相应产品库存`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelOutbound(row.id)
      ElMessage.success('取消出库成功')
      fetchOutboundList()
    } catch (error: any) {
      console.error('取消出库失败:', error)
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`取消出库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('取消出库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 删除出库单
const handleDelete = (row: ProductOutbound) => {
  ElMessageBox.confirm(
    `确定要删除出库单 "${row.outbound_number}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteOutbound(row.id)
      ElMessage.success('删除成功')
      fetchOutboundList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'draft': 'info',
    'confirmed': 'success',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'draft': '草稿',
    'confirmed': '已确认',
    'cancelled': '已取消'
  }
  return map[status] || '未知'
}



onMounted(() => {
  fetchCustomers()
  fetchOutboundList()
})
</script>

<style scoped>
.outbound-list-container {
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

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 