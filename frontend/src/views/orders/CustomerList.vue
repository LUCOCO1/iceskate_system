<template>
  <div class="customer-list-container">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="handleAddCustomer" :icon="Plus">
        新建客户
      </el-button>
    </div>

    <!-- 搜索卡片 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="客户编码">
          <el-input 
            v-model="searchForm.code" 
            placeholder="请输入客户编码" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入客户名称" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.is_active" 
            placeholder="请选择状态" 
            clearable 
            style="width: 150px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 客户表格 -->
    <el-card class="table-card">
      <el-table 
        :data="customerList" 
        v-loading="loading" 
        stripe 
        border
        style="width: 100%"
      >
        <el-table-column prop="code" label="客户编码" width="120" />
        <el-table-column prop="name" label="客户名称" width="200" />
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button 
              :type="scope.row.is_active ? 'warning' : 'success'" 
              link 
              @click="handleToggleStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="danger" 
              link 
              @click="handleDelete(scope.row)"
            >
              删除
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
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 客户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新建客户' : '编辑客户'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="customerFormRef"
        :model="customerForm"
        :rules="customerRules"
        label-width="100px"
      >
        <el-form-item label="客户编码" prop="code">
          <el-input v-model="customerForm.code" placeholder="请输入客户编码" />
        </el-form-item>
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="customerForm.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="customerForm.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="customerForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="customerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input 
            v-model="customerForm.address" 
            type="textarea" 
            :rows="3"
            placeholder="请输入地址" 
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="customerForm.is_active" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input 
            v-model="customerForm.notes" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注" 
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCustomerForm">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { 
  getCustomerList, 
  createCustomer, 
  updateCustomer, 
  deleteCustomer 
} from '@/api/orders'
import type { Customer, CustomerForm } from '@/types/orders'

// 搜索表单
const searchForm = reactive({
  code: '',
  name: '',
  is_active: null as boolean | null
})

// 表格数据
const loading = ref(false)
const customerList = ref<Customer[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const customerFormRef = ref<FormInstance>()
const customerForm = reactive<CustomerForm>({
  code: '',
  name: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  notes: '',
  is_active: true
})

// 表单验证规则
const customerRules = {
  code: [
    { required: true, message: '请输入客户编码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchCustomerList()
})

// 获取客户列表
const fetchCustomerList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      code: searchForm.code || undefined,
      name: searchForm.name || undefined,
      is_active: searchForm.is_active
    }

    const res: any = await getCustomerList(params)

    if (res) {
      if ('results' in res && 'count' in res) {
        customerList.value = res.results
        total.value = res.count as number
      } else if (Array.isArray(res)) {
        customerList.value = res
        total.value = res.length
      }
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchCustomerList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.code = ''
  searchForm.name = ''
  searchForm.is_active = null
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchCustomerList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchCustomerList()
}

// 新建客户
const handleAddCustomer = () => {
  dialogType.value = 'add'
  resetCustomerForm()
  dialogVisible.value = true
}

// 编辑客户
const handleEdit = (row: Customer) => {
  dialogType.value = 'edit'
  Object.assign(customerForm, row)
  dialogVisible.value = true
}

// 切换状态
const handleToggleStatus = async (row: Customer) => {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}客户"${row.name}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateCustomer(row.id, { is_active: !row.is_active })
    ElMessage.success(`${action}成功`)
    fetchCustomerList()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  }
}

// 删除客户
const handleDelete = async (row: Customer) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${row.name}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    fetchCustomerList()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 重置客户表单
const resetCustomerForm = () => {
  customerForm.code = ''
  customerForm.name = ''
  customerForm.contact = ''
  customerForm.phone = ''
  customerForm.email = ''
  customerForm.address = ''
  customerForm.notes = ''
  customerForm.is_active = true
}

// 提交客户表单
const submitCustomerForm = async () => {
  if (!customerFormRef.value) return
  
  try {
    await customerFormRef.value.validate()
    
    if (dialogType.value === 'add') {
      await createCustomer(customerForm)
      ElMessage.success('客户创建成功')
    } else {
      // 编辑模式需要客户ID
      const customerId = customerList.value.find(c => 
        c.code === customerForm.code && c.name === customerForm.name
      )?.id
      if (customerId) {
        await updateCustomer(customerId, customerForm)
        ElMessage.success('客户更新成功')
      }
    }
    
    dialogVisible.value = false
    fetchCustomerList()
  } catch (error: any) {
    console.error('提交客户表单失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(`提交失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('提交失败，请检查表单数据')
    }
  }
}
</script>

<style scoped>
.customer-list-container {
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

.dialog-footer {
  text-align: right;
}
</style> 