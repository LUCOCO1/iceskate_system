<template>
  <div class="inventory-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>库存详情</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdjust">
          <el-icon><Edit /></el-icon>调整库存
        </el-button>
        <el-button type="success" @click="handleTransfer">
          <el-icon><Right /></el-icon>库存调拨
        </el-button>
        <el-button type="info" @click="handlePrint">
          <el-icon><Printer /></el-icon>打印
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStockStatusType(inventory)">
            {{ getStockStatusLabel(inventory) }}
          </el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="物料类型">
          {{ inventory.inventory_type === 'material' ? '材料' : '产品' }}
        </el-descriptions-item>
        <el-descriptions-item label="名称">
          {{ inventory.inventory_type === 'material' ? inventory.material_name : inventory.product_name }}
        </el-descriptions-item>
        <el-descriptions-item label="编码">
          {{ inventory.inventory_type === 'material' ? inventory.material_code : inventory.product_code }}
        </el-descriptions-item>
        <el-descriptions-item label="规格">{{ inventory.specification }}</el-descriptions-item>
        <el-descriptions-item label="库存数量">{{ inventory.quantity }} {{ inventory.unit }}</el-descriptions-item>
        <el-descriptions-item label="库位">{{ inventory.location }}</el-descriptions-item>
        <el-descriptions-item label="最小库存">{{ inventory.min_stock || '无' }} {{ inventory.min_stock ? inventory.unit : '' }}</el-descriptions-item>
        <el-descriptions-item label="最大库存">{{ inventory.max_stock || '无' }} {{ inventory.max_stock ? inventory.unit : '' }}</el-descriptions-item>
        <el-descriptions-item label="最后更新时间">{{ inventory.last_update_time }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ inventory.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 库存变动历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>库存变动历史</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 260px"
              @change="handleDateRangeChange"
            />
          </div>
        </div>
      </template>
      <el-table :data="movementHistory" border style="width: 100%" v-loading="historyLoading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="movement_date" label="日期" width="120" />
        <el-table-column label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getMovementTypeTag(scope.row.movement_type)">
              {{ getMovementTypeLabel(scope.row.movement_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数量变化" width="120">
          <template #default="scope">
            <span :class="getQuantityChangeClass(scope.row)">
              {{ getQuantityChangeText(scope.row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="变动后数量" width="120">
          <template #default="scope">
            {{ scope.row.after_quantity || '未知' }} {{ inventory.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="reference_number" label="关联单号" width="150" />
        <el-table-column prop="location" label="库位" width="120" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="notes" label="备注" min-width="150" />
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Right, Printer } from '@element-plus/icons-vue'
import { getInventoryDetail, getInventoryMovementHistory } from '@/api/inventory'
import type { InventoryDetail, InventoryMovement } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const inventoryId = Number(route.params.id)
const inventoryType = route.path.includes('material') ? 'material' : 'product'

// 库存详情
const inventory = ref<InventoryDetail>({
  id: 0,
  inventory_type: inventoryType,
  material_id: 0,
  material_name: '',
  material_code: '',
  product_id: 0,
  product_name: '',
  product_code: '',
  specification: '',
  quantity: 0,
  unit: '',
  location: '',
  min_stock: 0,
  max_stock: 0,
  last_update_time: '',
  notes: ''
})
const loading = ref(true)

// 库存变动历史
const movementHistory = ref<InventoryMovement[]>([])
const historyLoading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dateRange = ref<[string, string] | null>(null)

// 获取库存详情
const fetchInventoryDetail = async () => {
  loading.value = true
  try {
    const res = await getInventoryDetail(inventoryId, inventoryType)
    if (res && typeof res === 'object') {
      inventory.value = res.data || res
    }
  } catch (error) {
    console.error('获取库存详情失败:', error)
    ElMessage.error('获取库存详情失败')
  } finally {
    loading.value = false
  }
}

// 获取库存变动历史
const fetchMovementHistory = async () => {
  historyLoading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      inventory_id: inventoryId,
      inventory_type: inventoryType,
      start_date: dateRange.value ? dateRange.value[0] : undefined,
      end_date: dateRange.value ? dateRange.value[1] : undefined
    }
    
    const res = await getInventoryMovementHistory(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        movementHistory.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取库存变动历史失败:', error)
    ElMessage.error('获取库存变动历史失败')
  } finally {
    historyLoading.value = false
  }
}

// 日期范围变化
const handleDateRangeChange = () => {
  currentPage.value = 1
  fetchMovementHistory()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchMovementHistory()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchMovementHistory()
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 调整库存
const handleAdjust = () => {
  ElMessage.info('库存调整功能待实现')
}

// 库存调拨
const handleTransfer = () => {
  ElMessage.info('库存调拨功能待实现')
}

// 打印
const handlePrint = () => {
  ElMessage.info('打印功能待实现')
}

// 获取库存状态标签类型
const getStockStatusType = (row: InventoryDetail) => {
  if (row.quantity <= (row.min_stock || 0)) {
    return 'danger'
  } else if (row.quantity >= (row.max_stock || Infinity)) {
    return 'warning'
  }
  return 'success'
}

// 获取库存状态标签文本
const getStockStatusLabel = (row: InventoryDetail) => {
  if (row.quantity <= (row.min_stock || 0)) {
    return '低库存'
  } else if (row.quantity >= (row.max_stock || Infinity)) {
    return '超库存'
  }
  return '正常'
}

// 获取移动类型标签样式
const getMovementTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'in': 'success',
    'out': 'danger',
    'transfer': 'warning',
    'adjust': 'info'
  }
  return map[type] || 'info'
}

// 获取移动类型标签文本
const getMovementTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    'in': '入库',
    'out': '出库',
    'transfer': '调拨',
    'adjust': '调整'
  }
  return map[type] || '未知'
}

// 获取数量变化样式
const getQuantityChangeClass = (row: InventoryMovement) => {
  const change = row.quantity_change || 0
  return {
    'quantity-increase': change > 0,
    'quantity-decrease': change < 0,
    'quantity-unchanged': change === 0
  }
}

// 获取数量变化文本
const getQuantityChangeText = (row: InventoryMovement) => {
  const change = row.quantity_change || 0
  if (change > 0) {
    return `+${change} ${inventory.value.unit}`
  } else if (change < 0) {
    return `${change} ${inventory.value.unit}`
  }
  return `${change} ${inventory.value.unit}`
}

onMounted(() => {
  fetchInventoryDetail()
  fetchMovementHistory()
})
</script>

<style scoped>
.inventory-detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.detail-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.quantity-increase {
  color: #67c23a;
  font-weight: bold;
}

.quantity-decrease {
  color: #f56c6c;
  font-weight: bold;
}

.quantity-unchanged {
  color: #909399;
}
</style> 