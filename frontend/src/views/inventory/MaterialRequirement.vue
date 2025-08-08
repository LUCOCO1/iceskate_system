<template>
  <div class="material-requirement-container">
    <div class="page-header">
      <h2>材料需求计算</h2>
      <el-button type="primary" @click="showAddItemDialog">
        <el-icon><Plus /></el-icon>添加产品
      </el-button>
    </div>

    <!-- 计算方式选择 -->
    <el-card class="calculation-mode-card">
      <template #header>
        <h3>计算方式</h3>
      </template>
      
      <el-radio-group v-model="calculationMode" @change="handleModeChange">
        <el-radio-button value="manual">手动输入</el-radio-button>
        <el-radio-button value="order">从订单导入</el-radio-button>
      </el-radio-group>
      
      <!-- 订单选择 -->
      <div v-if="calculationMode === 'order'" class="order-selection">
        <el-form :inline="true" style="margin-top: 16px;">
          <el-form-item label="选择订单">
            <el-select 
              v-model="selectedOrderId" 
              placeholder="请选择订单" 
              filterable 
              style="width: 300px;"
              @change="handleOrderChange"
            >
              <el-option
                v-for="order in orderOptions"
                :key="order.id"
                :label="`${order.order_number} - ${order.customer_name}`"
                :value="order.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadOrderItems" :disabled="!selectedOrderId">
              导入订单明细
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 产品明细表格 -->
    <el-card class="items-card">
      <template #header>
        <div class="card-header">
          <h3>产品明细</h3>
          <div>
            <el-button @click="clearAllItems" :disabled="orderItems.length === 0">
              清空
            </el-button>
            <el-button type="primary" @click="calculateRequirements" :disabled="orderItems.length === 0">
              计算材料需求
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="orderItems" border style="width: 100%" empty-text="暂无产品明细">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="product_code" label="产品编码" width="120" />
        <el-table-column prop="specification" label="规格" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="unit_weight" label="单重(kg)" width="100" align="right">
          <template #default="scope">
            {{ scope.row.unit_weight || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column label="预计材料重量(kg)" width="150" align="right">
          <template #default="scope">
            <span v-if="scope.row.unit_weight > 0">
              {{ (scope.row.quantity * scope.row.unit_weight).toFixed(3) }}
            </span>
            <span v-else class="text-warning">需设置单重</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editItem(scope.$index)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="removeItem(scope.$index)"
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 计算结果 -->
    <el-card v-if="calculationResult" class="result-card">
      <template #header>
        <h3>计算结果</h3>
      </template>
      
      <!-- 汇总信息 -->
      <div class="summary-info">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">产品种类</div>
              <div class="summary-value">{{ calculationResult.summary.total_product_types }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">处理明细数</div>
              <div class="summary-value">{{ calculationResult.summary.total_items_processed }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="summary-item">
              <div class="summary-label">总材料重量</div>
              <div class="summary-value highlight">{{ calculationResult.summary.total_material_weight_display }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="calculationResult.errors && calculationResult.errors.length > 0" class="error-info">
        <el-alert 
          title="计算错误" 
          type="error" 
          :closable="false"
          style="margin-bottom: 16px;"
        >
          <ul>
            <li v-for="error in calculationResult.errors" :key="error">{{ error }}</li>
          </ul>
        </el-alert>
      </div>
      
      <!-- 材料需求汇总 -->
      <div v-if="calculationResult.material_requirements.length > 0">
        <h4>材料需求汇总</h4>
        <el-table :data="calculationResult.material_requirements" border>
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column prop="product_code" label="产品编码" width="120" />
          <el-table-column prop="total_quantity" label="总数量" width="100" align="right" />
          <el-table-column prop="unit_weight" label="单重(kg)" width="100" align="right" />
          <el-table-column prop="total_material_weight" label="总材料重量(kg)" width="150" align="right">
            <template #default="scope">
              {{ scope.row.total_material_weight.toFixed(3) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 计算详情 -->
      <div v-if="calculationResult.calculation_details.length > 0" style="margin-top: 24px;">
        <h4>计算详情</h4>
        <el-table :data="calculationResult.calculation_details" border>
          <el-table-column prop="row_number" label="行号" width="60" />
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column prop="unit_weight" label="单重(kg)" width="100" align="right" />
          <el-table-column prop="calculation_formula" label="计算公式" width="200" />
          <el-table-column prop="material_weight" label="材料重量(kg)" width="120" align="right">
            <template #default="scope">
              {{ scope.row.material_weight.toFixed(3) }}
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" />
        </el-table>
      </div>
    </el-card>

    <!-- 添加/编辑产品对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingIndex >= 0 ? '编辑产品' : '添加产品'"
      width="600px"
      append-to-body
      :max-height="'80vh'"
      :fullscreen="false"
    >
      <el-form :model="currentItem" :rules="itemRules" ref="itemFormRef" label-width="120px">
        <el-form-item label="产品" prop="product_id">
          <el-select 
            v-model="currentItem.product_id" 
            placeholder="请选择产品" 
            filterable 
            style="width: 100%;"
            @change="handleProductChange"
          >
            <el-option
              v-for="product in productOptions"
              :key="product.id"
              :label="`${product.name} (${product.code})`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number 
            v-model="currentItem.quantity" 
            :min="0.001" 
            :precision="3" 
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="单重" v-if="currentItem.unit_weight !== undefined">
          <span>{{ currentItem.unit_weight }} kg/件</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="currentItem.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { 
  getProductList, 
  calculateMaterialRequirements 
} from '@/api/inventory'
import { getOrderList } from '@/api/orders'

// 响应式数据
const calculationMode = ref('manual')
const selectedOrderId = ref<number | null>(null)
const orderOptions = ref<any[]>([])
const productOptions = ref<any[]>([])
const orderItems = ref<any[]>([])
const calculationResult = ref<any>(null)

const dialogVisible = ref(false)
const editingIndex = ref(-1)
const currentItem = reactive({
  product_id: null,
  product_name: '',
  product_code: '',
  specification: '',
  quantity: 1,
  unit_weight: 0,
  notes: ''
})

const itemRules = {
  product_id: [{ required: true, message: '请选择产品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

// 生命周期
onMounted(() => {
  fetchProducts()
  fetchOrders()
})

// 获取产品列表
const fetchProducts = async () => {
  try {
    const response = await getProductList({ page_size: 1000 })
    productOptions.value = response.data?.results || []
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  }
}

// 获取订单列表
const fetchOrders = async () => {
  try {
    const response = await getOrderList({ 
      page_size: 1000,
      status: ['pending', 'processing', 'completed']
    })
    orderOptions.value = response.data?.results || []
  } catch (error) {
    console.error('获取订单列表失败:', error)
  }
}

// 计算模式切换
const handleModeChange = () => {
  if (calculationMode.value === 'manual') {
    selectedOrderId.value = null
  }
  orderItems.value = []
  calculationResult.value = null
}

// 订单选择变化
const handleOrderChange = () => {
  orderItems.value = []
  calculationResult.value = null
}

// 导入订单明细
const loadOrderItems = async () => {
  if (!selectedOrderId.value) return
  
  try {
    const response = await calculateMaterialRequirements({
      order_id: selectedOrderId.value
    })
    
    if (response.data.success) {
      // 转换为表格数据格式
      orderItems.value = response.data.calculation_details.map((detail: any) => ({
        product_id: detail.product_id,
        product_name: detail.product_name,
        product_code: detail.product_code,
        specification: '', // 从产品信息中获取
        quantity: detail.quantity,
        unit_weight: detail.unit_weight,
        notes: detail.notes
      }))
      
      ElMessage.success('订单明细导入成功')
    } else {
      ElMessage.error(`导入失败: ${response.data.errors.join(', ')}`)
    }
  } catch (error) {
    console.error('导入订单明细失败:', error)
    ElMessage.error('导入订单明细失败')
  }
}

// 显示添加产品对话框
const showAddItemDialog = () => {
  editingIndex.value = -1
  resetCurrentItem()
  dialogVisible.value = true
}

// 编辑产品
const editItem = (index: number) => {
  editingIndex.value = index
  const item = orderItems.value[index]
  Object.assign(currentItem, item)
  dialogVisible.value = true
}

// 删除产品
const removeItem = (index: number) => {
  orderItems.value.splice(index, 1)
  calculationResult.value = null
  ElMessage.success('删除成功')
}

// 清空所有产品
const clearAllItems = () => {
  orderItems.value = []
  calculationResult.value = null
  ElMessage.success('已清空所有产品')
}

// 产品选择变化
const handleProductChange = (productId: number) => {
  const product = productOptions.value.find(p => p.id === productId)
  if (product) {
    currentItem.product_name = product.name
    currentItem.product_code = product.code
    currentItem.specification = product.specification
    currentItem.unit_weight = product.unit_weight || 0
  }
}

// 保存产品
const saveItem = () => {
  if (!currentItem.product_id) {
    ElMessage.error('请选择产品')
    return
  }
  
  if (currentItem.quantity <= 0) {
    ElMessage.error('数量必须大于0')
    return
  }
  
  const itemData = { ...currentItem }
  
  if (editingIndex.value >= 0) {
    // 编辑模式
    orderItems.value[editingIndex.value] = itemData
    ElMessage.success('修改成功')
  } else {
    // 添加模式
    orderItems.value.push(itemData)
    ElMessage.success('添加成功')
  }
  
  dialogVisible.value = false
  calculationResult.value = null
}

// 重置当前编辑项
const resetCurrentItem = () => {
  Object.assign(currentItem, {
    product_id: null,
    product_name: '',
    product_code: '',
    specification: '',
    quantity: 1,
    unit_weight: 0,
    notes: ''
  })
}

// 计算材料需求
const calculateRequirements = async () => {
  if (orderItems.value.length === 0) {
    ElMessage.error('请先添加产品明细')
    return
  }
  
  try {
    const requestData = {
      order_items: orderItems.value.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        product_name: item.product_name,
        notes: item.notes
      }))
    }
    
    const response = await calculateMaterialRequirements(requestData)
    calculationResult.value = response.data
    
    if (response.data.success) {
      ElMessage.success('材料需求计算完成')
    } else {
      ElMessage.warning('计算完成，但存在错误，请查看详情')
    }
  } catch (error) {
    console.error('计算材料需求失败:', error)
    ElMessage.error('计算材料需求失败')
  }
}
</script>

<style scoped>
.material-requirement-container {
  padding: 20px;
  color: #000;
  max-width: 1200px; /* 添加最大宽度限制 */
  margin: 0 auto; /* 水平居中对齐 */
  box-sizing: border-box; /* 确保padding不会增加总宽度 */
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

.calculation-mode-card,
.items-card,
.result-card {
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

.order-selection {
  margin-top: 16px;
}

.summary-info {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #000;
}

.summary-value.highlight {
  color: #409eff;
}

.error-info {
  margin-bottom: 16px;
}

.text-warning {
  color: #e6a23c;
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

:deep(.el-form-item__label) {
  color: #000;
  font-weight: 500;
}

:deep(.el-radio-button__inner) {
  color: #000;
}

:deep(.el-input), :deep(.el-input-number) {
  z-index: 1000;
  position: relative;
}
.el-dialog__body {
  max-height: calc(80vh - 120px);
  overflow-y: auto;
  padding: 20px;
}
</style>