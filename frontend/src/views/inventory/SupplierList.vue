<template>
  <div class="supplier-list-container">
    <div class="page-header">
      <h2>供应商管理</h2>
      <el-button type="primary" @click="handleAddSupplier">
        <el-icon><Plus /></el-icon>添加供应商
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="供应商编码">
          <el-input v-model="searchForm.code" placeholder="请输入供应商编码" clearable />
        </el-form-item>
        <el-form-item label="供应商名称">
          <el-input v-model="searchForm.name" placeholder="请输入供应商名称" clearable />
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
        :data="supplierList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="供应商编码" min-width="120" />
        <el-table-column prop="name" label="供应商名称" min-width="150" />
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { getSupplierList } from '@/api/inventory'
import type { Supplier } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  code: '',
  name: ''
})

// 查询参数
const query = reactive({
  page: 1,
  limit: 10,
  ...searchForm
})

// 供应商列表数据
const supplierList = ref<Supplier[]>([])
const loading = ref(false)
const total = ref(0)

// 生命周期钩子
onMounted(() => {
  fetchSupplierList()
})

// 获取供应商列表
const fetchSupplierList = async () => {
  loading.value = true
  try {
    const res = await getSupplierList({
      page: query.page,
      limit: query.limit,
      code: query.code || undefined,
      name: query.name || undefined
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        supplierList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    ElMessage.error('获取供应商列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  Object.assign(query, searchForm)
  fetchSupplierList()
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
  fetchSupplierList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchSupplierList()
}

// 添加供应商
const handleAddSupplier = () => {
  ElMessage.info('添加供应商功能待实现')
}

// 编辑供应商
const handleEdit = (_row: Supplier) => {
  ElMessage.info('编辑供应商功能待实现')
}

// 查看详情
const handleViewDetail = (row: Supplier) => {
  ElMessageBox.alert(`供应商名称: ${row.name}\n供应商编码: ${row.code}\n联系人: ${row.contact || '无'}\n联系电话: ${row.phone || '无'}\n地址: ${row.address || '无'}\n备注: ${row.notes || '无'}`, '供应商详情', {
    confirmButtonText: '确定'
  })
}

// 删除供应商
const handleDelete = (row: Supplier) => {
  ElMessageBox.confirm(
    `确定要删除供应商 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.info('删除供应商功能待实现')
  }).catch(() => {})
}
</script>

<style scoped>
.supplier-list-container {
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
</style> 