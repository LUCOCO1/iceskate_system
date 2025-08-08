<template>
  <div class="product-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>产品详情</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
        <el-button type="success" @click="handleInStock">
          <el-icon><Plus /></el-icon>入库
        </el-button>
        <el-button type="warning" @click="handleOutStock">
          <el-icon><Minus /></el-icon>出库
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="产品编码">{{ product.code }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ product.name }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ product.specification || '无' }}</el-descriptions-item>
        <el-descriptions-item label="单位">{{ product.unit }}</el-descriptions-item>
        <el-descriptions-item label="单重(kg)">
          <span v-if="product.unit_weight && parseFloat(product.unit_weight) > 0">
            {{ parseFloat(product.unit_weight).toFixed(3) }}
          </span>
          <span v-else style="color: #999;">未设置</span>
        </el-descriptions-item>
        <el-descriptions-item label="当前库存">
          <span :class="getStockStatusClass()">{{ product.stock }} {{ product.unit }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="product.is_active ? 'success' : 'danger'">
            {{ product.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最小库存">{{ product.min_stock }} {{ product.unit }}</el-descriptions-item>
        <el-descriptions-item label="预警库存">{{ product.warning_stock }} {{ product.unit }}</el-descriptions-item>
        <el-descriptions-item label="最大库存">{{ product.max_stock }} {{ product.unit }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ product.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 变动记录 -->
    <el-card class="movement-card" v-loading="movementLoading">
      <template #header>
        <div class="card-header">
          <span>变动记录</span>
        </div>
      </template>
      <el-table :data="movementList" border style="width: 100%">
        <el-table-column prop="movement_date" label="变动时间" width="180" />
        <el-table-column prop="movement_type_display" label="变动类型" width="100">
          <template #default="scope">
            <el-tag :type="getMovementTypeTag(scope.row.movement_type)">
              {{ scope.row.movement_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="reference_number" label="关联单号" width="150" />
        <el-table-column prop="notes" label="备注" min-width="200" />
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="movementQuery.page"
          v-model:page-size="movementQuery.limit"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="movementTotal"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 入库对话框 -->
    <el-dialog
      v-model="inStockDialogVisible"
      title="产品入库"
      width="500px"
    >
      <el-form
        ref="inStockFormRef"
        :model="movementForm"
        :rules="movementRules"
        label-width="100px"
      >
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="movementForm.quantity" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="product.unit" disabled />
        </el-form-item>
        <el-form-item label="关联单号" prop="reference_number">
          <el-input v-model="movementForm.reference_number" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="movementForm.notes"
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="inStockDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitInStock">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog
      v-model="outStockDialogVisible"
      title="产品出库"
      width="500px"
    >
      <el-form
        ref="outStockFormRef"
        :model="movementForm"
        :rules="movementRules"
        label-width="100px"
      >
        <el-form-item label="出库数量" prop="quantity">
          <el-input-number
            v-model="movementForm.quantity"
            :min="0.01"
            :max="product.stock"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="product.unit" disabled />
        </el-form-item>
        <el-form-item label="关联单号" prop="reference_number">
          <el-input v-model="movementForm.reference_number" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="movementForm.notes"
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outStockDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitOutStock">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import { ArrowLeft, Edit, Plus, Minus } from '@element-plus/icons-vue'
import { getProductDetail, getProductMovementList, createProductMovement } from '@/api/inventory'
import type { Product, ProductMovement } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const productId = Number(route.params.id)

// 产品详情
const product = ref<Product>({} as Product)
const loading = ref(true)

// 变动记录
const movementList = ref<ProductMovement[]>([])
const movementLoading = ref(false)
const movementTotal = ref(0)
const movementQuery = reactive({
  page: 1,
  limit: 10,
  product: productId
})

// 入库/出库表单
const inStockDialogVisible = ref(false)
const outStockDialogVisible = ref(false)
const inStockFormRef = ref<FormInstance>()
const outStockFormRef = ref<FormInstance>()
const movementForm = reactive({
  product: productId,
  quantity: 0,
  reference_number: '',
  notes: ''
})
const movementRules = {
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '数量必须大于0', trigger: 'blur' }
  ],
  reference_number: [
    { required: true, message: '请输入关联单号', trigger: 'blur' }
  ]
}

// 获取产品详情
const fetchProductDetail = async () => {
  loading.value = true
  try {
    const res = await getProductDetail(productId)
    product.value = res.data
  } catch (error) {
    console.error('获取产品详情失败:', error)
    ElMessage.error('获取产品详情失败')
  } finally {
    loading.value = false
  }
}

// 获取变动记录
const fetchMovementList = async () => {
  movementLoading.value = true
  try {
    const res = await getProductMovementList({
      product: productId,
      page: movementQuery.page,
      limit: movementQuery.limit
    })
    movementList.value = res.data.results
    movementTotal.value = res.data.count
  } catch (error) {
    console.error('获取变动记录失败:', error)
    ElMessage.error('获取变动记录失败')
  } finally {
    movementLoading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑产品
const handleEdit = () => {
  // 跳转到编辑页面
  ElMessage.info('编辑功能待实现')
}

// 入库操作
const handleInStock = () => {
  movementForm.quantity = 0
  movementForm.reference_number = ''
  movementForm.notes = ''
  inStockDialogVisible.value = true
}

// 出库操作
const handleOutStock = () => {
  movementForm.quantity = 0
  movementForm.reference_number = ''
  movementForm.notes = ''
  outStockDialogVisible.value = true
}

// 提交入库
const submitInStock = async () => {
  if (!inStockFormRef.value) return
  
  await inStockFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await createProductMovement({
          product: productId,
          movement_type: 'in',
          quantity: movementForm.quantity,
          unit: product.value.unit,
          reference_number: movementForm.reference_number,
          notes: movementForm.notes
        })
        ElMessage.success('入库成功')
        inStockDialogVisible.value = false
        // 刷新数据
        fetchProductDetail()
        fetchMovementList()
      } catch (error) {
        console.error('入库失败:', error)
        ElMessage.error('入库失败')
      }
    }
  })
}

// 提交出库
const submitOutStock = async () => {
  if (!outStockFormRef.value) return
  
  await outStockFormRef.value.validate(async (valid) => {
    if (valid) {
      if (movementForm.quantity > product.value.stock) {
        ElMessage.error('出库数量不能大于库存数量')
        return
      }
      
      try {
        await createProductMovement({
          product: productId,
          movement_type: 'out',
          quantity: movementForm.quantity,
          unit: product.value.unit,
          reference_number: movementForm.reference_number,
          notes: movementForm.notes
        })
        ElMessage.success('出库成功')
        outStockDialogVisible.value = false
        // 刷新数据
        fetchProductDetail()
        fetchMovementList()
      } catch (error) {
        console.error('出库失败:', error)
        ElMessage.error('出库失败')
      }
    }
  })
}

// 分页处理
const handleSizeChange = (val: number) => {
  movementQuery.limit = val
  fetchMovementList()
}

const handleCurrentChange = (val: number) => {
  movementQuery.page = val
  fetchMovementList()
}

// 获取库存状态样式
const getStockStatusClass = () => {
  if (!product.value.stock) return ''
  
  if (product.value.stock <= product.value.min_stock) {
    return 'stock-danger'
  } else if (product.value.stock <= product.value.warning_stock) {
    return 'stock-warning'
  } else if (product.value.stock >= product.value.max_stock) {
    return 'stock-info'
  }
  return 'stock-normal'
}

// 获取变动类型标签样式
const getMovementTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'in': 'success',
    'out': 'danger'
  }
  return map[type] || 'info'
}

onMounted(() => {
  fetchProductDetail()
  fetchMovementList()
})
</script>

<style scoped>
.product-detail-container {
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

.detail-card,
.movement-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.stock-danger {
  color: #f56c6c;
  font-weight: bold;
}

.stock-warning {
  color: #e6a23c;
  font-weight: bold;
}

.stock-info {
  color: #409eff;
  font-weight: bold;
}

.stock-normal {
  color: #67c23a;
  font-weight: bold;
}
</style> 