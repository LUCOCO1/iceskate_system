<template>
  <div class="process-schedule-list-container">
    <div class="page-header">
      <h2>工序排程</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加排程
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="生产订单">
          <el-input v-model="searchForm.production_order" placeholder="请输入生产订单号" clearable />
        </el-form-item>
        <el-form-item label="工序">
          <el-select v-model="searchForm.process" placeholder="选择工序" clearable>
            <el-option
              v-for="process in processOptions"
              :key="process.id"
              :label="process.name"
              :value="process.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="待开始" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="延迟" value="delayed" />
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
        :data="scheduleList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="production_order_number" label="生产订单号" min-width="150" />
        <el-table-column prop="process_name" label="工序名称" min-width="120" />
        <el-table-column prop="planned_start_time" label="计划开始时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.planned_start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="planned_end_time" label="计划结束时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.planned_end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_start_time" label="实际开始时间" width="160">
          <template #default="scope">
            {{ scope.row.actual_start_time ? formatDateTime(scope.row.actual_start_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_end_time" label="实际结束时间" width="160">
          <template #default="scope">
            {{ scope.row.actual_end_time ? formatDateTime(scope.row.actual_end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="equipment_name" label="设备" min-width="120" />
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
      :title="dialogType === 'add' ? '添加工序排程' : '编辑工序排程'"
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
        <el-form-item label="工序" prop="process">
          <el-select v-model="form.process" placeholder="选择工序" style="width: 100%">
            <el-option
              v-for="process in processOptions"
              :key="process.id"
              :label="process.name"
              :value="process.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始时间" prop="planned_start_time">
          <el-date-picker
            v-model="form.planned_start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="计划结束时间" prop="planned_end_time">
          <el-date-picker
            v-model="form.planned_end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="设备" prop="equipment">
          <el-select v-model="form.equipment" placeholder="选择设备" style="width: 100%">
            <el-option
              v-for="equipment in equipmentOptions"
              :key="equipment.id"
              :label="equipment.name"
              :value="equipment.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
            <el-option label="待开始" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="延迟" value="delayed" />
          </el-select>
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
  getProcessScheduleList, 
  createProcessSchedule,
  updateProcessSchedule,
  deleteProcessSchedule,
  getProcessStepList,
  getProductionOrderList,
  getEquipmentList
} from '@/api/production'

// 搜索表单
const searchForm = reactive({
  production_order: '',
  process: '',
  status: ''
})

// 表格数据
const loading = ref(false)
const scheduleList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 选项数据
const processOptions = ref<any[]>([])
const productionOrderOptions = ref<any[]>([])
const equipmentOptions = ref<any[]>([])

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  production_order: '',
  process: '',
  planned_start_time: '',
  planned_end_time: '',
  equipment: '',
  status: 'pending',
  notes: ''
})

// 表单验证规则
const rules = {
  production_order: [
    { required: true, message: '请选择生产订单', trigger: 'change' }
  ],
  process: [
    { required: true, message: '请选择工序', trigger: 'change' }
  ],
  planned_start_time: [
    { required: true, message: '请选择计划开始时间', trigger: 'change' }
  ],
  planned_end_time: [
    { required: true, message: '请选择计划结束时间', trigger: 'change' }
  ]
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'pending':
      return 'info'
    case 'in_progress':
      return 'warning'
    case 'completed':
      return 'success'
    case 'delayed':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 生命周期钩子
onMounted(() => {
  fetchScheduleList()
  fetchOptions()
})

// 获取选项数据
const fetchOptions = async () => {
  try {
    const [processRes, orderRes, equipmentRes] = await Promise.all([
      getProcessStepList({ page_size: 1000 }),
      getProductionOrderList({ page_size: 1000 }),
      getEquipmentList({ page_size: 1000 })
    ])
    
    processOptions.value = processRes.data?.results || []
    productionOrderOptions.value = orderRes.data?.results || []
    equipmentOptions.value = equipmentRes.data?.results || []
  } catch (error) {
    console.error('获取选项数据失败:', error)
  }
}

// 获取排程列表
const fetchScheduleList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.production_order) params.production_order = searchForm.production_order
    if (searchForm.process) params.process = searchForm.process
    if (searchForm.status) params.status = searchForm.status
    
    const res = await getProcessScheduleList(params)
    
    if (res && res.data && typeof res.data === 'object') {
      const data = res.data as any
      if ('results' in data && 'count' in data) {
        scheduleList.value = Array.isArray(data.results) ? data.results : []
        total.value = Number(data.count) || 0
      }
    }
  } catch (error) {
    console.error('获取工序排程列表失败:', error)
    ElMessage.error('获取工序排程列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchScheduleList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.production_order = ''
  searchForm.process = ''
  searchForm.status = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchScheduleList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchScheduleList()
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
  form.process = row.process
  form.planned_start_time = row.planned_start_time
  form.planned_end_time = row.planned_end_time
  form.equipment = row.equipment
  form.status = row.status
  form.notes = row.notes || ''
  dialogVisible.value = true
}

// 删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除工序排程 "${row.process_name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProcessSchedule(row.id)
      ElMessage.success('删除成功')
      fetchScheduleList()
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
  form.process = ''
  form.planned_start_time = ''
  form.planned_end_time = ''
  form.equipment = ''
  form.status = 'pending'
  form.notes = ''
}

// 提交表单
const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const formData = {
          production_order: form.production_order,
          process: form.process,
          planned_start_time: form.planned_start_time,
          planned_end_time: form.planned_end_time,
          equipment: form.equipment,
          status: form.status,
          notes: form.notes
        }
        
        if (dialogType.value === 'add') {
          await createProcessSchedule(formData)
          ElMessage.success('添加成功')
        } else {
          await updateProcessSchedule(form.id, formData)
          ElMessage.success('更新成功')
        }
        
        dialogVisible.value = false
        fetchScheduleList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }
  })
}
</script>

<style scoped>
.process-schedule-list-container {
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