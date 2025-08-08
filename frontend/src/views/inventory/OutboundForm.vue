<template>
  <div class="outbound-form-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>{{ isEdit ? '编辑出库单' : '新增出库单' }}</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          <el-icon><Check /></el-icon>保存
        </el-button>
        <el-button @click="goBack">
          <el-icon><Close /></el-icon>取消
        </el-button>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="outboundForm"
      :rules="rules"
      label-width="120px"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出库单号" prop="outbound_number">
              <el-input 
                v-model="outboundForm.outbound_number" 
                placeholder="系统自动生成"
                disabled
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联订单" prop="order">
              <el-select
                v-model="outboundForm.order"
                placeholder="选择关联订单"
                clearable
                filterable
                style="width: 100%"
                @change="handleOrderChange"
              >
                <el-option
                  v-for="item in orderOptions"
                  :key="item.id"
                  :label="`${item.order_number} - ${item.customer_name || '未知客户'}`"
                  :value="item.id"
                >
                  <span style="float: left">{{ item.order_number }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px">
                    {{ item.customer_name || '未知客户' }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出库日期" prop="outbound_date">
              <el-date-picker
                v-model="outboundForm.outbound_date"
                type="date"
                placeholder="选择出库日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="outboundForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-card>

      <!-- 出库明细 -->
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>出库明细</span>
            <div>
              <el-button 
                v-if="outboundForm.order" 
                type="success" 
                @click="handleLoadOrderItems" 
                plain
                :loading="loadingOrderItems"
              >
                <el-icon><Download /></el-icon>从订单加载明细
              </el-button>
              <el-button type="primary" @click="handleAddItem" plain>
                <el-icon><Plus /></el-icon>添加产品
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="outboundForm.items" border style="width: 100%">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column label="产品名称" min-width="150">
            <template #default="scope">
              <el-select
                v-model="scope.row.product"
                placeholder="选择产品"
                filterable
                clearable
                style="width: 100%"
                @change="(val: number) => handleProductChange(val, scope.$index)"
              >
                <el-option
                  v-for="item in productOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="150">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="单位" width="100">
            <template #default="scope">
              <el-input v-model="scope.row.unit" placeholder="单位" />
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150">
            <template #default="scope">
              <el-input v-model="scope.row.notes" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="scope">
              <el-button
                type="danger"
                @click="handleRemoveItem(scope.$index)"
                circle
                plain
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="empty-data" v-if="!outboundForm.items || outboundForm.items.length === 0">
          <el-empty description="暂无出库明细，请添加产品" />
        </div>
      </el-card>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { ArrowLeft, Check, Close, Plus, Delete, Download } from '@element-plus/icons-vue'
import { getProductList, getOutboundDetail, createOutbound, updateOutbound } from '@/api/inventory'
import { getOrderList, getOrderDetail } from '@/api/orders'
import type { ProductOutbound, ProductOutboundItem, Product } from '@/types/inventory'

// 订单类型定义
interface Order {
  id: number
  order_number: string
  customer: number
  customer_name?: string
  status: string
  items?: OrderItem[]
}

// 订单明细类型定义
interface OrderItem {
  id: number
  order: number
  product: number
  product_name?: string
  color?: string
  material?: string
  quantity: number
  unit: string
  notes?: string
}

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)
const outboundId = computed(() => Number(route.params.id) || 0)

// 表单数据
const outboundForm = reactive<ProductOutbound>({
  id: 0,
  outbound_number: '',
  outbound_date: new Date().toISOString().split('T')[0],
  order: undefined,
  status: 'draft',
  notes: '',
  items: [],
  created_at: ''
})

// 表单验证规则
const rules = {
  outbound_date: [{ required: true, message: '请选择出库日期', trigger: 'change' }]
}

// 加载状态
const loading = ref(false)
const submitting = ref(false)
const loadingOrderItems = ref(false)

// 选项数据
const productOptions = ref<Product[]>([])
const orderOptions = ref<Order[]>([])

// 获取产品列表
const fetchProducts = async () => {
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
  }
}

// 获取订单列表
const fetchOrders = async () => {
  try {
    const res = await getOrderList({ page_size: 1000, status: ['pending', 'processing', 'completed'] })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        orderOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取订单列表失败:', error)
  }
}

// 获取出库单详情
const fetchOutboundDetail = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const res = await getOutboundDetail(outboundId.value)
    if (res && typeof res === 'object') {
      const data = res.data || res
      Object.assign(outboundForm, data)
    }
  } catch (error) {
    console.error('获取出库单详情失败:', error)
    ElMessage.error('获取出库单详情失败')
  } finally {
    loading.value = false
  }
}

// 订单选择变更
const handleOrderChange = async (orderId: number | null) => {
  if (!orderId) {
    // 清空订单选择时，清空出库明细
    outboundForm.items = []
    return
  }
  
  // 仅显示提示，不自动加载明细
  ElMessage.info('已选择订单，可点击"从订单加载明细"按钮或手动添加产品')
}

// 从订单加载明细
const handleLoadOrderItems = async () => {
  if (!outboundForm.order) return
  
  try {
    loadingOrderItems.value = true
    const res = await getOrderDetail(outboundForm.order)
    if (res && typeof res === 'object') {
      const orderData = res.data || res
      if (orderData.items && Array.isArray(orderData.items)) {
        // 根据订单明细自动填充出库明细
        outboundForm.items = orderData.items.map((orderItem: OrderItem) => {
          return {
            id: 0,
            outbound: outboundId.value,
            product: orderItem.product,
            product_name: orderItem.product_name,
            quantity: orderItem.quantity,
            unit: orderItem.unit,
            notes: `订单明细：${[orderItem.color, orderItem.material, orderItem.notes].filter(Boolean).join(' ')}`.replace('订单明细：', orderItem.color || orderItem.material || orderItem.notes ? '订单明细：' : '')
          }
        })
        
        ElMessage.success(`已自动填充 ${orderData.items.length} 个产品明细`)
      }
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    ElMessage.error('获取订单详情失败')
  } finally {
    loadingOrderItems.value = false
  }
}

// 产品选择变更
const handleProductChange = (productId: number, index: number) => {
  if (!productId) return
  
  const product = productOptions.value.find(item => item.id === productId)
  if (product && outboundForm.items) {
    outboundForm.items[index].product_name = product.name
    outboundForm.items[index].unit = product.unit || '个'
  }
}

// 添加出库明细项
const handleAddItem = () => {
  const newItem: ProductOutboundItem = {
    id: 0,
    outbound: outboundId.value,
    product: null as any, // 设置为null，强制用户选择
    product_name: '',
    quantity: 1,
    unit: '个',
    notes: ''
  }
  
  if (!outboundForm.items) {
    outboundForm.items = [];
  }
  
  outboundForm.items.push(newItem)
}

// 移除出库明细项
const handleRemoveItem = (index: number) => {
  if (outboundForm.items) {
    outboundForm.items.splice(index, 1)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请检查表单填写是否正确')
      return
    }
    
    // 简化验证逻辑：必须有明细项
    if (!outboundForm.items || outboundForm.items.length === 0) {
      ElMessage.error('请添加出库明细（可手动添加或从订单加载）')
      return
    }
    
    // 验证明细项
    for (const item of outboundForm.items) {
      if (!item.product || item.product === 0) {
        ElMessage.error('请选择产品')
        return
      }
      if (!item.quantity || item.quantity <= 0) {
        ElMessage.error('请输入有效的数量')
        return
      }
    }
    
    submitting.value = true
    try {
      // 清理数据：将Vue响应式对象转换为纯净的JavaScript对象
      const cleanData = {
        outbound_number: outboundForm.outbound_number,
        outbound_date: outboundForm.outbound_date,
        order: outboundForm.order,
        status: outboundForm.status,
        notes: outboundForm.notes,
        items: outboundForm.items?.map(item => ({
          product: item.product,
          quantity: item.quantity,
          unit: item.unit,
          notes: item.notes || ''
        })) || []
      }
      
      // 添加调试信息
      console.log('原始数据:', outboundForm)
      console.log('清理后的数据:', cleanData)
      
      if (isEdit.value) {
        await updateOutbound(outboundId.value, cleanData)
        ElMessage.success('出库单更新成功')
      } else {
        await createOutbound(cleanData)
        ElMessage.success('出库单创建成功')
      }
      router.push('/inventory/outbounds')
    } catch (error: any) {
      console.error('保存出库单失败:', error)
      console.error('错误详情:', error.response?.data)
      
      let errorMessage = '保存出库单失败'
      
      if (error.response?.data) {
        const errorData = error.response.data
        console.log('详细错误数据:', errorData)
        
        // 处理Django REST Framework的错误格式
        if (typeof errorData === 'object') {
          if (errorData.non_field_errors) {
            // 非字段错误（通常是序列化器级别的验证错误）
            errorMessage = Array.isArray(errorData.non_field_errors) 
              ? errorData.non_field_errors[0] 
              : errorData.non_field_errors
          } else if (errorData.items) {
            // 明细项错误
            if (Array.isArray(errorData.items)) {
              // 如果items是数组，处理第一个错误
              const itemError = errorData.items[0]
              if (typeof itemError === 'object') {
                errorMessage = `明细项错误: ${JSON.stringify(itemError, null, 2)}`
              } else {
                errorMessage = `明细项错误: ${itemError}`
              }
            } else if (typeof errorData.items === 'object') {
              // 如果items是对象，提取错误信息
              const itemErrors = []
              for (const [key, value] of Object.entries(errorData.items)) {
                if (Array.isArray(value)) {
                  itemErrors.push(`${key}: ${value.join(', ')}`)
                } else {
                  itemErrors.push(`${key}: ${value}`)
                }
              }
              errorMessage = `明细项错误: ${itemErrors.join('; ')}`
            } else {
              errorMessage = `明细项错误: ${errorData.items}`
            }
          } else if (errorData.detail) {
            errorMessage = errorData.detail
          } else {
            // 处理字段级错误
            const errorFields = []
            for (const [field, errors] of Object.entries(errorData)) {
              if (Array.isArray(errors)) {
                errorFields.push(`${field}: ${errors.join(', ')}`)
              } else if (typeof errors === 'string') {
                errorFields.push(`${field}: ${errors}`)
              } else if (typeof errors === 'object') {
                errorFields.push(`${field}: ${JSON.stringify(errors)}`)
              }
            }
            
            if (errorFields.length > 0) {
              errorMessage = errorFields.join('; ')
            } else {
              errorMessage = `请求失败: ${JSON.stringify(errorData, null, 2)}`
            }
          }
        } else if (typeof errorData === 'string') {
          errorMessage = errorData
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      ElMessage.error(errorMessage)
    } finally {
      submitting.value = false
    }
  })
}

// 返回上一页
const goBack = () => {
  ElMessageBox.confirm(
    '确定要离开当前页面吗？未保存的数据将会丢失',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    router.back()
  }).catch(() => {})
}

onMounted(() => {
  fetchProducts()
  fetchOrders()
  fetchOutboundDetail()
})
</script>

<style scoped>
.outbound-form-container {
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

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-data {
  margin: 20px 0;
}
</style> 