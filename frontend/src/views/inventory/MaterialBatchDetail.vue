<template>
  <div class="material-batch-detail-container">
    <div class="page-header">
      <h2>材料批次详情</h2>
      <div class="header-actions">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <el-button 
          v-if="batchDetail.status === 'normal'"
          type="primary" 
          @click="handleEdit"
        >
          <el-icon><Edit /></el-icon>编辑
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="info-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h3>基本信息</h3>
          <el-tag :type="getStatusType(batchDetail.status)">
            {{ getStatusLabel(batchDetail.status) }}
          </el-tag>
        </div>
      </template>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="info-item">
            <label>批次号:</label>
            <span>{{ batchDetail.batch_number }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>材料名称:</label>
            <span>{{ batchDetail.material_name }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>材料编码:</label>
            <span>{{ batchDetail.material_detail?.code }}</span>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="info-item">
            <label>初始数量:</label>
            <span>{{ batchDetail.initial_quantity }} {{ batchDetail.material_detail?.unit }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>剩余数量:</label>
            <span class="quantity-value">{{ batchDetail.remaining_quantity }} {{ batchDetail.material_detail?.unit }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>使用进度:</label>
            <el-progress 
              :percentage="calculateProgress()" 
              :color="getProgressColor()"
              :show-text="false"
              style="margin-top: 8px;"
            />
            <span class="progress-text">
              已使用 {{ (batchDetail.initial_quantity - batchDetail.remaining_quantity).toFixed(2) }} / {{ batchDetail.initial_quantity }}
            </span>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="info-item">
            <label>生产日期:</label>
            <span>{{ batchDetail.production_date }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>有效期:</label>
            <span :class="{ 'expired': isExpired() }">
              {{ batchDetail.expiry_date || '无限期' }}
            </span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>创建时间:</label>
            <span>{{ formatDateTime(batchDetail.created_at) }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 采购信息 -->
    <el-card class="info-card" v-if="batchDetail.purchase_detail">
      <template #header>
        <h3>采购信息</h3>
      </template>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="info-item">
            <label>采购单号:</label>
            <span>{{ batchDetail.purchase_detail.purchase_number }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>供应商:</label>
            <span>{{ batchDetail.purchase_detail.supplier_name }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>采购日期:</label>
            <span>{{ batchDetail.purchase_detail.purchase_date }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 库存变动记录 -->
    <el-card class="info-card">
      <template #header>
        <h3>库存变动记录</h3>
      </template>
      
      <el-table 
        :data="batchDetail.movements || []" 
        border 
        empty-text="暂无变动记录"
      >
        <el-table-column prop="movement_date" label="变动时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.movement_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="movement_type" label="变动类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.movement_type === 'in' ? 'success' : 'warning'">
              {{ scope.row.movement_type === 'in' ? '入库' : '出库' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="变动数量" width="120" align="right" />
        <el-table-column prop="reference_number" label="关联单号" width="150" />
        <el-table-column prop="notes" label="备注" min-width="200" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import { getMaterialBatchDetail } from '@/api/inventory'
import type { MaterialBatchDetail } from '@/types/batch'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const batchDetail = ref<MaterialBatchDetail>({
  id: 0,
  batch_number: '',
  material: 0,
  material_name: '',
  purchase: 0,
  production_date: '',
  expiry_date: null,
  initial_quantity: 0,
  remaining_quantity: 0,
  status: 'normal',
  created_at: '',
  material_detail: {
    id: 0,
    name: '',
    code: '',
    specification: '',
    unit: ''
  },
  purchase_detail: {
    id: 0,
    purchase_number: '',
    supplier_name: '',
    purchase_date: ''
  },
  movements: []
})

// 生命周期
onMounted(() => {
  const batchId = route.params.id as string
  if (batchId) {
    fetchBatchDetail(Number(batchId))
  }
})

// 获取批次详情
const fetchBatchDetail = async (id: number) => {
  loading.value = true
  try {
    const response = await getMaterialBatchDetail(id)
    batchDetail.value = response.data
  } catch (error) {
    console.error('获取批次详情失败:', error)
    ElMessage.error('获取批次详情失败')
  } finally {
    loading.value = false
  }
}

// 计算进度百分比
const calculateProgress = () => {
  if (batchDetail.value.initial_quantity <= 0) return 0
  const used = batchDetail.value.initial_quantity - batchDetail.value.remaining_quantity
  return Math.round((used / batchDetail.value.initial_quantity) * 100)
}

// 获取进度条颜色
const getProgressColor = () => {
  const percentage = (batchDetail.value.remaining_quantity / batchDetail.value.initial_quantity) * 100
  if (percentage <= 20) return '#f56c6c' // 红色
  if (percentage <= 50) return '#e6a23c' // 橙色
  return '#67c23a' // 绿色
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'normal': 'success',
    'expired': 'danger',
    'depleted': 'info'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'normal': '正常',
    'expired': '已过期',
    'depleted': '已耗尽'
  }
  return map[status] || '未知'
}

// 判断是否过期
const isExpired = () => {
  if (!batchDetail.value.expiry_date) return false
  return new Date(batchDetail.value.expiry_date) < new Date()
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 编辑批次
const handleEdit = () => {
  ElMessage.info('编辑功能待开发')
}
</script>

<style scoped>
.material-batch-detail-container {
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
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #000;
  font-weight: 600;
}

.info-item {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.info-item label {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
  font-weight: 500;
}

.info-item span {
  color: #000;
  font-size: 16px;
}

.quantity-value {
  font-weight: 600;
  color: #409eff;
}

.progress-text {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.expired {
  color: #f56c6c;
  font-weight: 600;
}

:deep(.el-card__header) {
  background-color: #fafbfc;
  border-bottom: 1px solid #ebeef5;
  padding: 18px 20px;
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

:deep(.el-button) {
  color: #000;
  font-weight: normal;
}

:deep(.el-tag) {
  font-weight: bold;
}

:deep(.el-progress-bar__outer) {
  height: 10px;
}
</style> 