<template>
  <div class="production-order-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>生产订单详情</h2>
      </div>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleEdit"
          v-if="['pending'].includes(order.status)"
          :icon="Edit"
        >
          编辑
        </el-button>
        <el-button 
          type="success" 
          @click="handleMaterialReady"
          v-if="order.status === 'pending'"
          :icon="Check"
        >
          备料完成
        </el-button>
        <el-button 
          type="warning" 
          @click="handleStartProduction"
          v-if="order.status === 'material_ready'"
          :icon="VideoPlay"
        >
          开始生产
        </el-button>
        <el-button 
          type="info" 
          @click="handleRecordProgress"
          v-if="order.status === 'in_production'"
          :icon="Calendar"
        >
          记录进度
        </el-button>
        <el-button 
          type="danger" 
          @click="handleCompleteProduction"
          v-if="order.status === 'in_production'"
          :icon="CircleCheck"
        >
          完成生产
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStatusType(order.status)">
            {{ getStatusLabel(order.status) }}
          </el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="生产单号">{{ order.order_number }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ order.product_name }}</el-descriptions-item>
        <el-descriptions-item label="计划数量">{{ order.planned_quantity }}</el-descriptions-item>
        <el-descriptions-item label="已完成数量">{{ order.completed_quantity }}</el-descriptions-item>
        <el-descriptions-item label="计划日期">{{ order.start_date }} 至 {{ order.end_date }}</el-descriptions-item>
        <el-descriptions-item label="实际日期">
          {{ order.actual_start_date || '尚未开始' }}
          <template v-if="order.actual_end_date"> 至 {{ order.actual_end_date }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(order.priority)">
            {{ getPriorityLabel(order.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">
          <el-progress :percentage="order.progress || 0" />
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ order.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ order.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ order.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 材料需求 -->
    <el-card class="items-card" v-if="materialRequirements.length > 0">
      <template #header>
        <div class="card-header">
          <span>材料需求</span>
        </div>
      </template>
      <el-table :data="materialRequirements" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column prop="material_specification" label="规格" min-width="120" />
        <el-table-column label="需求数量" width="120">
          <template #default="scope">
            {{ scope.row.required_quantity }}
          </template>
        </el-table-column>
        <el-table-column label="实际用量" width="120">
          <template #default="scope">
            {{ scope.row.actual_quantity }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
      </el-table>
    </el-card>

    <!-- 生产进度记录 -->
    <el-card class="items-card" v-if="progressRecords.length > 0">
      <template #header>
        <div class="card-header">
          <span>生产进度记录</span>
        </div>
      </template>
      <el-table :data="progressRecords" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="record_date" label="记录日期" width="120" />
        <el-table-column label="完成数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }}
          </template>
        </el-table-column>
        <el-table-column label="累计数量" width="120">
          <template #default="scope">
            {{ scope.row.accumulated_quantity }}
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button 
              type="danger" 
              size="small" 
              @click="handleCancelProgress(scope.row)"
              v-if="scope.row.can_edit"
            >
              <el-icon><Delete /></el-icon>撤销
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 进度记录对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="记录生产进度"
      width="500px"
    >
      <el-form :model="progressForm" label-width="120px">
        <el-form-item label="生产单号">
          <el-input v-model="order.order_number" disabled />
        </el-form-item>
        <el-form-item label="产品">
          <el-input v-model="order.product_name" disabled />
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
            :max="order.planned_quantity"
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
          <el-input v-model="order.order_number" disabled />
        </el-form-item>
        <el-form-item label="产品">
          <el-input v-model="order.product_name" disabled />
        </el-form-item>
        <el-form-item label="计划数量">
          <el-input v-model="order.planned_quantity" disabled />
        </el-form-item>
        <el-form-item label="已完成数量">
          <el-input v-model="order.completed_quantity" disabled />
        </el-form-item>
        <el-form-item label="本次完成数量">
          <el-input-number
            v-model="completeForm.actual_quantity"
            :min="0"
            :max="order.planned_quantity"
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Edit, 
  Check, 
  Calendar, 
  CircleCheck, 
  Delete,
  VideoPlay 
} from '@element-plus/icons-vue'
import { 
  getProductionOrderDetail,
  materialReadyProductionOrder,
  startProductionOrder,
  recordProductionProgress,
  completeProductionOrder,
  cancelProductionProgress
} from '@/api/production'
import type { 
  ProductionOrder, 
  MaterialRequirement,
  ProductionProgress 
} from '@/types/production'

const route = useRoute()
const router = useRouter()
const orderId = Number(route.params.id)

// 订单详情
const order = ref<ProductionOrder>({} as ProductionOrder)
const loading = ref(true)
const materialRequirements = ref<MaterialRequirement[]>([])
const progressRecords = ref<ProductionProgress[]>([])

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

// 获取订单详情
const fetchOrderDetail = async () => {
  loading.value = true
  try {
    const res = await getProductionOrderDetail(orderId)
    if (res && typeof res === 'object') {
      const data = res.data || res
      order.value = data
      
      // 获取相关数据
      if (data.material_requirements) {
        materialRequirements.value = data.material_requirements
      }
      
      if (data.progress_records) {
        progressRecords.value = data.progress_records
      }
    }
  } catch (error) {
    console.error('获取生产订单详情失败:', error)
    ElMessage.error('获取生产订单详情失败')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑订单
const handleEdit = () => {
  router.push(`/production/order-edit/${orderId}`)
}

// 备料完成
const handleMaterialReady = () => {
  ElMessageBox.confirm(
    `确定要将生产订单 "${order.value.order_number}" 标记为备料完成吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await materialReadyProductionOrder(orderId)
      ElMessage.success('备料完成标记成功')
      fetchOrderDetail()
    } catch (error: any) {
      console.error('备料完成操作失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`备料完成操作失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('备料完成操作失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 开始生产
const handleStartProduction = () => {
  ElMessageBox.confirm(
    `确定要开始生产订单 "${order.value.order_number}" 吗？开始后将扣减相应材料库存`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await startProductionOrder(orderId)
      ElMessage.success('开始生产成功')
      fetchOrderDetail()
    } catch (error: any) {
      console.error('开始生产失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`开始生产失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('开始生产失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 记录进度
const handleRecordProgress = () => {
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
    await recordProductionProgress(orderId, progressForm)
    ElMessage.success('进度记录成功')
    progressDialogVisible.value = false
    fetchOrderDetail()
  } catch (error: any) {
    console.error('进度记录失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(`进度记录失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('进度记录失败，请稍后重试')
    }
  }
}

// 撤销进度记录
const handleCancelProgress = (row: ProductionProgress) => {
  ElMessageBox.confirm(
    '确定要撤销此进度记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelProductionProgress(orderId, row.id)
      ElMessage.success('撤销进度记录成功')
      fetchOrderDetail()
    } catch (error: any) {
      console.error('撤销进度记录失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`撤销进度记录失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('撤销进度记录失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 完成生产
const handleCompleteProduction = () => {
  completeForm.actual_quantity = order.value.completed_quantity > 0 ? order.value.completed_quantity : order.value.planned_quantity
  completeDialogVisible.value = true
}

// 提交完成生产
const submitCompleteProduction = async () => {
  if (completeForm.actual_quantity <= 0) {
    ElMessage.warning('请输入有效的完成数量')
    return
  }

  try {
    await completeProductionOrder(orderId, completeForm)
    ElMessage.success('完成生产成功')
    completeDialogVisible.value = false
    fetchOrderDetail()
  } catch (error: any) {
    console.error('完成生产失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(`完成生产失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('完成生产失败，请稍后重试')
    }
  }
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

onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.production-order-detail-container {
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

.title-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-header h2 {
  color: #000;
  font-weight: 600;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 100px;
}

.detail-card,
.items-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  color: #000;
  font-weight: 600;
}

.el-tag {
  font-weight: bold;
  padding: 6px 12px;
}

:deep(.el-descriptions) {
  color: #000;
}

:deep(.el-descriptions__label) {
  color: #000 !important;
  font-weight: 500;
}

:deep(.el-descriptions__content) {
  color: #000 !important;
}

:deep(.el-table) {
  color: #000 !important;
}

:deep(.el-table th) {
  color: #000 !important;
  font-weight: bold;
}

:deep(.el-table td) {
  color: #000 !important;
}
</style> 