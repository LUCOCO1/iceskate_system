<template>
  <div class="production-order-form-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>{{ isEdit ? '编辑生产订单' : '创建生产订单' }}</h2>
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
      <el-card>
        <template #header>
          <div class="card-header">
            基本信息
          </div>
        </template>

        <el-row :gutter="20" v-if="!isEdit">
          <el-col :span="24">
            <el-form-item label="关联销售订单" prop="sales_order">
              <el-select 
                v-model="form.sales_order" 
                placeholder="请选择销售订单（可选，选择后自动填充产品信息）" 
                style="width: 100%;"
                clearable
                filterable
                @change="handleOrderSelect"
                :loading="loadingOrders"
              >
                <el-option 
                  v-for="order in orderOptions" 
                  :key="order.id"
                  :label="`${order.order_number} - ${order.customer_name} (${order.status_display})`" 
                  :value="order.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="orderOptions.length === 0 && !loadingOrders">
          <el-col :span="24">
            <el-alert
              title="暂无可关联的销售订单"
              type="info"
              description="当前没有'待处理'或'生产中'状态的销售订单可供关联。您可以直接创建生产订单。"
              show-icon
              :closable="false"
            />
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product">
              <el-select 
                v-if="!form.sales_order"
                v-model="form.product" 
                placeholder="请选择产品" 
                style="width: 100%;"
                filterable
                @change="handleProductSelect"
              >
                <el-option 
                  v-for="product in productOptions" 
                  :key="product.id"
                  :label="product.name" 
                  :value="product.id"
                />
              </el-select>
              <!-- 当选择了销售订单时，显示产品名称 -->
              <el-input 
                v-else
                v-model="form.product_name"
                readonly
                placeholder="从订单自动填充"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划数量" prop="planned_quantity">
              <el-input-number 
                v-model="form.planned_quantity" 
                :min="1" 
                :precision="0" 
                style="width: 100%;" 
                placeholder="请输入计划数量"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%;">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="responsible_person">
              <el-input v-model="form.responsible_person" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（非必填）"
          />
        </el-form-item>
      </el-card>

      <el-card class="material-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="header-title">材料需求</span>
              <el-tag v-if="form.material_requirements.length > 0" type="info" size="small">
                {{ form.material_requirements.length }} 种材料
              </el-tag>
            </div>
            <el-button 
              type="primary" 
              @click="addMaterialRow" 
              :icon="Plus"
              size="small"
            >
              添加材料
            </el-button>
          </div>
        </template>

        <div class="material-requirements-container">
          <div v-if="form.material_requirements.length === 0" class="empty-state">
            <div class="empty-icon">
              <el-icon size="48"><Box /></el-icon>
            </div>
            <div class="empty-text">还没有添加材料需求</div>
            <div class="empty-subtext">点击上方"添加材料"按钮开始添加</div>
          </div>

          <transition-group name="material-item" tag="div" class="material-items">
            <div 
              v-for="(item, index) in form.material_requirements" 
              :key="index" 
              class="material-item-card"
            >
              <div class="material-item-header">
                <div class="item-number">{{ index + 1 }}</div>
                <div class="item-title">材料需求 {{ index + 1 }}</div>
                <el-button 
                  type="danger" 
                  @click="removeMaterialRow(index)"
                  :icon="Delete"
                  size="small"
                  circle
                  plain
                  title="删除此材料需求"
                />
              </div>

              <div class="material-item-content">
                <!-- 第一行：材料名称 -->
                <el-row :gutter="16">
                  <el-col :span="24">
                    <el-form-item 
                      label="材料名称"
                      :prop="`material_requirements.${index}.material_name`"
                      :rules="{ required: true, message: '请选择材料', trigger: 'change' }"
                      class="material-form-item"
                    >
                      <el-select 
                        v-model="item.material_name" 
                        placeholder="请选择材料" 
                        filterable 
                        clearable
                        style="width: 100%;"
                        @change="(val: string) => handleMaterialSelect(val, index)"
                      >
                        <el-option 
                          v-for="materialOption in materialOptions" 
                          :key="materialOption.name"
                          :label="materialOption.name" 
                          :value="materialOption.name"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 第二行：材料规格、需求数量 -->
                <el-row :gutter="16">
                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <el-form-item 
                      label="材料规格"
                      :prop="`material_requirements.${index}.material_specification`"
                      class="material-form-item"
                    >
                      <el-input 
                        v-model="item.material_specification" 
                        placeholder="自动填充规格" 
                        readonly
                        style="width: 100%;"
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
                    <el-form-item 
                      label="需求数量"
                      :prop="`material_requirements.${index}.required_quantity`"
                      :rules="{ required: true, message: '请输入数量', trigger: 'blur' }"
                      class="material-form-item"
                    >
                      <el-input-number 
                        v-model="item.required_quantity" 
                        :min="1" 
                        :precision="0" 
                        style="width: 100%;"
                        placeholder="数量"
                        controls-position="right"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 第三行：备注说明 -->
                <el-row :gutter="16">
                  <el-col :span="24">
                    <el-form-item 
                      label="备注说明"
                      :prop="`material_requirements.${index}.notes`"
                      class="material-form-item"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { ArrowLeft, Plus, Delete, Box } from '@element-plus/icons-vue'
import { 
  getProductionOrderDetail, 
  createProductionOrder, 
  updateProductionOrder
} from '@/api/production'
import { getMaterialList, getProductList } from '@/api/inventory'
import { getOrderList, getOrderDetail } from '@/api/orders'
import type { ProductionOrderForm, MaterialRequirementForm } from '@/types/production'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 判断是创建还是编辑模式
const isEdit = computed(() => route.params.id !== undefined)
const orderId = computed(() => (isEdit.value ? Number(route.params.id) : null))

// 选项数据
const materialOptions = ref<{ id: number; name: string; specification: string }[]>([])
const productOptions = ref<{ id: number; name: string; unit: string }[]>([])
const orderOptions = ref<{ id: number; order_number: string; customer_name: string; status_display: string; items: any[] }[]>([])
const loadingOrders = ref(false)

// 表单数据
const form = reactive<ProductionOrderForm>({
  sales_order: undefined,
  product: undefined,
  product_name: '',
  planned_quantity: 0,
  start_date: '',
  end_date: '',
  priority: 'medium',
  responsible_person: '',
  notes: '',
  material_requirements: []
})

// 表单验证规则
const rules = {
  product: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  planned_quantity: [
    { required: true, message: '请输入计划数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  responsible_person: [
    { required: true, message: '请输入负责人', trigger: 'blur' }
  ]
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取销售订单列表
const fetchOrders = async () => {
  if (isEdit.value) return // 编辑模式不需要加载订单
  
  loadingOrders.value = true
  try {
    // 先尝试获取所有订单，再在前端过滤
    const params = { 
      page_size: 100 
    }
    console.log('请求销售订单参数:', params)
    
    const res = await getOrderList(params)
    console.log('获取到的完整订单响应:', res) // 添加调试日志
    
    if (res) {
      // 处理DRF分页响应格式: {count: X, results: [...]} 或直接的数组
      let allOrders
      if (res.results) {
        // DRF分页格式
        allOrders = res.results
      } else if (res.data && res.data.results) {
        // 可能被axios包装了一层
        allOrders = res.data.results
      } else if (res.data && Array.isArray(res.data)) {
        // axios包装的数组格式
        allOrders = res.data
      } else if (Array.isArray(res)) {
        // 直接数组格式
        allOrders = res
      } else {
        console.warn('未知的响应格式:', res)
        allOrders = []
      }
      
      console.log('提取的订单数组:', allOrders) // 添加调试日志
      console.log('订单数组长度:', Array.isArray(allOrders) ? allOrders.length : '不是数组')
      
      if (Array.isArray(allOrders)) {
        // 打印所有订单的状态，便于调试
        console.log('所有订单状态分布:')
        const statusCount = {}
        allOrders.forEach((order: any, index: number) => {
          console.log(`订单 ${index + 1}: ${order.order_number} - 状态: ${order.status} (${order.status_display || '无显示名称'})`)
          statusCount[order.status] = (statusCount[order.status] || 0) + 1
        })
        console.log('状态统计:', statusCount)
        
        // 前端过滤状态为pending和processing的订单
        const filteredOrders = allOrders.filter((order: any) => 
          order.status === 'pending' || order.status === 'processing'
        )
        console.log('过滤后的订单:', filteredOrders)
        console.log('过滤后订单数量:', filteredOrders.length)
        
        // 打印第一个订单的详细信息
        if (filteredOrders.length > 0) {
          console.log('第一个订单详情:', filteredOrders[0])
          console.log('第一个订单字段:', Object.keys(filteredOrders[0]))
        }
        
        orderOptions.value = filteredOrders.map((order: any, index: number) => {
          console.log(`处理订单 ${index + 1}:`, {
            id: order.id,
            order_number: order.order_number,
            customer_name: order.customer_name,
            status: order.status,
            status_display: order.status_display,
            items_count: order.items ? order.items.length : 0
          })
          
          return {
            id: order.id,
            order_number: order.order_number,
            customer_name: order.customer_name || '未知客户',
            status_display: order.status_display || order.status,
            items: order.items || []
          }
        })
        console.log('最终订单选项列表:', orderOptions.value)
        console.log('可选订单数量:', orderOptions.value.length)
      } else {
        console.warn('订单数据不是数组格式:', allOrders)
        orderOptions.value = []
      }
    } else {
      console.warn('未获取到有效的订单数据, res:', res)
      orderOptions.value = []
    }
  } catch (error: any) {
    console.error('获取销售订单列表失败:', error)
    if (error.response) {
      console.error('响应错误详情:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      })
      console.error('错误响应数据:', JSON.stringify(error.response.data, null, 2))
      ElMessage.error(`获取销售订单列表失败: ${error.response.status} - ${JSON.stringify(error.response.data)}`)
    } else if (error.request) {
      console.error('请求错误:', error.request)
      ElMessage.error('网络请求失败，请检查后端服务是否启动')
    } else {
      console.error('其他错误:', error.message)
      ElMessage.error(`获取销售订单列表失败: ${error.message}`)
    }
    orderOptions.value = []
  } finally {
    loadingOrders.value = false
  }
}

// 处理销售订单选择
const handleOrderSelect = async (orderId: number | undefined) => {
  console.log('=== 开始处理订单选择 ===')
  console.log('选中的订单ID:', orderId)
  
  if (!orderId) {
    console.log('清空订单选择，重置表单')
    // 清空时重置表单
    form.product = undefined
    form.product_name = ''
    form.planned_quantity = 0
    form.material_requirements = []
    return
  }

  try {
    loading.value = true
    console.log('开始获取订单详情...')
    const res = await getOrderDetail(orderId)
    console.log('订单详情API完整响应:', res)
    console.log('响应类型:', typeof res)
    console.log('响应keys:', Object.keys(res || {}))
    
    // 处理不同的响应格式
    let orderData
    if (res && res.data) {
      // 如果有data字段，使用data字段的内容
      orderData = res.data
    } else if (res && res.id) {
      // 如果直接返回了订单对象（包含id字段），直接使用
      orderData = res
    } else {
      console.error('无效的API响应格式:', res)
      ElMessage.error('获取订单详情失败：响应格式无效')
      return
    }
    
    if (orderData) {
      console.log('提取的订单数据:', orderData)
      console.log('订单数据类型:', typeof orderData)
      console.log('订单数据keys:', Object.keys(orderData || {}))
      console.log('订单items:', orderData.items)
      console.log('订单items类型:', typeof orderData.items)
      console.log('订单items是否为数组:', Array.isArray(orderData.items))
      console.log('订单items长度:', orderData.items ? orderData.items.length : 'undefined')
      
      // 如果订单有产品项，自动填充产品信息
      if (orderData.items && Array.isArray(orderData.items) && orderData.items.length > 0) {
        console.log('=== 开始处理产品项 ===')
        console.log('产品项数量:', orderData.items.length)
        
        // 打印所有产品项的详细信息
        orderData.items.forEach((item: any, index: number) => {
          console.log(`产品项 ${index + 1}:`, item)
          console.log(`产品项 ${index + 1} keys:`, Object.keys(item || {}))
          console.log(`产品项 ${index + 1} product字段:`, item.product)
          console.log(`产品项 ${index + 1} product_name字段:`, item.product_name)
          console.log(`产品项 ${index + 1} quantity字段:`, item.quantity)
        })
        
        // 如果只有一个产品，直接填充
        if (orderData.items.length === 1) {
          console.log('单个产品处理')
          const item = orderData.items[0]
          console.log('处理的产品项:', item)
          
          form.product = item.product
          form.product_name = item.product_name || `产品${item.product}`
          form.planned_quantity = Number(item.quantity) || 0
          
          console.log('填充后的form.product:', form.product)
          console.log('填充后的form.product_name:', form.product_name)
          console.log('填充后的form.planned_quantity:', form.planned_quantity)
          
          // 确保产品选择框显示正确，需要查找产品选项中的名称
          console.log('当前产品选项列表:', productOptions.value)
          console.log('当前产品选项数量:', productOptions.value.length)
          console.log('要查找的产品ID:', item.product)
          
          const productOption = productOptions.value.find(p => p.id === item.product)
          console.log('找到的产品选项:', productOption)
          
          if (productOption) {
            form.product_name = productOption.name
            console.log('从产品选项中更新产品名称:', form.product_name)
          } else {
            console.warn('未找到匹配的产品选项，产品ID:', item.product)
            // 如果没找到，尝试从订单项中获取产品名称
            if (item.product_name) {
              form.product_name = item.product_name
              console.log('使用订单项中的产品名称:', form.product_name)
            }
            
            // 如果产品列表为空，可能是还没加载完成，等待后重试
            if (productOptions.value.length === 0) {
              console.log('产品列表为空，等待产品数据加载后重试...')
              // 等待产品数据加载完成后重新处理
              setTimeout(() => {
                console.log('重试查找产品，当前产品列表长度:', productOptions.value.length)
                const retryProductOption = productOptions.value.find(p => p.id === item.product)
                if (retryProductOption) {
                  form.product_name = retryProductOption.name
                  console.log('重试成功，更新产品名称:', form.product_name)
                }
              }, 1000)
            }
          }
        } else {
          console.log('多个产品处理')
          // 如果有多个产品，选择第一个作为主要产品，但保留所有产品信息
          const firstItem = orderData.items[0]
          console.log('选中的第一个产品项:', firstItem)
          
          form.product = firstItem.product
          form.product_name = firstItem.product_name || `产品${firstItem.product}`
          
          // 确保产品选择框显示正确，需要查找产品选项中的名称
          console.log('当前产品选项列表:', productOptions.value)
          console.log('当前产品选项数量:', productOptions.value.length)
          console.log('要查找的产品ID:', firstItem.product)
          
          const productOption = productOptions.value.find(p => p.id === firstItem.product)
          console.log('找到的产品选项:', productOption)
          
          if (productOption) {
            form.product_name = productOption.name
            console.log('从产品选项中更新产品名称:', form.product_name)
          } else {
            console.warn('未找到匹配的产品选项，产品ID:', firstItem.product)
            // 如果没找到，尝试从订单项中获取产品名称
            if (firstItem.product_name) {
              form.product_name = firstItem.product_name
              console.log('使用订单项中的产品名称:', form.product_name)
            }
          }
          
          // 计算该产品的总数量（同一产品可能有多行）
          const sameProductItems = orderData.items.filter((item: any) => item.product === firstItem.product)
          console.log('相同产品的项目:', sameProductItems)
          const productQuantity = sameProductItems.reduce((sum: number, item: any) => sum + Number(item.quantity), 0)
          form.planned_quantity = productQuantity
          
          console.log('填充后的form.product:', form.product)
          console.log('填充后的form.product_name:', form.product_name)
          console.log('填充后的form.planned_quantity:', form.planned_quantity)
          
          // 如果有其他不同产品，在备注中提醒
          const uniqueProducts = [...new Set(orderData.items.map((item: any) => item.product_name || `产品${item.product}`))]
          console.log('所有不同的产品:', uniqueProducts)
          if (uniqueProducts.length > 1) {
            const otherProducts = uniqueProducts.filter(name => name !== (firstItem.product_name || `产品${firstItem.product}`))
            console.log('其他产品:', otherProducts)
            ElMessage.warning(`订单包含多个产品，已选择${firstItem.product_name || `产品${firstItem.product}`}，其他产品：${otherProducts.join('、')}`)
          }
        }
        
        // 自动填充备注
        const customerInfo = orderData.customer_name ? `客户：${orderData.customer_name}` : ''
        const orderInfo = `订单号：${orderData.order_number}`
        const productInfo = orderData.items.length > 1 ? `包含${orderData.items.length}个产品项` : ''
        form.notes = `从销售订单自动创建 - ${orderInfo}${customerInfo ? '; ' + customerInfo : ''}${productInfo ? '; ' + productInfo : ''}`
        
        console.log('生成的备注:', form.notes)
        console.log('=== 产品填充完成 ===')
        console.log('最终表单状态:', {
          product: form.product,
          product_name: form.product_name,
          planned_quantity: form.planned_quantity,
          sales_order: form.sales_order,
          notes: form.notes
        })
        
        ElMessage.success(`已从订单 ${orderData.order_number} 自动填充产品信息`)
      } else {
        console.warn('订单没有有效的产品明细')
        console.log('orderData.items值:', orderData.items)
        ElMessage.warning('该订单没有产品明细，请手动选择产品')
      }
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    if (error.response) {
      console.error('错误响应详情:', error.response)
    }
    ElMessage.error('获取订单详情失败')
  } finally {
    loading.value = false
    console.log('=== 订单选择处理结束 ===')
  }
}

// 处理产品选择
const handleProductSelect = (productId: number) => {
  const product = productOptions.value.find(p => p.id === productId)
  if (product) {
    form.product_name = product.name
  }
}

// 获取产品列表
const fetchProducts = async () => {
  try {
    const res = await getProductList()
    if (res && res.data) {
      productOptions.value = res.data.results || res.data
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  }
}

// 获取材料列表
const fetchMaterials = async () => {
  try {
    console.log('开始获取材料列表...')
    const res = await getMaterialList()
    console.log('材料列表API完整响应:', res)
    console.log('材料列表API响应类型:', typeof res)
    console.log('材料列表API响应键:', Object.keys(res || {}))
    
    // 处理axios可能包装的响应
    let actualData = res
    
    // 如果是axios响应格式，提取data字段
    if (res && typeof res === 'object' && 'data' in res) {
      actualData = res.data
      console.log('提取axios的data字段:', actualData)
      console.log('data字段类型:', typeof actualData)
      console.log('data字段键:', Object.keys(actualData || {}))
    }
    
    if (actualData && typeof actualData === 'object') {
      let materialsData
      
      // 处理不同的响应格式
      if (actualData.results && Array.isArray(actualData.results)) {
        // DRF分页格式
        console.log('检测到DRF分页格式')
        materialsData = actualData.results
      } else if (Array.isArray(actualData)) {
        // 直接数组格式
        console.log('检测到直接数组格式')
        materialsData = actualData
      } else if (actualData.data && Array.isArray(actualData.data)) {
        // 嵌套的data数组
        console.log('检测到嵌套data数组格式')
        materialsData = actualData.data
      } else {
        console.warn('未知的材料数据格式，尝试直接使用:', actualData)
        // 尝试将对象转换为数组（可能是单个对象）
        materialsData = [actualData]
      }
      
      console.log('提取的材料数据:', materialsData)
      console.log('材料数据类型:', typeof materialsData)
      console.log('是否为数组:', Array.isArray(materialsData))
      console.log('材料数据长度:', Array.isArray(materialsData) ? materialsData.length : '不是数组')
      
      if (Array.isArray(materialsData) && materialsData.length > 0) {
        // 检查第一个材料项的结构
        console.log('第一个材料项结构:', materialsData[0])
        console.log('第一个材料项键:', Object.keys(materialsData[0] || {}))
        
        materialOptions.value = materialsData.map((item: any, index: number) => {
          console.log(`处理材料项 ${index + 1}:`, item)
          const mappedItem = {
            id: item.id,
            name: item.name || item.material_name || `材料${item.id}`,
            specification: item.specification || item.spec || item.material_specification || ''
          }
          console.log(`映射后的材料项 ${index + 1}:`, mappedItem)
          return mappedItem
        })
        console.log('最终材料选项列表:', materialOptions.value)
        ElMessage.success(`已加载 ${materialOptions.value.length} 个材料`)
      } else if (Array.isArray(materialsData) && materialsData.length === 0) {
        console.warn('材料数据数组为空')
        materialOptions.value = []
        ElMessage.warning('未找到可用材料，请先在库存管理中添加材料')
      } else {
        console.warn('材料数据不是有效数组:', materialsData)
        materialOptions.value = []
        ElMessage.warning('材料数据格式不正确')
      }
    } else {
      console.error('材料数据响应无效:', actualData)
      materialOptions.value = []
      ElMessage.error('获取材料数据失败：响应格式无效')
    }
  } catch (error: any) {
    console.error('获取材料列表失败:', error)
    materialOptions.value = []
    
    if (error.response) {
      console.error('API错误响应:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      })
      ElMessage.error(`获取材料列表失败: ${error.response.status} - ${error.response.statusText}`)
    } else if (error.request) {
      console.error('网络请求失败:', error.request)
      ElMessage.error('网络请求失败，请检查后端服务是否启动')
    } else {
      console.error('其他错误:', error.message)
      ElMessage.error(`获取材料列表失败: ${error.message}`)
    }
  }
}

// 获取订单详情（编辑模式）
const fetchOrderDetail = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const res = await getProductionOrderDetail(orderId.value as number)
    if (res && typeof res === 'object') {
      const data = res.data || res
      
      // 填充表单数据
      form.sales_order = data.sales_order
      form.product = data.product
      form.product_name = data.product_name || ''
      form.planned_quantity = data.planned_quantity || 0
      form.start_date = data.start_date || ''
      form.end_date = data.end_date || ''
      form.priority = data.priority || 'medium'
      form.responsible_person = data.responsible_person || ''
      form.notes = data.notes || ''
      
      // 填充材料需求
      if (data.material_requirements && Array.isArray(data.material_requirements)) {
        form.material_requirements = data.material_requirements.map((item: any) => ({
          material_name: item.material_name || '',
          material_specification: item.material_specification || '',
          required_quantity: item.required_quantity || 0,
          notes: item.notes || ''
        }))
      }
    }
  } catch (error) {
    console.error('获取生产订单详情失败:', error)
    ElMessage.error('获取生产订单详情失败')
  } finally {
    loading.value = false
  }
}

// 添加材料行
const addMaterialRow = () => {
  form.material_requirements.push({
    material_name: '',
    material_specification: '',
    required_quantity: 1,
    notes: ''
  })
}

// 移除材料行
const removeMaterialRow = (index: number) => {
  form.material_requirements.splice(index, 1)
}

// 选择材料时自动填充规格
const handleMaterialSelect = (materialName: string, index: number) => {
  const material = materialOptions.value.find(item => item.name === materialName)
  if (material) {
    form.material_requirements[index].material_specification = material.specification
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 验证产品是否选择
    if (!form.product) {
      ElMessage.warning('请选择产品')
      return
    }
    
    // 验证材料需求是否为空
    if (form.material_requirements.length === 0) {
      ElMessage.warning('请至少添加一种材料需求，否则无法开始生产')
      return
    }
    
    // 验证日期
    const startDate = new Date(form.start_date)
    const endDate = new Date(form.end_date)
    if (endDate < startDate) {
      ElMessage.warning('结束日期不能早于开始日期')
      return
    }
    
    loading.value = true
    
    // 准备提交数据
    const submitData = {
      sales_order: form.sales_order || null, // 改为null而不是undefined
      product: form.product,
      planned_quantity: form.planned_quantity,
      start_date: form.start_date,
      end_date: form.end_date,
      priority: form.priority,
      responsible_person: form.responsible_person,
      notes: form.notes,
      // order_number字段让后端自动生成，不需要前端传递
      material_requirements_data: form.material_requirements // 添加材料需求数据
    }
    console.log('=== 开始提交表单 ===')
    console.log('表单材料需求数据:', form.material_requirements)
    console.log('提交的数据:', submitData)
    console.log('材料需求数据详情:', submitData.material_requirements_data)
    
    let res

    if (isEdit.value) {
      // 编辑模式
      console.log('编辑模式，订单ID:', orderId.value)
      res = await updateProductionOrder(orderId.value as number, submitData)
      ElMessage.success('生产订单更新成功')
    } else {
      // 创建模式
      console.log('创建模式，调用createProductionOrder')
      res = await createProductionOrder(submitData)
      ElMessage.success('生产订单创建成功')
    }
    
    console.log('提交成功，响应:', res)
    // 创建或编辑成功后返回列表页
    router.push('/production/production-orders')
  } catch (error: any) {
    console.error('=== 提交表单失败详情 ===')
    console.error('完整错误对象:', error)
    console.error('错误类型:', error.constructor.name)
    console.error('错误消息:', error.message)
    
    if (error.response) {
      console.error('HTTP响应错误:')
      console.error('- 状态码:', error.response.status)
      console.error('- 状态文本:', error.response.statusText)
      console.error('- 响应头:', error.response.headers)
      console.error('- 响应数据:', error.response.data)
      console.error('- 响应数据类型:', typeof error.response.data)
      console.error('- 响应数据键:', error.response.data ? Object.keys(error.response.data) : '无')
      console.error('- 响应数据完整内容:', JSON.stringify(error.response.data, null, 2))
      
      // 尝试提取具体错误信息
      let errorMessage = '提交失败'
      if (error.response.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response.data.non_field_errors) {
          errorMessage = Array.isArray(error.response.data.non_field_errors) 
            ? error.response.data.non_field_errors.join('; ')
            : error.response.data.non_field_errors
        } else {
          // 尝试提取第一个字段的错误
          const firstFieldError = Object.values(error.response.data)[0]
          if (Array.isArray(firstFieldError)) {
            errorMessage = firstFieldError[0]
          } else if (typeof firstFieldError === 'string') {
            errorMessage = firstFieldError
          } else {
            errorMessage = `服务器返回错误 (${error.response.status}): ${JSON.stringify(error.response.data)}`
          }
        }
      }
      
      ElMessage.error(`${errorMessage}`)
    } else if (error.request) {
      console.error('网络请求错误:', error.request)
      ElMessage.error('网络请求失败，请检查网络连接和后端服务')
    } else {
      console.error('其他错误:', error.message)
      ElMessage.error(`提交失败: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 确保按顺序加载，先加载基础数据再加载订单选项
  await fetchMaterials()
  await fetchProducts()
  await fetchOrders()
  
  if (isEdit.value) {
    await fetchOrderDetail()
  } else {
    // 新建时添加一行空的材料需求
    addMaterialRow()
  }
})
</script>

<style scoped>
.production-order-form-container {
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
  max-width: 1200px;
  margin: 0 auto;
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

.material-card {
  margin-top: 20px;
}

/* 材料需求容器 */
.material-requirements-container {
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

/* 材料项容器 */
.material-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 材料项卡片 */
.material-item-card {
  border: 2px solid #f0f2f5;
  border-radius: 12px;
  background: #fafbfc;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.material-item-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.material-item-card:focus-within {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 材料项头部 */
.material-item-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
}

.item-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
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

/* 材料项内容 */
.material-item-content {
  padding: 24px 20px;
  background: white;
}

/* 材料表单项样式 */
.material-form-item {
  margin-bottom: 20px;
}

.material-form-item :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.material-form-item :deep(.el-form-item__error) {
  margin-top: 4px;
  font-size: 12px;
}

/* 输入框增强样式 */
.material-item-content :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.material-item-content :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc;
}

.material-item-content :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.material-item-content :deep(.el-select) {
  width: 100%;
}

.material-item-content :deep(.el-input-number) {
  width: 100%;
}

.material-item-content :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: vertical;
  min-height: 60px;
}

/* 动画效果 */
.material-item-enter-active,
.material-item-leave-active {
  transition: all 0.5s ease;
}

.material-item-enter-from {
  opacity: 0;
  transform: translateY(-30px) scale(0.95);
}

.material-item-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}

.material-item-move {
  transition: transform 0.5s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .material-item-header {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .material-item-content {
    padding: 20px 16px;
  }

  .material-item-card {
    border-radius: 8px;
  }
  
  .material-form-item {
    margin-bottom: 16px;
  }
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.table-form-item {
  margin-bottom: 0 !important;
}

:deep(.el-form-item__error) {
  position: static;
  margin-top: 2px;
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