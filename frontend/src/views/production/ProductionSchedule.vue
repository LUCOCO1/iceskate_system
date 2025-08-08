<template>
  <div class="production-schedule-container">
    <div class="page-header">
      <h2>生产排程</h2>
      <div class="action-buttons">
        <el-button type="primary" @click="handleExportSchedule">
          <el-icon><Download /></el-icon>导出排程
        </el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="生产单号">
          <el-input 
            v-model="searchForm.order_number" 
            placeholder="请输入生产单号" 
            clearable 
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input 
            v-model="searchForm.product_name" 
            placeholder="请输入产品名称" 
            clearable 
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="工序">
          <el-select 
            v-model="searchForm.process" 
            placeholder="选择工序"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option 
              v-for="item in processOptions" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="待生产" value="pending" />
            <el-option label="生产中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已延期" value="delayed" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="scheduleList" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="order_number" label="生产单号" min-width="150" />
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="process_name" label="工序" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="planned_start_time" label="计划开始时间" width="160" />
        <el-table-column prop="planned_end_time" label="计划结束时间" width="160" />
        <el-table-column prop="actual_start_time" label="实际开始时间" width="160">
          <template #default="scope">
            {{ scope.row.actual_start_time || '尚未开始' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_end_time" label="实际结束时间" width="160">
          <template #default="scope">
            {{ scope.row.actual_end_time || '尚未完成' }}
          </template>
        </el-table-column>
        <el-table-column prop="equipment_name" label="使用设备" width="120" />
        <el-table-column prop="operator_name" label="操作人员" width="120" />
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleUpdateSchedule(scope.row)"
              :disabled="scope.row.status === 'completed'"
            >
              <el-icon><Edit /></el-icon>更新
            </el-button>
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

    <!-- 甘特图视图 -->
    <el-card class="gantt-card">
      <template #header>
        <div class="card-header">
          <span>排程甘特图</span>
          <el-radio-group v-model="timeScale" size="small">
            <el-radio-button label="day">日</el-radio-button>
            <el-radio-button label="week">周</el-radio-button>
            <el-radio-button label="month">月</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="gantt-container">
        <!-- 这里放置甘特图组件，可以使用第三方库如 v-gantt-chart 等 -->
        <div class="gantt-placeholder">
          <el-empty description="甘特图视图开发中..." />
        </div>
      </div>
    </el-card>

    <!-- 更新排程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="更新排程"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="生产单号">
          <el-input v-model="uiInfo.order_number" disabled />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="uiInfo.product_name" disabled />
        </el-form-item>
        <el-form-item label="工序">
          <el-input v-model="form.process_name" disabled />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待生产" value="pending" />
            <el-option label="生产中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已延期" value="delayed" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始时间" prop="planned_start_time">
          <el-date-picker
            v-model="form.planned_start_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="计划结束时间" prop="planned_end_time">
          <el-date-picker
            v-model="form.planned_end_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="实际开始时间" prop="actual_start_time">
          <el-date-picker
            v-model="form.actual_start_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>
        <el-form-item label="实际结束时间" prop="actual_end_time">
          <el-date-picker
            v-model="form.actual_end_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>
        <el-form-item label="使用设备" prop="equipment">
          <el-select 
            v-model="form.equipment" 
            filterable 
            clearable
            placeholder="选择设备"
            style="width: 100%"
          >
            <el-option
              v-for="item in equipmentOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人员" prop="operator">
          <el-select 
            v-model="form.operator" 
            filterable 
            clearable
            placeholder="选择操作人员"
            style="width: 100%"
          >
            <el-option
              v-for="item in operatorOptions"
              :key="item.id"
              :label="item.username"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, FormInstance } from 'element-plus'
import { Download, Search, Refresh, Edit } from '@element-plus/icons-vue'
import { 
  getProcessScheduleList, 
  updateProcessSchedule 
} from '@/api/production'
import { getProcessStepList } from '@/api/production'
import { getEquipmentList } from '@/api/production'
import { getUserList } from '@/api/system'
import type { ProcessSchedule, ProcessStep } from '@/types/production'

// 搜索表单
const searchForm = reactive({
  order_number: '',
  product_name: '',
  process: undefined as number | undefined,
  status: undefined as string | undefined,
  start_date: undefined as string | undefined,
  end_date: undefined as string | undefined
})

// 日期范围
const dateRange = ref<[string, string] | null>(null)

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val) {
    searchForm.start_date = val[0]
    searchForm.end_date = val[1]
  } else {
    searchForm.start_date = undefined
    searchForm.end_date = undefined
  }
})

// 数据列表
const scheduleList = ref<ProcessSchedule[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 甘特图时间尺度
const timeScale = ref('day')

// 工序选项
const processOptions = ref<ProcessStep[]>([])

// 设备选项
const equipmentOptions = ref<any[]>([])

// 操作人员选项
const operatorOptions = ref<any[]>([])

// 对话框
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  id: undefined as number | undefined,
  production_order: undefined as number | undefined,
  process: undefined as number | undefined,
  process_name: '',
  planned_start_time: '',
  planned_end_time: '',
  actual_start_time: undefined as string | undefined,
  actual_end_time: undefined as string | undefined,
  status: 'pending' as 'pending' | 'in_progress' | 'completed' | 'delayed',
  equipment: undefined as number | undefined,
  equipment_name: undefined as string | undefined,
  operator: undefined as number | undefined,
  operator_name: undefined as string | undefined,
  notes: ''
})

// 临时存储一些UI显示信息
const uiInfo = reactive({
  order_number: '',
  product_name: ''
})

// 表单验证规则
const rules = {
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  planned_start_time: [
    { required: true, message: '请选择计划开始时间', trigger: 'change' }
  ],
  planned_end_time: [
    { required: true, message: '请选择计划结束时间', trigger: 'change' }
  ]
}

// 获取排程列表
const fetchScheduleList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    const res = await getProcessScheduleList(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        scheduleList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取排程列表失败:', error)
    ElMessage.error('获取排程列表失败')
  } finally {
    loading.value = false
  }
}

// 获取工序列表
const fetchProcessOptions = async () => {
  try {
    const res = await getProcessStepList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        processOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取工序列表失败:', error)
  }
}

// 获取设备列表
const fetchEquipmentOptions = async () => {
  try {
    const res = await getEquipmentList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        equipmentOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

// 获取操作人员列表
const fetchOperatorOptions = async () => {
  try {
    const res = await getUserList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        operatorOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取操作人员列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchScheduleList()
}

// 重置搜索
const handleReset = () => {
  // 单独处理每种类型的属性
  searchForm.order_number = ''
  searchForm.product_name = ''
  searchForm.process = undefined
  searchForm.status = undefined
  searchForm.start_date = undefined
  searchForm.end_date = undefined
  
  dateRange.value = null
  currentPage.value = 1
  fetchScheduleList()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchScheduleList()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchScheduleList()
}

// 更新排程
const handleUpdateSchedule = (row: ProcessSchedule) => {
  // 设置表单数据
  form.id = row.id
  form.production_order = row.production_order
  form.process = row.process
  form.process_name = row.process_name || ''
  form.status = row.status
  form.planned_start_time = row.planned_start_time || ''
  form.planned_end_time = row.planned_end_time || ''
  form.actual_start_time = row.actual_start_time
  form.actual_end_time = row.actual_end_time
  form.equipment = row.equipment
  form.equipment_name = row.equipment_name
  form.operator = row.operator
  form.operator_name = row.operator_name
  form.notes = row.notes || ''
  
  // 设置 UI 显示信息
  uiInfo.order_number = row.production_order ? `订单-${row.production_order}` : '';
  uiInfo.product_name = row.process_name || '';
  
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    // 验证时间
    if (form.planned_end_time && form.planned_start_time) {
      const startTime = new Date(form.planned_start_time)
      const endTime = new Date(form.planned_end_time)
      if (endTime <= startTime) {
        ElMessage.warning('计划结束时间必须晚于计划开始时间')
        return
      }
    }
    
    if (form.actual_end_time && form.actual_start_time) {
      const startTime = new Date(form.actual_start_time)
      const endTime = new Date(form.actual_end_time)
      if (endTime <= startTime) {
        ElMessage.warning('实际结束时间必须晚于实际开始时间')
        return
      }
    }
    
    try {
      if (form.id !== undefined) {
        await updateProcessSchedule(form.id, form)
        ElMessage.success('更新成功')
        dialogVisible.value = false
        fetchScheduleList()
      }
    } catch (error: any) {
      console.error('更新失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`更新失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('更新失败，请稍后重试')
      }
    }
  })
}

// 导出排程
const handleExportSchedule = () => {
  ElMessage.info('导出功能开发中...')
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'in_progress': 'success',
    'completed': 'primary',
    'delayed': 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待生产',
    'in_progress': '生产中',
    'completed': '已完成',
    'delayed': '已延期'
  }
  return map[status] || '未知'
}

onMounted(() => {
  Promise.all([
    fetchProcessOptions(),
    fetchEquipmentOptions(),
    fetchOperatorOptions()
  ]).then(() => {
    fetchScheduleList()
  })
})
</script>

<style scoped>
.production-schedule-container {
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
  margin: 0;
}

.search-card,
.table-card,
.gantt-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #000;
  font-weight: 600;
}

.gantt-container {
  height: 500px;
  overflow: auto;
}

.gantt-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

:deep(.el-form-item__label) {
  color: #000;
  font-weight: 500;
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

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: #000;
}

.el-tag {
  font-weight: bold;
  padding: 6px 10px;
}

:deep(.el-button) {
  min-width: 80px;
  font-weight: normal;
  margin: 2px;
}
</style> 