<template>
  <div class="equipment-list-container">
    <div class="page-header">
      <h2>设备管理</h2>
      <el-button type="primary" @click="handleAddEquipment">
        <el-icon><Plus /></el-icon>新增设备
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="设备名称">
          <el-input v-model="searchForm.name" placeholder="请输入设备名称" clearable />
        </el-form-item>
        <el-form-item label="设备编号">
          <el-input v-model="searchForm.code" placeholder="请输入设备编号" clearable />
        </el-form-item>
        <el-form-item label="所属工序">
          <el-select v-model="searchForm.process_step" placeholder="请选择工序" clearable>
            <el-option
              v-for="item in processStepOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="设备状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="normal" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="故障" value="malfunction" />
            <el-option label="报废" value="scrapped" />
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
        :data="equipmentList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="设备名称" min-width="150" />
        <el-table-column prop="code" label="设备编号" width="120" />
        <el-table-column prop="model" label="设备型号" width="120" />
        <el-table-column prop="process_step_name" label="所属工序" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="daily_capacity" label="日产能" width="100" />
        <el-table-column prop="purchase_date" label="购入日期" width="120" />
        <el-table-column label="维护日期" width="180">
          <template #default="scope">
            <div v-if="scope.row.last_maintenance">上次: {{ scope.row.last_maintenance }}</div>
            <div v-if="scope.row.next_maintenance">下次: {{ scope.row.next_maintenance }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(scope.row)"
              :disabled="scope.row.status === 'scrapped'"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleMaintenanceRecord(scope.row)"
            >
              <el-icon><Tools /></el-icon>维护记录
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.status === 'scrapped'"
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 设备表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增设备' : '编辑设备'"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备编号" prop="code">
          <el-input v-model="form.code" placeholder="请输入设备编号" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="设备型号" prop="model">
          <el-input v-model="form.model" placeholder="请输入设备型号" />
        </el-form-item>
        <el-form-item label="所属工序" prop="process_step">
          <el-select v-model="form.process_step" placeholder="请选择工序" style="width: 100%">
            <el-option
              v-for="item in processStepOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="设备状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="故障" value="malfunction" />
            <el-option label="报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="日产能" prop="daily_capacity">
          <el-input-number v-model="form.daily_capacity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="购入日期" prop="purchase_date">
          <el-date-picker
            v-model="form.purchase_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="上次维护日期">
          <el-date-picker
            v-model="form.last_maintenance"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="下次维护日期">
          <el-date-picker
            v-model="form.next_maintenance"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 维护记录对话框 -->
    <el-dialog
      v-model="maintenanceDialogVisible"
      title="记录设备维护"
      width="500px"
    >
      <el-form :model="maintenanceForm" label-width="120px">
        <el-form-item label="设备名称">
          <el-input v-model="currentEquipment.name" disabled />
        </el-form-item>
        <el-form-item label="设备编号">
          <el-input v-model="currentEquipment.code" disabled />
        </el-form-item>
        <el-form-item label="维护日期" prop="maintenance_date">
          <el-date-picker
            v-model="maintenanceForm.maintenance_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="下次维护日期" prop="next_maintenance">
          <el-date-picker
            v-model="maintenanceForm.next_maintenance"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="维护内容" prop="notes">
          <el-input
            v-model="maintenanceForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入维护内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="maintenanceDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitMaintenanceRecord">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Refresh, 
  Edit, 
  Delete, 
  Tools 
} from '@element-plus/icons-vue'
import { 
  getEquipmentList, 
  getEquipmentDetail,
  createEquipment,
  updateEquipment,
  deleteEquipment
} from '@/api/production'
import { getProcessStepList } from '@/api/production'
import type { Equipment, ProcessStep } from '@/types/production'

// 搜索表单
const searchForm = reactive({
  name: '',
  code: '',
  process_step: '',
  status: ''
})

// 查询参数
const query = reactive({
  page: 1,
  page_size: 10,
  ...searchForm
})

// 设备列表数据
const equipmentList = ref<Equipment[]>([])
const loading = ref(false)
const total = ref(0)

// 工序选项
const processStepOptions = ref<ProcessStep[]>([])
const loadingProcessSteps = ref(false)

// 表单对话框
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref()
const form = reactive<Partial<Equipment>>({
  name: '',
  code: '',
  model: '',
  status: 'normal',
  process_step: undefined,
  daily_capacity: 0,
  purchase_date: '',
  last_maintenance: undefined,
  next_maintenance: undefined,
  notes: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  model: [{ required: true, message: '请输入设备型号', trigger: 'blur' }],
  process_step: [{ required: true, message: '请选择所属工序', trigger: 'change' }],
  status: [{ required: true, message: '请选择设备状态', trigger: 'change' }],
  daily_capacity: [{ required: true, message: '请输入日产能', trigger: 'blur' }],
  purchase_date: [{ required: true, message: '请选择购入日期', trigger: 'change' }]
}

// 维护记录对话框
const maintenanceDialogVisible = ref(false)
const currentEquipment = ref<Equipment>({} as Equipment)
const maintenanceForm = reactive({
  maintenance_date: new Date().toISOString().split('T')[0],
  next_maintenance: '',
  notes: ''
})

// 生命周期钩子
onMounted(() => {
  fetchEquipmentList()
  fetchProcessSteps()
})

// 获取设备列表
const fetchEquipmentList = async () => {
  loading.value = true
  try {
    const res = await getEquipmentList({
      page: query.page,
      page_size: query.page_size,
      name: query.name || undefined,
      code: query.code || undefined,
      process_step: query.process_step || undefined,
      status: query.status || undefined
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        equipmentList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取设备列表失败:', error)
    ElMessage.error('获取设备列表失败')
  } finally {
    loading.value = false
  }
}

// 获取工序列表
const fetchProcessSteps = async () => {
  loadingProcessSteps.value = true
  try {
    const res = await getProcessStepList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        processStepOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取工序列表失败:', error)
  } finally {
    loadingProcessSteps.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  Object.assign(query, searchForm)
  fetchEquipmentList()
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
  query.page_size = val
  fetchEquipmentList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchEquipmentList()
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'normal': 'success',
    'maintenance': 'warning',
    'malfunction': 'danger',
    'scrapped': 'info'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'normal': '正常',
    'maintenance': '维护中',
    'malfunction': '故障',
    'scrapped': '报废'
  }
  return map[status] || '未知'
}

// 新增设备
const handleAddEquipment = () => {
  dialogType.value = 'add'
  // 重置表单
  form.name = ''
  form.code = ''
  form.model = ''
  form.status = 'normal'
  form.process_step = undefined
  form.daily_capacity = 0
  form.purchase_date = new Date().toISOString().split('T')[0]
  form.last_maintenance = undefined
  form.next_maintenance = undefined
  form.notes = ''
  dialogVisible.value = true
}

// 编辑设备
const handleEdit = async (row: Equipment) => {
  dialogType.value = 'edit'
  try {
    const res = await getEquipmentDetail(row.id)
    if (res && typeof res === 'object') {
      const data = res.data || res
      Object.assign(form, data)
    }
    dialogVisible.value = true
  } catch (error) {
    console.error('获取设备详情失败:', error)
    ElMessage.error('获取设备详情失败')
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          await createEquipment(form)
          ElMessage.success('新增设备成功')
        } else {
          await updateEquipment(form.id as number, form)
          ElMessage.success('编辑设备成功')
        }
        dialogVisible.value = false
        fetchEquipmentList()
      } catch (error: any) {
        console.error(dialogType.value === 'add' ? '新增设备失败:' : '编辑设备失败:', error)
        if (error.response && error.response.data && error.response.data.error) {
          ElMessage.error(`操作失败: ${error.response.data.error}`)
        } else {
          ElMessage.error('操作失败，请稍后重试')
        }
      }
    }
  })
}

// 删除设备
const handleDelete = (row: Equipment) => {
  ElMessageBox.confirm(
    `确定要删除设备 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteEquipment(row.id)
      ElMessage.success('删除成功')
      fetchEquipmentList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 维护记录
const handleMaintenanceRecord = (row: Equipment) => {
  currentEquipment.value = row
  maintenanceForm.maintenance_date = new Date().toISOString().split('T')[0]
  maintenanceForm.next_maintenance = ''
  maintenanceForm.notes = ''
  maintenanceDialogVisible.value = true
}

// 提交维护记录
const submitMaintenanceRecord = async () => {
  if (!maintenanceForm.maintenance_date) {
    ElMessage.warning('请选择维护日期')
    return
  }

  try {
    await updateEquipment(currentEquipment.value.id, {
      id: currentEquipment.value.id,
      last_maintenance: maintenanceForm.maintenance_date,
      next_maintenance: maintenanceForm.next_maintenance || null,
      status: 'normal', // 维护后恢复正常状态
      notes: currentEquipment.value.notes + 
        (currentEquipment.value.notes ? '\n' : '') + 
        `维护记录(${maintenanceForm.maintenance_date}): ${maintenanceForm.notes}`
    })
    ElMessage.success('维护记录添加成功')
    maintenanceDialogVisible.value = false
    fetchEquipmentList()
  } catch (error: any) {
    console.error('维护记录添加失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(`维护记录添加失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('维护记录添加失败，请稍后重试')
    }
  }
}
</script>

<style scoped>
.equipment-list-container {
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

.page-header h2 {
  color: #000;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-form {
  padding: 10px 0;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 操作按钮文字样式 */
:deep(.el-button) {
  min-width: 90px;
  margin: 2px;
  font-weight: normal; /* 不加粗 */
}

/* 普通按钮文字颜色为黑色 */
.el-button:not(.el-button--primary, .el-button--success, .el-button--warning, .el-button--danger, .el-button--info):not(.is-disabled) {
  color: #000;
}

/* 更简洁的方式设置所有主题按钮的文字颜色为黑色 */
.el-table .el-button--primary,
.el-table .el-button--success, 
.el-table .el-button--warning,
.el-table .el-button--danger,
.el-table .el-button--info {
  color: #000 !important;
}

.el-table .el-button span,
.el-table .el-button i {
  color: #000;
}

.el-tag {
  font-weight: bold;
  padding: 6px 10px;
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

:deep(.el-form-item__label) {
  color: #000;
  font-weight: 500;
}

:deep(.el-input__inner) {
  color: #000;
}

:deep(.el-pagination) {
  color: #000;
}

:deep(.el-pagination button) {
  color: #000;
}
</style> 