<template>
  <div class="material-list-container">
    <div class="page-header">
      <h2>材料库存管理</h2>
      <el-button type="primary" @click="handleAddMaterial">
        <el-icon><Plus /></el-icon>添加材料
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="材料编码">
          <el-input v-model="searchForm.code" placeholder="请输入材料编码" clearable />
        </el-form-item>
        <el-form-item label="材料名称">
          <el-input v-model="searchForm.name" placeholder="请输入材料名称" clearable />
        </el-form-item>
        <el-form-item label="库存状态">
          <el-select v-model="searchForm.stock_status" placeholder="请选择库存状态" clearable>
            <el-option label="库存不足" value="low" />
            <el-option label="库存预警" value="warning" />
            <el-option label="库存正常" value="normal" />
            <el-option label="库存过高" value="high" />
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
        :data="materialList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="材料编码" min-width="120" />
        <el-table-column prop="name" label="材料名称" min-width="120" />
        <el-table-column prop="specification" label="规格" min-width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column label="库存数量" width="120">
          <template #default="scope">
            <span :class="getStockStatusClass(scope.row)">
              {{ scope.row.stock }} {{ scope.row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="last_purchase_price" label="最近采购价" width="120">
          <template #default="scope">
            {{ scope.row.last_purchase_price ? `¥${scope.row.last_purchase_price}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleViewDetail(scope.row)"
              text
            >
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleEdit(scope.row)"
              text
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleInStock(scope.row)"
              text
            >
              <el-icon><Plus /></el-icon>入库
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleOutStock(scope.row)"
              text
            >
              <el-icon><Minus /></el-icon>出库
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              text
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.limit"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 材料表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加材料' : '编辑材料'"
      width="600px"
    >
      <el-form
        ref="materialFormRef"
        :model="materialForm"
        :rules="materialRules"
        label-width="100px"
      >
        <el-form-item label="材料编码" prop="code">
          <el-input v-model="materialForm.code" placeholder="请输入材料编码" />
        </el-form-item>
        <el-form-item label="材料名称" prop="name">
          <el-input v-model="materialForm.name" placeholder="请输入材料名称" />
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="materialForm.specification" placeholder="请输入规格" />
        </el-form-item>
        <el-form-item label="尺寸" prop="dimensions">
          <el-input v-model="materialForm.dimensions" placeholder="请输入尺寸" />
        </el-form-item>
        <el-form-item label="来料方式" prop="supply_method">
          <el-input v-model="materialForm.supply_method" placeholder="请输入来料方式" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="materialForm.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="最小库存" prop="min_stock">
          <el-input-number v-model="materialForm.min_stock" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预警库存" prop="warning_stock">
          <el-input-number v-model="materialForm.warning_stock" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最大库存" prop="max_stock">
          <el-input-number v-model="materialForm.max_stock" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最近采购价" prop="last_purchase_price">
          <el-input-number
            v-model="materialForm.last_purchase_price"
            :min="0"
            :precision="2"
            :step="0.1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="materialForm.is_active" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="materialForm.notes"
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 入库对话框 -->
    <el-dialog
      v-model="inStockDialogVisible"
      title="材料入库"
      width="500px"
    >
      <el-form
        ref="inStockFormRef"
        :model="movementForm"
        :rules="movementRules"
        label-width="100px"
      >
        <el-form-item label="材料">
          <el-input v-model="selectedMaterial.name" disabled />
        </el-form-item>
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="movementForm.quantity" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="selectedMaterial.unit" disabled />
        </el-form-item>
        <el-form-item label="关联单号" prop="reference_number">
          <el-input v-model="movementForm.reference_number" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="库位" prop="location">
          <el-input v-model="movementForm.location" placeholder="请输入库位" />
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
      title="材料出库"
      width="500px"
    >
      <el-form
        ref="outStockFormRef"
        :model="movementForm"
        :rules="movementRules"
        label-width="100px"
      >
        <el-form-item label="材料">
          <el-input v-model="selectedMaterial.name" disabled />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input :value="`${selectedMaterial.stock} ${selectedMaterial.unit}`" disabled />
        </el-form-item>
        <el-form-item label="出库数量" prop="quantity">
          <el-input-number
            v-model="movementForm.quantity"
            :min="0.01"
            :max="selectedMaterial.stock"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="selectedMaterial.unit" disabled />
        </el-form-item>
        <el-form-item label="关联单号" prop="reference_number">
          <el-input v-model="movementForm.reference_number" placeholder="请输入关联单号" />
        </el-form-item>
        <el-form-item label="库位" prop="location">
          <el-input v-model="movementForm.location" placeholder="请输入库位" />
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh, View, Delete, Minus, Edit } from '@element-plus/icons-vue'
import { getMaterialList, createMaterial, updateMaterial, deleteMaterial, createMaterialMovement } from '@/api/inventory'
import type { Material } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  code: '',
  name: '',
  stock_status: ''
})

// 查询参数
const query = reactive({
  page: 1,
  limit: 10,
  ...searchForm
})

// 材料列表数据
const materialList = ref<Material[]>([])
const loading = ref(false)
const total = ref(0)

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const materialFormRef = ref<FormInstance>()
const materialForm = reactive<Partial<Material>>({
  code: '',
  name: '',
  specification: '',
  dimensions: '',
  supply_method: '',
  unit: '',
  stock: 0,
  min_stock: 0,
  warning_stock: 0,
  max_stock: 0,
  last_purchase_price: undefined,
  notes: '',
  is_active: true
})

// 表单验证规则
const materialRules = {
  code: [
    { required: true, message: '请输入材料编码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ]
}

// 入库/出库相关
const inStockDialogVisible = ref(false)
const outStockDialogVisible = ref(false)
const inStockFormRef = ref<FormInstance>()
const outStockFormRef = ref<FormInstance>()
const selectedMaterial = ref<Material>({} as Material)
const movementForm = reactive({
  material: 0,
  quantity: 0,
  reference_number: '',
  location: '',
  notes: ''
})
const movementRules = {
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '数量必须大于0', trigger: 'blur' }
  ]
}

// 生命周期钩子
onMounted(() => {
  fetchMaterialList()
})

// 获取材料列表
const fetchMaterialList = async () => {
  loading.value = true
  try {
    const res = await getMaterialList({
      page: query.page,
      limit: query.limit,
      code: query.code || undefined,
      name: query.name || undefined,
      stock_status: query.stock_status || undefined
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        materialList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取材料列表失败:', error)
    ElMessage.error('获取材料列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  Object.assign(query, searchForm)
  fetchMaterialList()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  query.page = 1
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  query.limit = val
  fetchMaterialList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchMaterialList()
}

// 添加材料
const handleAddMaterial = () => {
  dialogType.value = 'add'
  Object.keys(materialForm).forEach(key => {
    const k = key as keyof typeof materialForm
    if (k === 'is_active') {
      materialForm[k] = true
    } else if (k === 'stock' || k === 'min_stock' || k === 'warning_stock' || k === 'max_stock') {
      materialForm[k] = 0
    } else if (k === 'last_purchase_price') {
      materialForm[k] = undefined
    } else {
      materialForm[k] = '' as any
    }
  })
  dialogVisible.value = true
}

// 编辑材料
const handleEdit = (row: Material) => {
  dialogType.value = 'edit'
  Object.assign(materialForm, row)
  dialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row: Material) => {
  ElMessageBox.alert(`材料名称: ${row.name}\n材料编码: ${row.code}\n规格: ${row.specification || '无'}\n单位: ${row.unit}\n库存: ${row.stock}\n备注: ${row.notes || '无'}`, '材料详情', {
    confirmButtonText: '确定'
  })
}

// 入库操作
const handleInStock = (row: Material) => {
  selectedMaterial.value = row
  movementForm.material = row.id
  movementForm.quantity = 0
  movementForm.reference_number = ''
  movementForm.location = ''
  movementForm.notes = ''
  inStockDialogVisible.value = true
}

// 出库操作
const handleOutStock = (row: Material) => {
  selectedMaterial.value = row
  movementForm.material = row.id
  movementForm.quantity = 0
  movementForm.reference_number = ''
  movementForm.location = ''
  movementForm.notes = ''
  outStockDialogVisible.value = true
}

// 删除材料
const handleDelete = (row: Material) => {
  ElMessageBox.confirm(
    `确定要删除材料 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteMaterial(row.id)
      ElMessage.success('删除成功')
      fetchMaterialList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!materialFormRef.value) return
  
  await materialFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          await createMaterial(materialForm)
          ElMessage.success('添加成功')
        } else {
          await updateMaterial(materialForm.id as number, materialForm)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchMaterialList()
      } catch (error) {
        console.error(dialogType.value === 'add' ? '添加失败:' : '更新失败:', error)
        ElMessage.error(dialogType.value === 'add' ? '添加失败' : '更新失败')
      }
    }
  })
}

// 提交入库
const submitInStock = async () => {
  if (!inStockFormRef.value) return
  
  await inStockFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await createMaterialMovement({
          material: movementForm.material,
          movement_type: 'in',
          quantity: movementForm.quantity,
          unit: selectedMaterial.value.unit,
          reference_number: movementForm.reference_number,
          location: movementForm.location,
          notes: movementForm.notes
        })
        ElMessage.success('入库成功')
        inStockDialogVisible.value = false
        fetchMaterialList()
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
      if (movementForm.quantity > selectedMaterial.value.stock) {
        ElMessage.error('出库数量不能大于库存数量')
        return
      }
      
      try {
        await createMaterialMovement({
          material: movementForm.material,
          movement_type: 'out',
          quantity: movementForm.quantity,
          unit: selectedMaterial.value.unit,
          reference_number: movementForm.reference_number,
          location: movementForm.location,
          notes: movementForm.notes
        })
        ElMessage.success('出库成功')
        outStockDialogVisible.value = false
        fetchMaterialList()
      } catch (error) {
        console.error('出库失败:', error)
        ElMessage.error('出库失败')
      }
    }
  })
}

// 获取库存状态样式
const getStockStatusClass = (material: Material) => {
  if (material.stock <= material.min_stock) {
    return 'stock-danger'
  } else if (material.stock <= material.warning_stock) {
    return 'stock-warning'
  } else if (material.stock >= material.max_stock) {
    return 'stock-info'
  }
  return 'stock-normal'
}
</script>

<style scoped>
.material-list-container {
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