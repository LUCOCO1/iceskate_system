<template>
  <div class="production-order-list-container">
    <div class="page-header">
      <h2>生产订单管理</h2>
      <el-button type="primary" @click="handleAddOrder">
        <el-icon><Plus /></el-icon>新建生产订单
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="生产单号">
          <el-input v-model="searchForm.order_number" placeholder="请输入生产单号" clearable />
        </el-form-item>
        <el-form-item label="产品">
          <el-select v-model="searchForm.product" placeholder="请选择产品" clearable filterable>
            <el-option
              v-for="item in productOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待生产" value="pending" />
            <el-option label="备料完成" value="material_ready" />
            <el-option label="生产中" value="in_production" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
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
        <el-table-column prop="order_number" label="生产单号" min-width="150" />
        <el-table-column prop="product_name" label="产品" min-width="150" />
        <el-table-column label="数量" width="150">
          <template #default="scope">
            <div>计划: {{ scope.row.planned_quantity }}</div>
            <div>完成: {{ scope.row.completed_quantity }}</div>
          </template>
        </el-table-column>
        <el-table-column label="日期" width="150">
          <template #default="scope">
            <div>计划: {{ scope.row.start_date }} 至 {{ scope.row.end_date }}</div>
            <div v-if="scope.row.actual_start_date">实际: {{ scope.row.actual_start_date }} 
              <template v-if="scope.row.actual_end_date">至 {{ scope.row.actual_end_date }}</template>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="120">
          <template #default="scope">
            <el-progress :percentage="Number(scope.row.progress) || 0" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ getPriorityLabel(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="scope">
            <!-- 流程指示器 -->
            <div class="workflow-indicator" style="margin-bottom: 8px;">
              <el-steps :active="getWorkflowStep(scope.row.status)" simple finish-status="success">
                <el-step title="待生产" />
                <el-step title="备料完成" />
                <el-step title="生产中" />
                <el-step title="已完成" />
              </el-steps>
            </div>
            
            <!-- 操作按钮组 -->
            <div class="action-buttons">
              <!-- 基本操作 -->
              <el-button 
                type="primary" 
                size="small" 
                @click="handleViewDetail(scope.row)"
              >
                <el-icon><View /></el-icon>详情
              </el-button>
              
              <!-- 流程操作按钮 -->
              <el-tooltip 
                v-if="scope.row.status === 'pending'"
                content="请先完成备料" 
                placement="top"
              >
                <el-button 
                  type="warning" 
                  size="small" 
                  @click="handleMaterialReady(scope.row)"
                  class="pulse-animation"
                >
                  <el-icon><Check /></el-icon>备料完成
                </el-button>
              </el-tooltip>
              
              <el-tooltip 
                v-else-if="scope.row.status === 'material_ready'"
                content="备料已完成，可以开始生产" 
                placement="top"
              >
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="handleStartProduction(scope.row)"
                  class="pulse-animation"
                >
                  <el-icon><VideoPlay /></el-icon>开始生产
                </el-button>
              </el-tooltip>
              
              <template v-else-if="scope.row.status === 'in_production'">
                <el-button 
                  type="info" 
                  size="small" 
                  @click="handleRecordProgress(scope.row)"
                >
                  <el-icon><Calendar /></el-icon>记录进度
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="handleCompleteProduction(scope.row)"
                  class="pulse-animation"
                >
                  <el-icon><CircleCheck /></el-icon>完成生产
                </el-button>
              </template>
              
              <!-- 其他操作 -->
              <el-dropdown v-if="scope.row.status === 'pending' || scope.row.status === 'completed'">
                <el-button size="small" type="info">
                  更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      v-if="scope.row.status === 'pending'"
                      @click="handleEdit(scope.row)"
                    >
                      <el-icon><Edit /></el-icon>编辑
                    </el-dropdown-item>
                    <el-dropdown-item 
                      v-if="scope.row.status === 'pending'"
                      @click="handleDelete(scope.row)"
                      divided
                    >
                      <el-icon><Delete /></el-icon>删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <!-- 禁用状态提示 -->
              <template v-if="scope.row.status !== 'pending' && scope.row.status !== 'material_ready' && scope.row.status !== 'in_production'">
                <el-tooltip 
                  v-for="action in getDisabledActions(scope.row.status)"
                  :key="action.name"
                  :content="action.tooltip" 
                  placement="top"
                >
                  <el-button 
                    size="small" 
                    :disabled="true"
                    style="margin-left: 5px;"
                  >
                    <el-icon><component :is="action.icon" /></el-icon>{{ action.label }}
                  </el-button>
                </el-tooltip>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 进度记录对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="记录生产进度"
      width="500px"
    >
      <el-form :model="progressForm" label-width="120px">
        <el-form-item label="生产单号">
          <el-input v-model="currentOrder.order_number" disabled />
        </el-form-item>
        <el-form-item label="产品">
          <el-input v-model="currentOrder.product_name" disabled />
        </el-form-item>
        <el-form-item label="记录日期">
          <el-date-picker
            v-model="progressForm.record_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="完成数量">
          <el-input-number
            v-model="progressForm.quantity"
            :min="0"
            :max="currentOrder.planned_quantity"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="progressForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="progressDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProgress">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 完成生产对话框 -->
    <el-dialog
      v-model="completeDialogVisible"
      title="完成生产"
      width="500px"
    >
      <el-form :model="completeForm" label-width="120px">
        <el-form-item label="生产单号">
          <el-input v-model="currentOrder.order_number" disabled />
        </el-form-item>
        <el-form-item label="产品">
          <el-input v-model="currentOrder.product_name" disabled />
        </el-form-item>
        <el-form-item label="计划数量">
          <el-input v-model="currentOrder.planned_quantity" disabled />
        </el-form-item>
        <el-form-item label="已完成数量">
          <el-input v-model="currentOrder.completed_quantity" disabled />
        </el-form-item>
        <el-form-item label="本次完成数量">
          <el-input-number
            v-model="completeForm.actual_quantity"
            :min="0"
            :max="currentOrder.planned_quantity"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="completeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCompleteProduction">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Refresh, 
  View, 
  Edit, 
  Delete, 
  Check, 
  Calendar, 
  CircleCheck,
  VideoPlay,
  ArrowDown
} from '@element-plus/icons-vue'
import { 
  getProductionOrderList, 
  deleteProductionOrder, 
  materialReadyProductionOrder,
  startProductionOrder,
  recordProductionProgress,
  completeProductionOrder
} from '@/api/production'
import { getProductList } from '@/api/inventory'
import type { ProductionOrder } from '@/types/production'
import type { Product } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  order_number: '',
  product: '',
  status: '',
  priority: ''
})

// 查询参数
const query = reactive({
  page: 1,
  page_size: 10,
  ...searchForm
})

// 订单列表数据
const orderList = ref<ProductionOrder[]>([])
const loading = ref(false)
const total = ref(0)

// 产品选项
const productOptions = ref<Product[]>([])
const loadingProducts = ref(false)

// 当前选中的订单（用于对话框）
const currentOrder = ref<ProductionOrder>({} as ProductionOrder)

// 进度记录对话框
const progressDialogVisible = ref(false)
const progressForm = reactive({
  record_date: new Date().toISOString().split('T')[0],
  quantity: 0,
  notes: ''
})

// 完成生产对话框
const completeDialogVisible = ref(false)
const completeForm = reactive({
  actual_quantity: 0
})

// 生命周期钩子
onMounted(() => {
  fetchOrderList()
  fetchProducts()
})

// 获取订单列表
const fetchOrderList = async () => {
  loading.value = true
  try {
    const res = await getProductionOrderList({
      page: query.page,
      page_size: query.page_size,
      order_number: query.order_number || undefined,
      product: query.product || undefined,
      status: query.status || undefined,
      priority: query.priority || undefined
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        orderList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取生产订单列表失败:', error)
    ElMessage.error('获取生产订单列表失败')
  } finally {
    loading.value = false
  }
}

// 获取产品列表
const fetchProducts = async () => {
  loadingProducts.value = true
  try {
    const res = await getProductList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        productOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
  } finally {
    loadingProducts.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  Object.assign(query, searchForm)
  fetchOrderList()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  query.page = 1
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  query.page_size = val
  fetchOrderList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchOrderList()
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'material_ready': 'warning',
    'in_production': 'success',
    'completed': 'primary'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待生产',
    'material_ready': '备料完成',
    'in_production': '生产中',
    'completed': '已完成'
  }
  return map[status] || '未知'
}

// 获取优先级标签类型
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return map[priority] || 'info'
}

// 获取优先级标签文本
const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = {
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return map[priority] || '未知'
}

// 获取工作流程步骤
const getWorkflowStep = (status: string) => {
  const map: Record<string, number> = {
    'pending': 0,
    'material_ready': 1,
    'in_production': 2,
    'completed': 3
  }
  return map[status] || 0
}

// 获取禁用操作列表
const getDisabledActions = (status: string) => {
  const actions = []
  
  if (status === 'completed') {
    actions.push(
      { name: 'material', label: '备料完成', icon: 'Check', tooltip: '订单已完成，无需备料' },
      { name: 'start', label: '开始生产', icon: 'VideoPlay', tooltip: '订单已完成' },
      { name: 'progress', label: '记录进度', icon: 'Calendar', tooltip: '订单已完成' }
    )
  }
  
  return actions
}

// 新建生产订单
const handleAddOrder = () => {
  router.push('/production/production-order-create')
}

// 编辑订单
const handleEdit = (row: ProductionOrder) => {
  router.push(`/production/production-order-edit/${row.id}`)
}

// 查看详情
const handleViewDetail = (row: ProductionOrder) => {
  router.push(`/production/production-order-detail/${row.id}`)
}

// 删除订单
const handleDelete = (row: ProductionOrder) => {
  ElMessageBox.confirm(
    `确定要删除生产订单 "${row.order_number}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProductionOrder(row.id)
      ElMessage.success('删除成功')
      fetchOrderList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 备料完成
const handleMaterialReady = (row: ProductionOrder) => {
  ElMessageBox.confirm(
    `确定要将生产订单 "${row.order_number}" 标记为备料完成吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await materialReadyProductionOrder(row.id)
      ElMessage.success('备料完成标记成功')
      fetchOrderList()
    } catch (error: any) {
      console.error('备料完成操作失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`备料完成操作失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('备料完成操作失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 开始生产
const handleStartProduction = (row: ProductionOrder) => {
  ElMessageBox.confirm(
    `确定要开始生产订单 "${row.order_number}" 吗？开始后将扣减相应材料库存`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await startProductionOrder(row.id)
      ElMessage.success('开始生产成功')
      fetchOrderList()
    } catch (error: any) {
      console.error('开始生产失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`开始生产失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('开始生产失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 记录进度
const handleRecordProgress = (row: ProductionOrder) => {
  currentOrder.value = row
  progressForm.quantity = 0
  progressForm.notes = ''
  progressForm.record_date = new Date().toISOString().split('T')[0]
  progressDialogVisible.value = true
}

// 提交进度记录
const submitProgress = async () => {
  if (progressForm.quantity <= 0) {
    ElMessage.warning('请输入有效的完成数量')
    return
  }

  try {
    // 修正字段名称，与后端API保持一致
    const progressData = {
      completed_quantity: progressForm.quantity,
      notes: progressForm.notes
    }
    await recordProductionProgress(currentOrder.value.id, progressData)
    ElMessage.success('进度记录成功')
    progressDialogVisible.value = false
    fetchOrderList()
  } catch (error: any) {
    console.error('进度记录失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(`进度记录失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('进度记录失败，请稍后重试')
    }
  }
}

// 完成生产
const handleCompleteProduction = (row: ProductionOrder) => {
  currentOrder.value = row
  completeForm.actual_quantity = row.completed_quantity > 0 ? row.completed_quantity : row.planned_quantity
  completeDialogVisible.value = true
}

// 提交完成生产
const submitCompleteProduction = async () => {
  if (completeForm.actual_quantity <= 0) {
    ElMessage.warning('请输入有效的完成数量')
    return
  }

  try {
    // 修正字段名称，与后端API保持一致
    const completeData = {
      completed_quantity: completeForm.actual_quantity
    }
    await completeProductionOrder(currentOrder.value.id, completeData)
    ElMessage.success('完成生产成功')
    completeDialogVisible.value = false
    fetchOrderList()
  } catch (error: any) {
    console.error('完成生产失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(`完成生产失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('完成生产失败，请稍后重试')
    }
  }
}
</script>

<style scoped>
.production-order-list-container {
  padding: 20px;
  color: #000;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.page-header h2 {
  color: #000;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-form {
  padding: 10px 0;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 操作按钮文字样式 */
:deep(.el-button) {
  min-width: 90px;
  margin: 2px;
  font-weight: normal; /* 不加粗 */
}

/* 普通按钮文字颜色为黑色 */
.el-button:not(.el-button--primary, .el-button--success, .el-button--warning, .el-button--danger, .el-button--info):not(.is-disabled) {
  color: #000;
}

/* 更简洁的方式设置所有主题按钮的文字颜色为黑色 */
.el-table .el-button--primary,
.el-table .el-button--success, 
.el-table .el-button--warning,
.el-table .el-button--danger,
.el-table .el-button--info {
  color: #000 !important;
}

.el-table .el-button span,
.el-table .el-button i {
  color: #000;
}

.el-tag {
  font-weight: bold;
  padding: 6px 10px;
}

:deep(.el-table) {
  color: #000;
}

:deep(.el-table th) {
  color: #000;
  font-weight: bold;
}

:deep(.el-table td) {
  color: #000;
}

:deep(.el-form-item__label) {
  color: #000;
  font-weight: 500;
}

:deep(.el-input__inner) {
  color: #000;
}

:deep(.el-pagination) {
  color: #000;
}

:deep(.el-pagination button) {
  color: #000;
}

/* 工作流程指示器样式 */
.workflow-indicator {
  padding: 0 10px;
}

.workflow-indicator :deep(.el-steps--simple) {
  background: transparent;
}

/* 操作按钮组样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

/* 脉冲动画效果 - 用于提示用户下一步操作 */
.pulse-animation {
  animation: pulse 2s infinite;
  position: relative;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}

/* 不同状态按钮的脉冲颜色 */
.el-button--warning.pulse-animation {
  animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
  0% {
    box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(230, 162, 60, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(230, 162, 60, 0);
  }
}

.el-button--danger.pulse-animation {
  animation: pulse-danger 2s infinite;
}

@keyframes pulse-danger {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

.el-button--success.pulse-animation {
  animation: pulse-success 2s infinite;
}

@keyframes pulse-success {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}
</style> 