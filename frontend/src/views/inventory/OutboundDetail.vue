<template>
  <div class="outbound-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>出库单详情</h2>
      </div>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleEdit"
          v-if="outbound.status === 'draft'"
          :icon="Edit"
        >
          编辑
        </el-button>
        <el-button 
          type="success" 
          @click="handleConfirm"
          v-if="outbound.status === 'draft'"
          :icon="Check"
        >
          确认出库
        </el-button>
        <el-button 
          type="warning" 
          @click="handleCancel"
          v-if="outbound.status === 'confirmed'"
          :icon="Close"
        >
          取消出库
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
          <el-tag :type="getStatusType(outbound.status)">
            {{ getStatusLabel(outbound.status) }}
          </el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="出库单号">{{ outbound.outbound_number }}</el-descriptions-item>
        <el-descriptions-item label="关联订单">{{ outbound.order_number || '无' }}</el-descriptions-item>
        <el-descriptions-item label="出库日期">{{ outbound.outbound_date }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(outbound.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ outbound.created_by_name || '系统' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(outbound.status)">
            {{ getStatusLabel(outbound.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ outbound.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 出库明细 -->
    <el-card class="items-card">
      <template #header>
        <div class="card-header">
          <span>出库明细</span>
        </div>
      </template>
      <el-table :data="outbound.items || []" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="product_code" label="产品编码" width="120" />
        <el-table-column label="数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
      </el-table>
      <div class="empty-data" v-if="!outbound.items || outbound.items.length === 0">
        <el-empty description="暂无出库明细" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Check, Close, Printer } from '@element-plus/icons-vue'
import { getOutboundDetail, confirmOutbound, cancelOutbound } from '@/api/inventory'
import type { ProductOutbound } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const outboundId = Number(route.params.id)

// 出库单详情
const outbound = ref<ProductOutbound>({
  id: 0,
  outbound_number: '',
  outbound_date: '',
  status: 'draft',
  created_at: '',
  items: []
})
const loading = ref(true)

// 获取出库单详情
const fetchOutboundDetail = async () => {
  loading.value = true
  try {
    const res = await getOutboundDetail(outboundId)
    if (res && typeof res === 'object') {
      outbound.value = res.data || res
    }
  } catch (error) {
    console.error('获取出库单详情失败:', error)
    ElMessage.error('获取出库单详情失败')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑出库单
const handleEdit = () => {
  router.push(`/inventory/outbound-edit/${outboundId}`)
}

// 确认出库
const handleConfirm = () => {
  ElMessageBox.confirm(
    `确定要确认出库单 "${outbound.value.outbound_number}" 吗？确认后将减少相应产品库存`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await confirmOutbound(outboundId)
      ElMessage.success('确认出库成功')
      fetchOutboundDetail()
    } catch (error: any) {
      console.error('确认出库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`确认出库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('确认出库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 取消出库
const handleCancel = () => {
  ElMessageBox.confirm(
    `确定要取消出库单 "${outbound.value.outbound_number}" 吗？取消后将恢复相应产品库存`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelOutbound(outboundId)
      ElMessage.success('取消出库成功')
      fetchOutboundDetail()
    } catch (error: any) {
      console.error('取消出库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`取消出库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('取消出库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 打印出库单
const handlePrint = () => {
  window.open(`/api/inventory/outbound/${outboundId}/print/`, '_blank')
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

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  fetchOutboundDetail()
})
</script>

<style scoped>
.outbound-detail-container {
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

.action-buttons .el-button--primary,
.action-buttons .el-button--success,
.action-buttons .el-button--warning,
.action-buttons .el-button--danger,
.action-buttons .el-button--info {
  color: #000 !important;
}

.action-buttons .el-button span,
.action-buttons .el-button i {
  color: #000;
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

.empty-data {
  margin: 20px 0;
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