<template>
  <div class="process-step-list-container">
    <div class="page-header">
      <h2>工序管理</h2>
      <el-button type="primary" @click="handleAddProcessStep">
        <el-icon><Plus /></el-icon>新增工序
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="工序名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入工序名称" 
            clearable 
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="工序编码">
          <el-input 
            v-model="searchForm.code" 
            placeholder="请输入工序编码" 
            clearable 
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="瓶颈工序">
          <el-select 
            v-model="searchForm.is_bottleneck" 
            placeholder="请选择" 
            clearable 
            style="width: 120px"
          >
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
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
      <el-table :data="processStepList" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="工序名称" min-width="150" />
        <el-table-column prop="code" label="工序编码" width="120" />
        <el-table-column prop="sequence" label="顺序" width="80" sortable />
        <el-table-column label="日产能" width="120">
          <template #default="scope">
            {{ scope.row.daily_capacity || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="是否瓶颈" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_bottleneck ? 'danger' : 'info'">
              {{ scope.row.is_bottleneck ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联设备" width="120">
          <template #default="scope">
            {{ scope.row.equipment_count || 0 }} 台
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(scope.row)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.equipment_count > 0"
            >
              <el-icon><Delete /></el-icon>删除
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

    <!-- 工序表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增工序' : '编辑工序'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        style="max-width: 460px"
      >
        <el-form-item label="工序名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入工序名称" />
        </el-form-item>
        <el-form-item label="工序编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入工序编码" />
        </el-form-item>
        <el-form-item label="顺序" prop="sequence">
          <el-input-number 
            v-model="form.sequence" 
            :min="1" 
            :precision="0" 
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="日产能" prop="daily_capacity">
          <el-input-number 
            v-model="form.daily_capacity" 
            :min="0" 
            :precision="0" 
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="是否瓶颈" prop="is_bottleneck">
          <el-switch v-model="form.is_bottleneck" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（非必填）"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { 
  getProcessStepList, 
  getProcessStepDetail, 
  createProcessStep, 
  updateProcessStep, 
  deleteProcessStep 
} from '@/api/production'
import type { ProcessStep } from '@/types/production'

// 搜索表单
const searchForm = reactive({
  name: '',
  code: '',
  is_bottleneck: undefined as boolean | undefined
})

// 数据列表
const processStepList = ref<ProcessStep[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 对话框
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = reactive<Partial<ProcessStep>>({
  name: '',
  code: '',
  sequence: 1,
  daily_capacity: 0,
  is_bottleneck: false,
  notes: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入工序名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入工序编码', trigger: 'blur' }
  ],
  sequence: [
    { required: true, message: '请输入顺序', trigger: 'change' },
    { type: 'number', min: 1, message: '顺序必须大于0', trigger: 'change' }
  ],
  daily_capacity: [
    { required: true, message: '请输入日产能', trigger: 'change' },
    { type: 'number', min: 0, message: '日产能不能为负数', trigger: 'change' }
  ]
}

// 获取工序列表
const fetchProcessStepList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    const res = await getProcessStepList(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        processStepList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取工序列表失败:', error)
    ElMessage.error('获取工序列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchProcessStepList()
}

// 重置搜索
const handleReset = () => {
  searchForm.name = ''
  searchForm.code = ''
  searchForm.is_bottleneck = undefined
  currentPage.value = 1
  fetchProcessStepList()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchProcessStepList()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchProcessStepList()
}

// 新增工序
const handleAddProcessStep = () => {
  dialogType.value = 'add'
  form.name = ''
  form.code = ''
  form.sequence = 1
  form.daily_capacity = 0
  form.is_bottleneck = false
  form.notes = ''
  dialogVisible.value = true
}

// 编辑工序
const handleEdit = async (row: ProcessStep) => {
  dialogType.value = 'edit'
  try {
    const res = await getProcessStepDetail(row.id)
    if (res && typeof res === 'object') {
      const data = res.data || res
      Object.assign(form, data)
    }
    dialogVisible.value = true
  } catch (error) {
    console.error('获取工序详情失败:', error)
    ElMessage.error('获取工序详情失败')
  }
}

// 删除工序
const handleDelete = (row: ProcessStep) => {
  ElMessageBox.confirm(
    `确定要删除工序 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProcessStep(row.id)
      ElMessage.success('删除成功')
      fetchProcessStepList()
    } catch (error: any) {
      console.error('删除失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`删除失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('删除失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    try {
      if (dialogType.value === 'add') {
        await createProcessStep(form)
        ElMessage.success('添加成功')
      } else {
        await updateProcessStep(form.id as number, form)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      fetchProcessStepList()
    } catch (error: any) {
      console.error('保存失败:', error)
      if (error.response?.data?.error) {
        ElMessage.error(`保存失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('保存失败，请稍后重试')
      }
    }
  })
}

onMounted(() => {
  fetchProcessStepList()
})
</script>

<style scoped>
.process-step-list-container {
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

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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