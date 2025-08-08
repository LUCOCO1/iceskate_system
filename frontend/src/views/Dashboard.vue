<template>
  <div class="dashboard-container">
    <!-- 材料库存 -->
    <div class="section-wrapper">
      <div class="section-card">
        <div class="card-header">
          <h2 class="card-title">
            <div class="title-icon-wrapper materials-icon">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-4"/>
                <path d="M9 11V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>
              </svg>
            </div>
            <div>
              <div class="title-text">材料库存</div>
              <div class="title-subtitle">{{ materials.length }} 种材料</div>
            </div>
          </h2>
          <button class="view-all-btn" @click="goToMaterials">
            查看全部
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
        <div class="section-content">
          <div v-if="materialsLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="materials.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>暂无材料数据</span>
          </div>
          <div v-else class="items-grid">
            <div v-for="material in materials.slice(0, 10)" :key="material.id" class="item-card">
              <div class="item-info">
                <div class="item-name">{{ material.name }}</div>
                <div class="item-detail">{{ material.specification || '无规格' }}</div>
              </div>
              <div class="item-value" :class="{ 'low-stock': (material.current_stock || 0) < 10 }">
                {{ material.current_stock || 0 }}
                <span class="unit">{{ material.unit || '件' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 生产订单 -->
    <div class="section-wrapper">
      <div class="section-card">
        <div class="card-header">
          <h2 class="card-title">
            <div class="title-icon-wrapper production-icon">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </div>
            <div>
              <div class="title-text">生产订单</div>
              <div class="title-subtitle">{{ productionOrders.length }} 个订单</div>
            </div>
          </h2>
          <button class="view-all-btn" @click="goToProductionOrders">
            查看全部
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
        <div class="section-content">
          <div v-if="productionOrdersLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="productionOrders.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>暂无生产订单</span>
          </div>
          <div v-else class="items-grid">
            <div v-for="order in productionOrders.slice(0, 10)" :key="order.id" class="item-card">
              <div class="item-info">
                <div class="item-name">{{ order.order_number }}</div>
                <div class="item-detail">{{ order.product_name || '未指定产品' }}</div>
              </div>
              <div class="status-badge" :class="`status-${order.status || 'pending'}`">
                {{ getStatusText(order.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 销售订单 -->
    <div class="section-wrapper">
      <div class="section-card">
        <div class="card-header">
          <h2 class="card-title">
            <div class="title-icon-wrapper orders-icon">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="9" cy="21" r="1"/>
                <circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
              </svg>
            </div>
            <div>
              <div class="title-text">销售订单</div>
              <div class="title-subtitle">{{ orders.length }} 个订单</div>
            </div>
          </h2>
          <button class="view-all-btn" @click="goToOrders">
            查看全部
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
        <div class="section-content">
          <div v-if="ordersLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="orders.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>暂无销售订单</span>
          </div>
          <div v-else class="items-grid">
            <div v-for="order in orders.slice(0, 10)" :key="order.id" class="item-card">
              <div class="item-info">
                <div class="item-name">{{ order.order_number }}</div>
                <div class="item-detail">{{ order.customer_name || '未知客户' }}</div>
              </div>
              <div class="item-amount">
                ¥{{ (order.total_amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMaterialList } from '@/api/inventory'
import { getProductionOrderList } from '@/api/production'
import { getOrderList } from '@/api/orders'

const router = useRouter()

// 材料库存数据
const materials = ref([])
const materialsLoading = ref(false)

// 生产订单数据
const productionOrders = ref([])
const productionOrdersLoading = ref(false)

// 销售订单数据
const orders = ref([])
const ordersLoading = ref(false)

// 模拟数据
const mockMaterials = [
  { id: 1, name: '钢板A320', specification: '厚度10mm', current_stock: 120, unit: '张' },
  { id: 2, name: '不锈钢管', specification: 'φ25×2.5', current_stock: 85, unit: '根' },
  { id: 3, name: '轴承6204', specification: '内径20mm', current_stock: 8, unit: '个' },
  { id: 4, name: '螺栓M8', specification: '长度30mm', current_stock: 450, unit: '个' },
  { id: 5, name: '铝合金板', specification: '3mm厚度', current_stock: 65, unit: '张' },
  { id: 6, name: '橡胶垫片', specification: 'φ50×5', current_stock: 200, unit: '个' },
  { id: 7, name: '电机线缆', specification: '2.5mm²', current_stock: 5, unit: '米' },
  { id: 8, name: '焊条E4303', specification: 'φ3.2', current_stock: 25, unit: '公斤' },
  { id: 9, name: '液压油', specification: '46号', current_stock: 180, unit: '升' },
  { id: 10, name: '密封圈', specification: 'φ30×2', current_stock: 95, unit: '个' }
]

const mockProductionOrders = [
  { id: 1, order_number: 'PO202501001', product_name: '精密轴承座', status: 'in_progress' },
  { id: 2, order_number: 'PO202501002', product_name: '液压缸体', status: 'pending' },
  { id: 3, order_number: 'PO202501003', product_name: '传动齿轮', status: 'completed' },
  { id: 4, order_number: 'PO202501004', product_name: '支撑架组件', status: 'in_progress' },
  { id: 5, order_number: 'PO202501005', product_name: '密封装置', status: 'pending' },
  { id: 6, order_number: 'PO202501006', product_name: '控制阀', status: 'in_progress' },
  { id: 7, order_number: 'PO202501007', product_name: '连接法兰', status: 'completed' },
  { id: 8, order_number: 'PO202501008', product_name: '减速器外壳', status: 'pending' },
  { id: 9, order_number: 'PO202501009', product_name: '导向套', status: 'in_progress' },
  { id: 10, order_number: 'PO202501010', product_name: '调节螺杆', status: 'cancelled' }
]

const mockOrders = [
  { id: 1, order_number: 'SO202501001', customer_name: '华东机械有限公司', total_amount: 45800.00 },
  { id: 2, order_number: 'SO202501002', customer_name: '精工制造集团', total_amount: 128500.50 },
  { id: 3, order_number: 'SO202501003', customer_name: '远大工业设备', total_amount: 67200.00 },
  { id: 4, order_number: 'SO202501004', customer_name: '中科自动化', total_amount: 89300.75 },
  { id: 5, order_number: 'SO202501005', customer_name: '泰合重工', total_amount: 156000.00 },
  { id: 6, order_number: 'SO202501006', customer_name: '鼎盛机械', total_amount: 73400.25 },
  { id: 7, order_number: 'SO202501007', customer_name: '恒力设备制造', total_amount: 94600.00 },
  { id: 8, order_number: 'SO202501008', customer_name: '凯旋工业', total_amount: 112800.80 },
  { id: 9, order_number: 'SO202501009', customer_name: '盛达机电', total_amount: 58900.00 },
  { id: 10, order_number: 'SO202501010', customer_name: '万华科技', total_amount: 203500.00 }
]

// 加载材料库存数据
const loadMaterials = async () => {
  materialsLoading.value = true
  try {
    const response = await getMaterialList()
    materials.value = response && response.length > 0 ? response : mockMaterials
  } catch (error) {
    console.error('加载材料数据失败:', error)
    materials.value = mockMaterials
  } finally {
    materialsLoading.value = false
  }
}

// 加载生产订单数据
const loadProductionOrders = async () => {
  productionOrdersLoading.value = true
  try {
    const response = await getProductionOrderList()
    productionOrders.value = response && response.length > 0 ? response : mockProductionOrders
  } catch (error) {
    console.error('加载生产订单数据失败:', error)
    productionOrders.value = mockProductionOrders
  } finally {
    productionOrdersLoading.value = false
  }
}

// 加载销售订单数据
const loadOrders = async () => {
  ordersLoading.value = true
  try {
    const response = await getOrderList()
    orders.value = response && response.length > 0 ? response : mockOrders
  } catch (error) {
    console.error('加载销售订单数据失败:', error)
    orders.value = mockOrders
  } finally {
    ordersLoading.value = false
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 导航到材料管理页面
const goToMaterials = () => {
  router.push('/inventory/materials')
}

// 导航到生产订单页面
const goToProductionOrders = () => {
  router.push('/production/production-orders')
}

// 导航到销售订单页面
const goToOrders = () => {
  router.push('/orders')
}

// 页面挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadMaterials(),
    loadProductionOrders(),
    loadOrders()
  ])
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #fafaf9;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.section-wrapper {
  margin-bottom: 3rem;
}

.section-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.section-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #f3f4f6;
  background: #fefefe;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.title-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.materials-icon {
  background: linear-gradient(135deg, #ecfccb 0%, #d9f99d 100%);
  color: #365314;
}

.production-icon {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.orders-icon {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #be185d;
}

.title-icon {
  width: 22px;
  height: 22px;
}

.title-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.2;
}

.title-subtitle {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.section-content {
  padding: 0;
  min-height: 200px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #d1d5db;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0;
}

.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.15s ease;
}

.item-card:hover {
  background: #f9fafb;
}

.item-card:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.25;
}

.item-detail {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.25;
}

.item-value {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}

.item-value.low-stock {
  color: #dc2626;
}

.unit {
  font-size: 0.75rem;
  font-weight: 400;
  color: #6b7280;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.item-amount {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
  font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .section-wrapper {
    margin-bottom: 2rem;
  }
  
  .card-header {
    padding: 1rem 1.5rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .items-grid {
    grid-template-columns: 1fr;
  }
  
  .item-card {
    padding: 0.75rem 1.5rem;
  }
  
  .card-title {
    font-size: 1.125rem;
  }
}

@media (max-width: 640px) {
  .dashboard-container {
    padding: 0.75rem;
  }
  
  .card-header {
    padding: 0.75rem 1rem;
  }
  
  .item-card {
    padding: 0.75rem 1rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .item-value,
  .status-badge,
  .item-amount {
    align-self: flex-end;
  }
}
</style> 