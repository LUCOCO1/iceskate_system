<template>
  <div class="material-requirement-list-container">
    <div class="page-header">
      <h2>材料需求</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加需求
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="生产订单">
          <el-input v-model="searchForm.production_order" placeholder="请输入生产订单号" clearable />
        </el-form-item>
        <el-form-item label="物料">
          <el-select v-model="searchForm.material" placeholder="选择物料" clearable>
            <el-option
              v-for="material in materialOptions"
              :key="material.id"
              :label="material.name"
              :value="material.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="待领料" value="pending" />
            <el-option label="部分领料" value="partial" />
            <el-option label="已完成" value="completed" />
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
        :data="requirementList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="production_order_number" label="生产订单号" min-width="150" />
        <el-table-column prop="material_name" label="物料名称" min-width="120" />
        <el-table-column prop="material_specification" label="规格" min-width="100" />
        <el-table-column prop="required_quantity" label="需求数量" width="100" align="right">
          <template #default="scope">
            {{ scope.row.required_quantity }}{{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="allocated_quantity" label="已分配数量" width="110" align="right">
          <template #default="scope">
            {{ scope.row.allocated_quantity || 0 }}{{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="used_quantity" label="实际用量" width="100" align="right">
          <template #default="scope">
            {{ scope.row.used_quantity || 0 }}{{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="getProgressPercentage(scope.row)" 
              :color="getProgressColor(scope.row)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="required_date" label="需求日期" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.required_date) }}
          </template>
        </el-table-column>
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
      :title="dialogType === 'add' ? '添加材料需求' : '编辑材料需求'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="生产订单" prop="production_order">
          <el-select v-model="form.production_order" placeholder="选择生产订单" style="width: 100%">
            <el-option
              v-for="order in productionOrderOptions"
              :key="order.id"
              :label="order.order_number"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material">
          <el-select v-model="form.material" placeholder="选择物料" style="width: 100%">
            <el-option
              v-for="material in materialOptions"
              :key="material.id"
              :label="`${material.name} (${material.specification})`"
              :value="material.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="需求数量" prop="required_quantity">
          <el-input-number 
            v-model="form.required_quantity" 
            :min="0" 
            :precision="2"
            style="width: 200px" 
          />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="请输入单位" style="width: 200px" />
        </el-form-item>
        <el-form-item label="需求日期" prop="required_date">
          <el-date-picker
            v-model="form.required_date"
            type="date"
            placeholder="选择需求日期"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { 
  getMaterialRequirementList, 
  createMaterialRequirement,
  updateMaterialRequirement,
  deleteMaterialRequirement,
  getProductionOrderList,
} from '@/api/production'
import { getMaterialList } from '@/api/inventory'

// 搜索表单
const searchForm = reactive({
  production_order: '',
  material: '',
  status: ''
})

// 表格数据
const loading = ref(false)
const requirementList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 选项数据
const materialOptions = ref<any[]>([])
const productionOrderOptions = ref<any[]>([])

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  production_order: '',
  material: '',
  required_quantity: 0,
  unit: '个',
  required_date: '',
  notes: ''
})

// 表单验证规则
const rules = {
  production_order: [
    { required: true, message: '请选择生产订单', trigger: 'change' }
  ],
  material: [
    { required: true, message: '请选择物料', trigger: 'change' }
  ],
  required_quantity: [
    { required: true, message: '请输入需求数量', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  required_date: [
    { required: true, message: '请选择需求日期', trigger: 'change' }
  ]
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'partial':
      return 'primary'
    case 'completed':
      return 'success'
    default:
      return 'info'
  }
}

// 获取进度百分比
const getProgressPercentage = (row: any) => {
  if (!row.required_quantity || row.required_quantity === 0) return 0
  const allocated = row.allocated_quantity || 0
  return Math.min(Math.round((allocated / row.required_quantity) * 100), 100)
}

// 获取进度条颜色
const getProgressColor = (row: any) => {
  const percentage = getProgressPercentage(row)
  if (percentage >= 100) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

// 生命周期钩子
onMounted(() => {
  fetchRequirementList()
  fetchOptions()
})

// 获取选项数据
const fetchOptions = async () => {
  try {
    const [orderRes, materialRes] = await Promise.all([
      getProductionOrderList({ page_size: 1000 }),
      getMaterialList({ page_size: 1000 })
    ])
    
    // 因为axios拦截器已经返回了response.data，所以res就是实际的数据
    productionOrderOptions.value = orderRes?.results || []
    
    // 从后端获取真实的材料数据
    if (materialRes) {
      const materials = materialRes.results || materialRes
      materialOptions.value = materials.map((item: any) => ({
        id: item.id,
        name: item.name,
        specification: item.specification || ''
      }))
    }
  } catch (error) {
    console.error('获取选项数据失败:', error)
  }
}

// 获取需求列表
const fetchRequirementList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.production_order) params.production_order = searchForm.production_order
    if (searchForm.material) params.material = searchForm.material
    if (searchForm.status) params.status = searchForm.status
    
    const res = await getMaterialRequirementList(params)
    console.log('材料需求API响应:', res)
    
    // 因为axios拦截器已经返回了response.data，所以res就是实际的数据
    if (res && typeof res === 'object') {
      if ('results' in res && 'count' in res) {
        requirementList.value = Array.isArray(res.results) ? res.results : []
        total.value = Number(res.count) || 0
        console.log('设置后的列表数据:', requirementList.value)
        console.log('数据总数:', total.value)
      } else {
        console.warn('响应数据格式不正确，没有results或count字段')
      }
    } else {
      console.warn('响应数据为空或格式不正确')
    }
  } catch (error) {
    console.error('获取材料需求列表失败:', error)
    ElMessage.error('获取材料需求列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchRequirementList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.production_order = ''
  searchForm.material = ''
  searchForm.status = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchRequirementList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchRequirementList()
}

// 添加
const handleAdd = () => {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.production_order = row.production_order
  form.material = row.material
  form.required_quantity = row.required_quantity
  form.unit = row.unit
  form.required_date = row.required_date
  form.notes = row.notes || ''
  dialogVisible.value = true
}

// 删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除材料需求 "${row.material_name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteMaterialRequirement(row.id)
      ElMessage.success('删除成功')
      fetchRequirementList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 重置表单
const resetForm = () => {
  form.id = 0
  form.production_order = ''
  form.material = ''
  form.required_quantity = 0
  form.unit = '个'
  form.required_date = ''
  form.notes = ''
}

// 提交表单
const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const formData = {
          production_order: form.production_order,
          material: form.material,
          required_quantity: form.required_quantity,
          unit: form.unit,
          required_date: form.required_date,
          notes: form.notes
        }
        
        if (dialogType.value === 'add') {
          await createMaterialRequirement(formData)
          ElMessage.success('添加成功')
        } else {
          await updateMaterialRequirement(form.id, formData)
          ElMessage.success('更新成功')
        }
        
        dialogVisible.value = false
        fetchRequirementList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }
  })
}
</script>

<style scoped>
.material-requirement-list-container {
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