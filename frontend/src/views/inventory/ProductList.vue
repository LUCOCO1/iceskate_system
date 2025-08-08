<template>
  <div class="product-list-container">
    <div class="page-header">
      <h2>产品库存管理</h2>
      <el-button type="primary" @click="handleAddProduct">
        <el-icon><Plus /></el-icon>添加产品
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="产品名称">
          <el-input v-model="searchForm.name" placeholder="请输入产品名称" clearable />
        </el-form-item>
        <el-form-item label="关联客户">
          <el-select
            v-model="searchForm.customer"
            placeholder="选择客户筛选"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="productList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="产品名称" min-width="120" />
        <el-table-column prop="specification" label="规格" min-width="120" />
        <el-table-column prop="unit" label="单位" width="100" />
        <el-table-column prop="unit_weight" label="单重(kg)" width="120">
          <template #default="scope">
            <span v-if="scope.row.unit_weight && parseFloat(scope.row.unit_weight) > 0">
              {{ parseFloat(scope.row.unit_weight).toFixed(3) }}
            </span>
            <span v-else style="color: #999;">未设置</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存数量" width="100" />
        <el-table-column prop="min_stock" label="最低库存" width="100" />
        <el-table-column prop="warning_stock" label="预警库存" width="100" />
        <el-table-column prop="max_stock" label="最高库存" width="100" />
        <el-table-column prop="customers_display" label="关联客户" min-width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.customers_display" type="info" size="small">
              {{ scope.row.customers_display }}
            </el-tag>
            <span v-else style="color: #999;">暂无关联客户</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag
              :type="getStockStatusType(scope.row.stock_status || '正常')"
            >
              {{ scope.row.stock_status || '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加产品' : '编辑产品'"
      width="600px"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="name">
              <el-input v-model="productForm.name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品编码" prop="code">
              <el-input v-model="productForm.code" placeholder="请输入产品编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格" prop="specification">
              <el-input v-model="productForm.specification" placeholder="请输入规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="productForm.unit" placeholder="请输入单位" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单重(kg)" prop="unit_weight">
              <el-input-number 
                v-model="productForm.unit_weight" 
                :min="0" 
                :precision="3" 
                :step="0.001"
                placeholder="请输入单重"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div style="padding-top: 32px; color: #999; font-size: 12px;">
              用于材料需求计算，单重 × 数量 = 材料用量
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="库存数量" prop="stock">
              <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低库存" prop="min_stock">
              <el-input-number v-model="productForm.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预警库存" prop="warning_stock">
              <el-input-number v-model="productForm.warning_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高库存" prop="max_stock">
              <el-input-number v-model="productForm.max_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关联客户" prop="customers">
          <el-select
            v-model="productForm.customers"
            multiple
            filterable
            placeholder="选择关联的客户（可多选）"
            style="width: 100%"
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            >
              <span style="float: left">{{ customer.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ customer.code }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="productForm.notes" placeholder="请输入备注" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="productForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getProductList, createProduct, updateProduct, deleteProduct } from '@/api/inventory'
import { getCustomerList } from '@/api/orders'

// 定义客户类型接口
interface Customer {
  id: number
  name: string
  code: string
  contact?: string
  phone?: string
  address?: string
  email?: string
  is_active: boolean
  notes?: string
}

// 定义产品类型接口
interface Product {
  id: number
  name: string
  code: string
  specification?: string
  unit: string
  unit_weight?: number
  stock: number
  min_stock: number
  warning_stock: number
  max_stock: number
  notes?: string
  is_active: boolean
  stock_status?: string
  customers_display?: string
  customers?: number[]
}

// 搜索表单
const searchForm = reactive({
  name: '',
  customer: ''
})

// 表格数据
const loading = ref(false)
const productList = ref<Product[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 客户选项
const customerOptions = ref<Customer[]>([])

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const productFormRef = ref<FormInstance>()
const productForm = reactive({
  id: 0,
  name: '',
  code: '',
  specification: '',
  unit: '',
  unit_weight: 0,
  stock: 0,
  min_stock: 0,
  warning_stock: 0,
  max_stock: 0,
  notes: '',
  is_active: true,
  customers: [] as number[]
})

// 表单验证规则
const productRules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入产品编码', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ]
}

// 获取库存状态类型
const getStockStatusType = (status: string) => {
  switch (status) {
    case '低库存':
      return 'danger'
    case '库存预警':
      return 'warning'
    case '库存过高':
      return 'info'
    default:
      return 'success'
  }
}

// 生命周期钩子
onMounted(() => {
  fetchProductList()
  fetchCustomers()
})

// 获取客户列表
const fetchCustomers = async () => {
  try {
    const res = await getCustomerList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        customerOptions.value = data.results
      } else if (Array.isArray(data)) {
        customerOptions.value = data
      }
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
    // 提供默认的客户选项
    customerOptions.value = [
      { id: 1, name: '客户A', code: 'CA001', is_active: true },
      { id: 2, name: '客户B', code: 'CB001', is_active: true }
    ]
  }
}

// 获取产品列表
const fetchProductList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.customer) params.customer = searchForm.customer
    
    const res = await getProductList(params)
    
    if (res && typeof res === 'object') {
      if ('results' in res && 'count' in res) {
        productList.value = res.results as Product[]
        total.value = res.count as number
      }
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    // 模拟数据
    productList.value = [
      {
        id: 1,
        name: '专业花样冰刀',
        code: 'H2812#',
        specification: 'H2812#',
        unit: '个',
        stock: 50,
        min_stock: 10,
        warning_stock: 20,
        max_stock: 100,
        is_active: true,
        stock_status: 'in_stock',
        notes: '高品质专业花样冰刀',
        customers_display: '客户A, 客户B',
        customers: [1, 2]
      }
    ]
    total.value = productList.value.length
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchProductList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.name = ''
  searchForm.customer = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchProductList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchProductList()
}

// 添加产品
const handleAddProduct = () => {
  dialogType.value = 'add'
  productForm.id = 0
  productForm.name = ''
  productForm.code = ''
  productForm.specification = ''
  productForm.unit = ''
  productForm.unit_weight = 0
  productForm.stock = 0
  productForm.min_stock = 0
  productForm.warning_stock = 0
  productForm.max_stock = 0
  productForm.notes = ''
  productForm.is_active = true
  productForm.customers = []
  dialogVisible.value = true
}

// 编辑产品
const handleEdit = (row: Product) => {
  dialogType.value = 'edit'
  productForm.id = row.id
  productForm.name = row.name
  productForm.code = row.code || ''
  productForm.specification = row.specification || ''
  productForm.unit = row.unit
  productForm.unit_weight = row.unit_weight || 0
  productForm.stock = row.stock
  productForm.min_stock = row.min_stock
  productForm.warning_stock = row.warning_stock
  productForm.max_stock = row.max_stock
  productForm.notes = row.notes || ''
  productForm.is_active = row.is_active
  productForm.customers = Array.isArray(row.customers) ? row.customers : []
  dialogVisible.value = true
}

// 删除产品
const handleDelete = (row: Product) => {
  ElMessageBox.confirm(
    `确定要删除产品 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      fetchProductList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const submitForm = () => {
  productFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const formData = {
          name: productForm.name,
          code: productForm.code,
          specification: productForm.specification,
          unit: productForm.unit,
          unit_weight: productForm.unit_weight,
          stock: productForm.stock,
          min_stock: productForm.min_stock,
          warning_stock: productForm.warning_stock,
          max_stock: productForm.max_stock,
          notes: productForm.notes,
          is_active: productForm.is_active,
          customers: productForm.customers
        }
        
        if (dialogType.value === 'add') {
          await createProduct(formData)
          ElMessage.success('添加成功')
        } else {
          await updateProduct(productForm.id, formData)
          ElMessage.success('更新成功')
        }
        
        dialogVisible.value = false
        fetchProductList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }
  })
}
</script>

<style scoped>
.product-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style> 