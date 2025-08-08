<template>
  <div class="order-list-container">
    <div class="page-header">
      <h2>生产订单管理</h2>
      <el-button type="primary" @click="handleAddOrder">
        <el-icon><Plus /></el-icon>新建订单
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单编号">
          <el-input v-model="searchForm.orderNo" placeholder="请输入订单编号" clearable />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="searchForm.productName" placeholder="请输入产品名称" clearable />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待生产" value="pending" />
            <el-option label="生产中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="orderList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="orderNo" label="订单编号" width="150" />
        <el-table-column prop="productName" label="产品名称" min-width="120" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="planStartDate" label="计划开始日期" width="150" />
        <el-table-column prop="planEndDate" label="计划完成日期" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="180">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button
              size="small"
              type="success"
              @click="handleViewProgress(scope.row)"
              :disabled="scope.row.status === 'cancelled'"
            >查看进度</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleCancel(scope.row)"
              :disabled="scope.row.status === 'completed' || scope.row.status === 'cancelled'"
            >取消</el-button>
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新建生产订单' : '编辑生产订单'"
      width="600px"
    >
      <el-form
        ref="orderFormRef"
        :model="orderForm"
        :rules="orderRules"
        label-width="120px"
      >
        <el-form-item label="产品名称" prop="productName">
          <el-select v-model="orderForm.productName" placeholder="请选择产品" style="width: 100%">
            <el-option label="专业花样冰刀" value="专业花样冰刀" />
            <el-option label="速滑冰刀" value="速滑冰刀" />
            <el-option label="儿童冰球冰刀" value="儿童冰球冰刀" />
          </el-select>
        </el-form-item>
        <el-form-item label="生产数量" prop="quantity">
          <el-input-number v-model="orderForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划开始日期" prop="planStartDate">
          <el-date-picker
            v-model="orderForm.planStartDate"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="计划完成日期" prop="planEndDate">
          <el-date-picker
            v-model="orderForm.planEndDate"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="订单状态" prop="status">
          <el-select v-model="orderForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="待生产" value="pending" />
            <el-option label="生产中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="orderForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 定义订单类型接口
interface Order {
  id: number
  orderNo: string
  productName: string
  quantity: number
  planStartDate: string
  planEndDate: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  progress: number
  createTime: string
  remark?: string
}

// 搜索表单
const searchForm = reactive({
  orderNo: '',
  productName: '',
  status: ''
})

// 表格数据
const loading = ref(false)
const orderList = ref<Order[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const orderFormRef = ref<FormInstance>()
const orderForm = reactive({
  id: 0,
  orderNo: '',
  productName: '',
  quantity: 1,
  planStartDate: '',
  planEndDate: '',
  status: 'pending' as 'pending' | 'in_progress' | 'completed' | 'cancelled',
  progress: 0,
  remark: ''
})

// 表单验证规则
const orderRules = {
  productName: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入生产数量', trigger: 'blur' }
  ],
  planStartDate: [
    { required: true, message: '请选择计划开始日期', trigger: 'change' }
  ],
  planEndDate: [
    { required: true, message: '请选择计划完成日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择订单状态', trigger: 'change' }
  ]
}

// 生命周期钩子
onMounted(() => {
  fetchOrderList()
})

// 获取订单列表
const fetchOrderList = () => {
  loading.value = true
  // 这里应该调用API获取数据
  // 模拟API调用
  setTimeout(() => {
    orderList.value = [
      {
        id: 1,
        orderNo: 'PO20230301001',
        productName: '专业花样冰刀',
        quantity: 50,
        planStartDate: '2023-03-05',
        planEndDate: '2023-03-15',
        status: 'in_progress',
        progress: 60,
        createTime: '2023-03-01 10:00:00'
      },
      {
        id: 2,
        orderNo: 'PO20230302001',
        productName: '速滑冰刀',
        quantity: 30,
        planStartDate: '2023-03-10',
        planEndDate: '2023-03-20',
        status: 'pending',
        progress: 0,
        createTime: '2023-03-02 14:30:00'
      },
      {
        id: 3,
        orderNo: 'PO20230303001',
        productName: '儿童冰球冰刀',
        quantity: 100,
        planStartDate: '2023-02-20',
        planEndDate: '2023-03-01',
        status: 'completed',
        progress: 100,
        createTime: '2023-03-03 09:15:00'
      }
    ]
    total.value = 3
    loading.value = false
  }, 500)
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchOrderList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.orderNo = ''
  searchForm.productName = ''
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

// 添加订单
const handleAddOrder = () => {
  dialogType.value = 'add'
  orderForm.id = 0
  orderForm.orderNo = generateOrderNo()
  orderForm.productName = ''
  orderForm.quantity = 1
  orderForm.planStartDate = ''
  orderForm.planEndDate = ''
  orderForm.status = 'pending'
  orderForm.progress = 0
  orderForm.remark = ''
  dialogVisible.value = true
}

// 生成订单编号
const generateOrderNo = () => {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `PO${year}${month}${day}${random}`
}

// 编辑订单
const handleEdit = (row: Order) => {
  dialogType.value = 'edit'
  orderForm.id = row.id
  orderForm.orderNo = row.orderNo
  orderForm.productName = row.productName
  orderForm.quantity = row.quantity
  orderForm.planStartDate = row.planStartDate
  orderForm.planEndDate = row.planEndDate
  orderForm.status = row.status
  orderForm.progress = row.progress
  orderForm.remark = row.remark || ''
  dialogVisible.value = true
}

// 查看进度
const handleViewProgress = (row: Order) => {
  router.push(`/production/progress?orderId=${row.id}`)
}

// 取消订单
const handleCancel = (row: Order) => {
  ElMessageBox.confirm(
    `确定要取消订单 "${row.orderNo}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用API取消订单
    ElMessage.success('订单已取消')
    fetchOrderList()
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!orderFormRef.value) return
  
  await orderFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该调用API保存数据
      ElMessage.success(dialogType.value === 'add' ? '订单创建成功' : '订单更新成功')
      dialogVisible.value = false
      fetchOrderList()
    }
  })
}

// 获取状态标签样式
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待生产',
    in_progress: '生产中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || '未知'
}

// 获取进度条状态
const getProgressStatus = (row: Order) => {
  if (row.status === 'completed') return 'success'
  if (row.status === 'cancelled') return 'exception'
  return ''
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