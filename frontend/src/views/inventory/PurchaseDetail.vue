<template>
  <div class="purchase-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>采购单详情</h2>
      </div>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleEdit"
          v-if="['draft', 'pending'].includes(purchase.status)"
          :icon="Edit"
        >
          编辑
        </el-button>
        <el-button 
          type="success" 
          @click="handleReceive"
          v-if="purchase.status === 'pending'"
          :icon="Check"
        >
          确认入库
        </el-button>
        <el-button 
          type="warning" 
          @click="handleCancelReceive"
          v-if="purchase.status === 'received'"
          :icon="Back"
        >
          撤销入库
        </el-button>
        <el-button 
          type="danger" 
          @click="handleCancel"
          v-if="['draft', 'pending'].includes(purchase.status)"
          :icon="Close"
        >
          取消
        </el-button>
        <el-button 
          type="info" 
          @click="handlePrint"
          :icon="Printer"
        >
          打印
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStatusType(purchase.status)">
            {{ getStatusLabel(purchase.status) }}
          </el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="采购单号">{{ purchase.purchase_number }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ purchase.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="采购日期">{{ purchase.purchase_date }}</el-descriptions-item>
        <el-descriptions-item label="交货日期">{{ purchase.delivery_date || '无' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ purchase.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ purchase.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ purchase.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 采购明细 -->
    <el-card class="items-card">
      <template #header>
        <div class="card-header">
          <span>采购明细</span>
        </div>
      </template>
      <el-table :data="purchase.items || []" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column prop="material_specification" label="材料规格" min-width="150" />
        <el-table-column prop="specification" label="规格尺寸" min-width="120" />
        <el-table-column prop="control_number" label="管制编号" width="120" />
        <el-table-column prop="material_type" label="采料方式" width="120" />
        <el-table-column label="数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column label="已入库数量" width="120">
          <template #default="scope">
            {{ scope.row.received_quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
      </el-table>
    </el-card>

    <!-- 入库记录 -->
    <el-card class="movement-card" v-if="movementList.length > 0">
      <template #header>
        <div class="card-header">
          <span>入库记录</span>
        </div>
      </template>
      <el-table :data="movementList" border style="width: 100%">
        <el-table-column prop="movement_date" label="入库时间" width="180" />
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column label="数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="库位" width="120" />
        <el-table-column prop="notes" label="备注" min-width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Check, Close, Printer, Back } from '@element-plus/icons-vue'
import { 
  getPurchaseDetail, 
  getMaterialMovementList, 
  confirmPurchase, 
  cancelPurchaseReceive 
} from '@/api/inventory'
import type { MaterialPurchase, MaterialMovement } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const purchaseId = Number(route.params.id)

// 采购单详情
const purchase = ref<MaterialPurchase>({} as MaterialPurchase)
const loading = ref(true)

// 入库记录
const movementList = ref<MaterialMovement[]>([])
const movementLoading = ref(false)

// 获取采购单详情
const fetchPurchaseDetail = async () => {
  loading.value = true
  try {
    const res = await getPurchaseDetail(purchaseId)
    if (res && typeof res === 'object') {
      purchase.value = res.data || res
    }
  } catch (error) {
    console.error('获取采购单详情失败:', error)
    ElMessage.error('获取采购单详情失败')
  } finally {
    loading.value = false
  }
}

// 获取入库记录
const fetchMovements = async () => {
  movementLoading.value = true
  try {
    const res = await getMaterialMovementList({
      purchase: purchaseId,
      movement_type: 'in'
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        movementList.value = data.results
      }
    }
  } catch (error) {
    console.error('获取入库记录失败:', error)
  } finally {
    movementLoading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑采购单
const handleEdit = () => {
  router.push(`/inventory/purchase-edit/${purchaseId}`)
}

// 入库操作
const handleReceive = () => {
  ElMessageBox.confirm(
    `确定要将采购单 "${purchase.value.purchase_number}" 确认入库吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await confirmPurchase(purchaseId)
      ElMessage.success('确认入库成功')
      fetchPurchaseDetail()
      fetchMovements()
    } catch (error: any) {
      console.error('确认入库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`确认入库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('确认入库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 撤销入库操作
const handleCancelReceive = () => {
  ElMessageBox.confirm(
    `确定要撤销采购单 "${purchase.value.purchase_number}" 的入库状态吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelPurchaseReceive(purchaseId)
      ElMessage.success('撤销入库成功')
      fetchPurchaseDetail()
      fetchMovements()
    } catch (error: any) {
      console.error('撤销入库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`撤销入库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('撤销入库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 取消采购单
const handleCancel = () => {
  ElMessageBox.confirm(
    `确定要取消采购单 "${purchase.value.purchase_number}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.info('取消功能待实现')
  }).catch(() => {})
}

// 打印采购单
const handlePrint = () => {
  window.open(`/api/inventory/purchase/${purchaseId}/print/`, '_blank')
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'draft': 'info',
    'pending': 'warning',
    'received': 'success',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'draft': '草稿',
    'pending': '待入库',
    'received': '已入库',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return map[status] || '未知'
}

onMounted(() => {
  fetchPurchaseDetail()
  fetchMovements()
})
</script>

<style scoped>
.purchase-detail-container {
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

.title-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 100px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-weight: normal;
}

/* 移除之前的样式，重新设置 */
.action-buttons .el-button--primary,
.action-buttons .el-button--success,
.action-buttons .el-button--warning,
.action-buttons .el-button--danger,
.action-buttons .el-button--info {
  /* 保持原有背景色，但文字改为黑色 */
  color: #000 !important;
}

.action-buttons .el-button span,
.action-buttons .el-button i {
  color: #000;
}

.detail-card,
.items-card,
.movement-card {
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

/* 深色选择器确保样式覆盖组件内部 */
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