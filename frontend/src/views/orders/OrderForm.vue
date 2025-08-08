<template>
  <div class="order-form-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>{{ isEdit ? '编辑订单' : '创建订单' }}</h2>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="left"
      label-width="120px"
      class="order-form"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-card>
        <template #header>
          <div class="card-header">
            基本信息
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" prop="customer">
              <el-select 
                v-model="form.customer" 
                placeholder="请选择客户" 
                style="width: 100%;"
                filterable
                @change="handleCustomerChange"
              >
                <el-option 
                  v-for="customer in customerOptions" 
                  :key="customer.id"
                  :label="`${customer.name} (${customer.code})`" 
                  :value="customer.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户订单号" prop="customer_order_number">
              <el-input v-model="form.customer_order_number" placeholder="请输入客户订单号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="下单日期" prop="order_date">
              <el-date-picker
                v-model="form.order_date"
                type="date"
                placeholder="选择下单日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交货日期" prop="delivery_date">
              <el-date-picker
                v-model="form.delivery_date"
                type="date"
                placeholder="选择交货日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="isEdit">
          <el-col :span="12">
            <el-form-item label="订单状态" prop="status">
              <el-select 
                v-model="form.status" 
                placeholder="请选择状态" 
                style="width: 100%;"
              >
                <el-option 
                  v-for="option in ORDER_STATUS_OPTIONS" 
                  :key="option.value"
                  :label="option.label" 
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <!-- 空列占位 -->
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（非必填）"
          />
        </el-form-item>
      </el-card>

      <!-- 订单明细 -->
      <el-card class="items-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="header-title">订单明细</span>
              <el-tag v-if="form.items.length > 0" type="info" size="small">
                {{ form.items.length }} 个产品
              </el-tag>
            </div>
            <el-button 
              type="primary" 
              @click="addOrderItem" 
              :icon="Plus"
              size="small"
              :disabled="!form.customer && !isEdit"
            >
              添加产品
            </el-button>
          </div>
        </template>

        <div class="order-items-container">
          <div v-if="form.items.length === 0" class="empty-state">
            <div class="empty-icon">
              <el-icon size="48"><ShoppingCart /></el-icon>
            </div>
            <div class="empty-text">{{ isEdit ? '该订单暂无产品明细' : '还没有添加产品明细' }}</div>
            <div class="empty-subtext">
              {{ isEdit ? '点击上方"添加产品"按钮添加产品' : form.customer ? '点击上方"添加产品"按钮开始添加' : '请先选择客户，然后添加产品明细' }}
            </div>
          </div>

          <transition-group name="order-item" tag="div" class="order-items">
            <div 
              v-for="(item, index) in form.items" 
              :key="index" 
              class="order-item-card"
            >
              <div class="order-item-header">
                <div class="item-number">{{ index + 1 }}</div>
                <div class="item-title">产品明细 {{ index + 1 }}</div>
                <el-button 
                  type="danger" 
                  @click="removeOrderItem(index)"
                  :icon="Delete"
                  size="small"
                  circle
                  plain
                  title="删除此产品明细"
                />
              </div>

              <div class="order-item-content">
                <!-- 第一行：产品名称 -->
                <el-row :gutter="16">
                  <el-col :span="24">
                    <el-form-item 
                      label="产品名称"
                      :prop="`items.${index}.product`"
                      :rules="{ required: true, message: '请选择产品', trigger: 'change' }"
                      class="order-form-item"
                    >
                      <el-select 
                        v-model="item.product" 
                        placeholder="请选择产品" 
                        filterable 
                        clearable
                        style="width: 100%;"
                        @change="(val: number) => handleProductSelect(val, index)"
                      >
                        <el-option 
                          v-for="product in productOptions" 
                          :key="product.id"
                          :label="product.name" 
                          :value="product.id"
                        />
                        <!-- 如果当前选中的产品不在产品选项中（比如不同客户的产品），也要显示 -->
                        <el-option 
                          v-if="item.product && !productOptions.find(p => p.id === item.product)"
                          :key="item.product"
                          :label="item.product_name || `产品ID: ${item.product}`"
                          :value="item.product"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 第二行：颜色、材料 -->
                <el-row :gutter="20" class="details-row">
                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <div class="field-wrapper color-field">
                      <el-form-item 
                        label="颜色"
                        :prop="`items.${index}.color`"
                        class="order-form-item enhanced-field"
                      >
                        <el-select
                          v-model="item.color"
                          placeholder="选择颜色"
                          style="width: 100%;"
                          clearable
                          class="enhanced-select"
                        >
                          <el-option label="本色" value="本色">
                            <div class="color-option">
                              <span class="color-dot natural"></span>
                              本色
                            </div>
                          </el-option>
                          <el-option label="白色" value="白色">
                            <div class="color-option">
                              <span class="color-dot white"></span>
                              白色
                            </div>
                          </el-option>
                          <el-option label="黑色" value="黑色">
                            <div class="color-option">
                              <span class="color-dot black"></span>
                              黑色
                            </div>
                          </el-option>
                          <el-option label="银色" value="银色">
                            <div class="color-option">
                              <span class="color-dot silver"></span>
                              银色
                            </div>
                          </el-option>
                          <el-option label="金色" value="金色">
                            <div class="color-option">
                              <span class="color-dot gold"></span>
                              金色
                            </div>
                          </el-option>
                          <el-option label="其他" value="其他">
                            <div class="color-option">
                              <span class="color-dot other"></span>
                              其他
                            </div>
                          </el-option>
                        </el-select>
                      </el-form-item>
                    </div>
                  </el-col>
                  
                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <div class="field-wrapper material-field">
                      <el-form-item 
                        label="材料"
                        :prop="`items.${index}.material`"
                        class="order-form-item enhanced-field"
                      >
                        <el-select 
                          v-model="item.material" 
                          placeholder="选择材料" 
                          filterable 
                          style="width: 100%;"
                          clearable
                          class="enhanced-select"
                        >
                          <el-option 
                            v-for="material in materialOptions" 
                            :key="material.id"
                            :label="material.name" 
                            :value="material.name"
                          />
                        </el-select>
                      </el-form-item>
                    </div>
                  </el-col>
                </el-row>

                <!-- 第三行：数量、单位 -->
                <el-row :gutter="20" class="details-row">
                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <div class="field-wrapper quantity-field">
                      <el-form-item 
                        label="数量"
                        :prop="`items.${index}.quantity`"
                        :rules="{ required: true, message: '请输入数量', trigger: 'blur' }"
                        class="order-form-item enhanced-field"
                      >
                        <el-input-number 
                          v-model="item.quantity" 
                          :min="1" 
                          :precision="0" 
                          style="width: 100%;"
                          placeholder="数量"
                          controls-position="right"
                          class="enhanced-number"
                        />
                      </el-form-item>
                    </div>
                  </el-col>

                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <div class="field-wrapper unit-field">
                      <el-form-item 
                        label="单位"
                        :prop="`items.${index}.unit`"
                        class="order-form-item enhanced-field"
                      >
                        <el-input 
                          v-model="item.unit" 
                          placeholder="单位" 
                          style="width: 100%;"
                          readonly
                          class="enhanced-input unit-input"
                        />
                      </el-form-item>
                    </div>
                  </el-col>
                </el-row>

                <!-- 第四行：备注说明 -->
                <el-row :gutter="16" style="margin-top: 20px;">
                  <el-col :span="24">
                    <el-form-item 
                      label="备注说明"
                      :prop="`items.${index}.notes`"
                      class="order-form-item"
                    >
                      <el-input 
                        v-model="item.notes" 
                        placeholder="备注信息（可选）" 
                        type="textarea"
                        :rows="2"
                        maxlength="200"
                        show-word-limit
                        style="width: 100%;"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>
          </transition-group>
        </div>
      </el-card>

      <div class="form-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import { ArrowLeft, Plus, Delete, ShoppingCart } from '@element-plus/icons-vue'
import { 
  getOrderDetail, 
  createOrder, 
  updateOrder,
  getCustomerList 
} from '@/api/orders'
import { getProductList, getMaterialList } from '@/api/inventory'
import type { OrderForm, OrderItemForm, Customer } from '@/types/orders'
import type { Product, Material } from '@/types/inventory'
import { ORDER_STATUS_OPTIONS } from '@/types/orders'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 判断是创建还是编辑模式
const isEdit = computed(() => route.params.id !== undefined)
const orderId = computed(() => (isEdit.value ? Number(route.params.id) : null))

// 选项数据
const customerOptions = ref<Customer[]>([])
const productOptions = ref<Product[]>([])
const materialOptions = ref<Material[]>([])

// 表单数据
const form = reactive<OrderForm>({
  customer: null,
  order_date: '',
  delivery_date: '',
  status: 'pending',
  notes: '',
  customer_order_number: '',
  items: []
})

// 表单验证规则
const rules = {
  customer: [
    { required: true, message: '请选择客户', trigger: 'change' }
  ],
  customer_order_number: [
    { required: true, message: '请输入客户订单号', trigger: 'blur' }
  ],
  order_date: [
    { required: true, message: '请选择下单日期', trigger: 'change' }
  ],
  delivery_date: [
    { required: true, message: '请选择交货日期', trigger: 'change' }
  ],
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取客户列表
const fetchCustomers = async () => {
  try {
    const res: any = await getCustomerList({ is_active: true })
    if (res) {
      customerOptions.value = 'results' in res ? res.results : Array.isArray(res) ? res : []
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
    ElMessage.error('获取客户列表失败')
  }
}

// 获取产品列表（可按客户过滤）
const fetchProducts = async (customerId?: number | null) => {
  try {
    const params: any = {}
    if (customerId) params.customer = customerId
    const res: any = await getProductList(params)
    if (res) {
      productOptions.value = 'results' in res ? res.results : Array.isArray(res) ? res : []
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  }
}

// 获取材料列表
const fetchMaterials = async () => {
  try {
    const res: any = await getMaterialList({ is_active: true })
    if (res) {
      materialOptions.value = 'results' in res ? res.results : Array.isArray(res) ? res : []
    }
  } catch (error) {
    console.error('获取材料列表失败:', error)
  }
}

// 获取订单详情（编辑模式）
const fetchOrderDetail = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  isLoadingData.value = true // 标记正在加载数据
  
  try {
    console.log('正在获取订单详情，订单ID:', orderId.value)
    const res = await getOrderDetail(orderId.value as number)
    console.log('订单详情API响应:', res)
    
    if (res) {
      // 处理不同的响应格式
      let data
      if (res.data) {
        data = res.data
      } else {
        data = res
      }
      
      console.log('处理后的订单数据:', data)
      
      if (data && typeof data === 'object') {
        // 填充表单数据
        form.customer = data.customer || null
        form.order_date = data.order_date || ''
        form.delivery_date = data.delivery_date || ''
        form.status = data.status || 'pending'
        form.notes = data.notes || ''
        form.customer_order_number = data.customer_order_number || ''
        
        console.log('表单数据填充完成:', {
          customer: form.customer,
          status: form.status,
          order_date: form.order_date
        })
        
        // 填充订单明细
        if (data.items && Array.isArray(data.items)) {
          form.items = data.items.map((item: any) => ({
            product: item.product || null,
            product_name: item.product_name || '',
            color: item.color || '',
            material: item.material || '',
            quantity: item.quantity || 1,
            unit: item.unit || '',
            notes: item.notes || ''
          }))
          console.log('订单明细填充完成，项目数:', form.items.length)
        } else {
          console.warn('订单明细数据为空或格式错误:', data.items)
          form.items = []
        }
        
        // 数据加载完成后再加载产品列表（避免触发客户变化监听器）
        isLoadingData.value = false
        
        // 如果有客户ID，重新加载对应的产品列表
        if (form.customer) {
          await fetchProducts(form.customer)
        }
      } else {
        console.error('订单数据格式错误:', data)
        ElMessage.error('订单数据格式错误')
      }
    } else {
      console.error('未获取到订单数据')
      ElMessage.error('未获取到订单数据')
    }
  } catch (error: any) {
    console.error('获取订单详情失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('订单不存在')
      router.push('/orders')
    } else {
      ElMessage.error(`获取订单详情失败: ${error.message || '未知错误'}`)
    }
  } finally {
    loading.value = false
    isLoadingData.value = false // 确保标记被重置
  }
}

// 处理客户选择
const handleCustomerChange = (customerId: number | null) => {
  // 编辑模式下不清空明细，只重新加载产品列表
  if (isEdit.value) {
    fetchProducts(customerId || undefined)
    return
  }
  
  // 新建模式下才清空明细并重新加载产品列表
  fetchProducts(customerId || undefined)
  form.items = []
  if (customerId) {
    // 新增一行空明细，方便继续操作
    addOrderItem()
  }
}

// 标记是否正在加载数据，避免触发监听器
const isLoadingData = ref(false)

// 监听客户变化（但排除数据加载期间的变化）
watch(() => form.customer, (newVal) => {
  if (!isLoadingData.value) {
    handleCustomerChange(newVal as number | null)
  }
})

// 处理产品选择
const handleProductSelect = (productId: number, index: number) => {
  const product = productOptions.value.find(p => p.id === productId)
  if (product) {
    form.items[index].product_name = product.name
    form.items[index].unit = product.unit || '个'
  }
}

// 添加订单明细
const addOrderItem = () => {
  const newItem: OrderItemForm = {
    product: null,
    product_name: '',
    color: '',
    material: '',
    quantity: 1,
    unit: '个',
    notes: ''
  }
  
  form.items.push(newItem)
}

// 移除订单明细
const removeOrderItem = (index: number) => {
  form.items.splice(index, 1)
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 验证订单明细
    if (form.items.length === 0) {
      ElMessage.warning('请至少添加一个产品明细')
      return
    }
    
    // 验证日期
    const orderDate = new Date(form.order_date)
    const deliveryDate = new Date(form.delivery_date)
    if (deliveryDate < orderDate) {
      ElMessage.warning('交货日期不能早于下单日期')
      return
    }
    
    loading.value = true
    
    // 准备提交数据
    const submitData: any = {
      customer: form.customer,
      order_date: form.order_date,
      delivery_date: form.delivery_date,
      notes: form.notes,
      customer_order_number: form.customer_order_number,
      items: form.items.map(item => ({
        product: item.product,
        color: item.color,
        material: item.material,
        quantity: item.quantity,
        unit: item.unit,
        notes: item.notes
      }))
    }
    
    // 编辑模式下包含状态字段
    if (isEdit.value) {
      submitData.status = form.status
    }
    
    let res

    if (isEdit.value) {
      // 编辑模式
      res = await updateOrder(orderId.value as number, submitData)
      ElMessage.success('订单更新成功')
    } else {
      // 创建模式
      res = await createOrder(submitData)
      ElMessage.success('订单创建成功')
    }
    
    // 创建或编辑成功后返回列表页
    router.push('/orders')
  } catch (error: any) {
    console.error('提交表单失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(`提交失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('提交失败，请检查表单数据')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCustomers()
  fetchProducts()
  fetchMaterials()
  if (isEdit.value) {
    fetchOrderDetail()
  } else {
    // 新建时设置默认日期，但不添加空的订单明细
    // 等用户选择客户后再添加明细行
    form.order_date = new Date().toISOString().split('T')[0]
    const deliveryDate = new Date()
    deliveryDate.setDate(deliveryDate.getDate() + 7) // 默认7天后交货
    form.delivery_date = deliveryDate.toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.order-form-container {
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

.order-form {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 12px;
}

.el-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #000;
  font-weight: 600;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.items-card {
  margin-top: 20px;
}

/* 订单明细容器 */
.order-items-container {
  min-height: 200px;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  color: #dcdfe6;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #909399;
  margin-bottom: 8px;
}

.empty-subtext {
  font-size: 14px;
  color: #c0c4cc;
}

/* 订单项容器 */
.order-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 订单项卡片 */
.order-item-card {
  border: 2px solid #f0f2f5;
  border-radius: 12px;
  background: #fafbfc;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.order-item-card:hover {
  border-color: #67c23a;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.15);
  transform: translateY(-2px);
}

.order-item-card:focus-within {
  border-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

/* 订单项头部 */
.order-item-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fffe 0%, #e8f5e8 100%);
  border-bottom: 1px solid #d4e4d4;
}

.item-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

/* 订单项内容 */
.order-item-content {
  padding: 24px 20px;
  background: white;
}

/* 订单表单项样式 */
.order-form-item {
  margin-bottom: 20px;
}

.order-form-item :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.order-form-item :deep(.el-form-item__error) {
  margin-top: 4px;
  font-size: 12px;
}

/* 输入框增强样式 */
.order-item-content :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.order-item-content :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc;
}

.order-item-content :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.order-item-content :deep(.el-select) {
  width: 100%;
}

.order-item-content :deep(.el-input-number) {
  width: 100%;
}

.order-item-content :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: vertical;
  min-height: 60px;
}

/* 动画效果 */
.order-item-enter-active,
.order-item-leave-active {
  transition: all 0.5s ease;
}

.order-item-enter-from {
  opacity: 0;
  transform: translateY(-30px) scale(0.95);
}

.order-item-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}

.order-item-move {
  transition: transform 0.5s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .order-item-header {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .order-item-content {
    padding: 20px 16px;
  }

  .order-item-card {
    border-radius: 8px;
  }
  
  .order-form-item {
    margin-bottom: 16px;
  }
}

/* Enhanced field styling for detail row */
.details-row {
  margin-top: 12px;
}

.field-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: linear-gradient(135deg, #fafbfc 0%, #f0f2f5 100%);
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  transition: all 0.3s ease;
  min-height: auto;
}

.field-wrapper:hover {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f8fffe 0%, #f0f8f0 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.15);
}

.field-wrapper:focus-within {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f8fffe 0%, #f0f8f0 100%);
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

.field-icon {
  width: 20px;
  height: 20px;
  color: #67c23a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2px;
  transition: all 0.3s ease;
}

.field-wrapper:hover .field-icon {
  color: #85ce61;
  transform: scale(1.1);
}

.color-field .field-icon {
  color: #f56c6c;
}

.material-field .field-icon {
  color: #e6a23c;
}

.quantity-field .field-icon {
  color: #409eff;
}

.unit-field .field-icon {
  color: #909399;
}

.enhanced-field {
  margin-bottom: 0;
}

.enhanced-field :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.enhanced-select,
.enhanced-number,
.enhanced-input {
  width: 100%;
}

.enhanced-select :deep(.el-input__wrapper),
.enhanced-number :deep(.el-input__wrapper),
.enhanced-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.enhanced-select :deep(.el-input__wrapper):hover,
.enhanced-number :deep(.el-input__wrapper):hover,
.enhanced-input :deep(.el-input__wrapper):hover {
  border-color: #67c23a;
  box-shadow: 0 0 0 1px rgba(103, 194, 58, 0.2);
}

.enhanced-select :deep(.el-input__wrapper.is-focus),
.enhanced-number :deep(.el-input__wrapper.is-focus),
.enhanced-input :deep(.el-input__wrapper.is-focus) {
  border-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.enhanced-number :deep(.el-input-number__increase),
.enhanced-number :deep(.el-input-number__decrease) {
  border-color: #dcdfe6;
  color: #67c23a;
  transition: all 0.3s ease;
}

.enhanced-number :deep(.el-input-number__increase):hover,
.enhanced-number :deep(.el-input-number__decrease):hover {
  background-color: #f0f8f0;
  color: #85ce61;
}

/* Color selection styling */
.color-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #ddd;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.color-option:hover .color-dot {
  transform: scale(1.1);
}

.color-dot.natural {
  background: linear-gradient(135deg, #f5e6d3 0%, #e6d2b5 100%);
}

.color-dot.white {
  background: #ffffff;
  box-shadow: 0 0 0 1px #ccc;
}

.color-dot.black {
  background: #2c2c2c;
}

.color-dot.silver {
  background: linear-gradient(135deg, #e8e8e8 0%, #c0c0c0 100%);
}

.color-dot.gold {
  background: linear-gradient(135deg, #ffd700 0%, #daa520 100%);
}

.color-dot.other {
  background: linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
}

.unit-input :deep(.el-input__inner) {
  background-color: #f8f9fa;
  cursor: not-allowed;
  color: #6c757d;
  font-style: italic;
}

/* Responsive adjustments for enhanced fields */
@media (max-width: 992px) {
  .details-row .el-col {
    margin-bottom: 16px;
  }
  
  .field-wrapper {
    padding: 12px;
  }
}

@media (max-width: 576px) {
  .details-row .el-col {
    margin-bottom: 12px;
  }
  
  .field-wrapper {
    padding: 10px;
  }
  
  .field-icon {
    width: 20px;
    height: 20px;
  }
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}
</style> 