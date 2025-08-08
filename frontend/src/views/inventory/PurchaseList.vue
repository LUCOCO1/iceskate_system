<template>
  <div class="purchase-list-container">
    <div class="page-header">
      <h2>采购管理</h2>
      <el-button type="primary" @click="handleAddPurchase">
        <el-icon><Plus /></el-icon>新建采购单
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="采购单号">
          <el-input v-model="searchForm.purchase_number" placeholder="请输入采购单号" clearable />
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="searchForm.supplier" placeholder="请选择供应商" clearable filterable>
            <el-option
              v-for="item in supplierOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待入库" value="pending" />
            <el-option label="已入库" value="received" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
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
        :data="purchaseList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="purchase_number" label="采购单号" min-width="150" />
        <el-table-column prop="supplier_name" label="供应商" min-width="150" />
        <el-table-column prop="purchase_date" label="采购日期" width="120" />
        <el-table-column prop="delivery_date" label="交货日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleViewDetail(scope.row)"
            >
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleEdit(scope.row)"
              :disabled="!['draft', 'pending'].includes(scope.row.status)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleConfirmReceive(scope.row)"
              :disabled="scope.row.status !== 'pending'"
            >
              <el-icon><Check /></el-icon>确认入库
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="handleCancelReceive(scope.row)"
              :disabled="scope.row.status !== 'received'"
            >
              <el-icon><Close /></el-icon>取消入库
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.status !== 'draft'"
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="handlePrint(scope.row)"
            >
              <el-icon><Printer /></el-icon>打印
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
import { Plus, Search, Refresh, View, Edit, Delete, Check, Close, Printer } from '@element-plus/icons-vue'
import { getPurchaseList, deletePurchase, getSupplierList, confirmPurchase, cancelPurchaseReceive } from '@/api/inventory'
import type { MaterialPurchase, Supplier } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  purchase_number: '',
  supplier: '',
  status: ''
})

// 查询参数
const query = reactive({
  page: 1,
  limit: 10,
  ...searchForm
})

// 采购单列表数据
const purchaseList = ref<MaterialPurchase[]>([])
const loading = ref(false)
const total = ref(0)

// 供应商选项
const supplierOptions = ref<Supplier[]>([])
const loadingSuppliers = ref(false)

// 生命周期钩子
onMounted(() => {
  fetchPurchaseList()
  fetchSuppliers()
})

// 获取采购单列表
const fetchPurchaseList = async () => {
  loading.value = true
  try {
    const res = await getPurchaseList({
      page: query.page,
      limit: query.limit,
      purchase_number: query.purchase_number || undefined,
      supplier: query.supplier || undefined,
      status: query.status || undefined
    })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        purchaseList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取采购单列表失败:', error)
    ElMessage.error('获取采购单列表失败')
  } finally {
    loading.value = false
  }
}

// 获取供应商列表
const fetchSuppliers = async () => {
  loadingSuppliers.value = true
  try {
    const res = await getSupplierList({ limit: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        supplierOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取供应商列表失败:', error)
  } finally {
    loadingSuppliers.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  Object.assign(query, searchForm)
  fetchPurchaseList()
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
  fetchPurchaseList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchPurchaseList()
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'draft': 'info',
    'pending': 'warning',
    'received': 'success',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'draft': '草稿',
    'pending': '待入库',
    'received': '已入库',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return map[status] || '未知'
}

// 新建采购单
const handleAddPurchase = () => {
  router.push('/inventory/purchase-create')
}

// 编辑采购单
const handleEdit = (row: MaterialPurchase) => {
  router.push(`/inventory/purchase-edit/${row.id}`)
}

// 查看详情
const handleViewDetail = (row: MaterialPurchase) => {
  router.push(`/inventory/purchase-edit/${row.id}`)
}

// 删除采购单
const handleDelete = (row: MaterialPurchase) => {
  ElMessageBox.confirm(
    `确定要删除采购单 "${row.purchase_number}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deletePurchase(row.id)
      ElMessage.success('删除成功')
      fetchPurchaseList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 确认入库
const handleConfirmReceive = (row: MaterialPurchase) => {
  ElMessageBox.confirm(
    `确定要将采购单 "${row.purchase_number}" 确认入库吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await confirmPurchase(row.id)
      ElMessage.success('确认入库成功')
      fetchPurchaseList()
    } catch (error: any) {
      console.error('确认入库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`确认入库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('确认入库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 取消入库
const handleCancelReceive = (row: MaterialPurchase) => {
  ElMessageBox.confirm(
    `确定要取消采购单 "${row.purchase_number}" 的入库状态吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelPurchaseReceive(row.id)
      ElMessage.success('取消入库成功')
      fetchPurchaseList()
    } catch (error: any) {
      console.error('取消入库失败:', error)
      // 显示后端返回的具体错误信息
      if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(`取消入库失败: ${error.response.data.error}`)
      } else {
        ElMessage.error('取消入库失败，请稍后重试')
      }
    }
  }).catch(() => {})
}

// 打印采购单
const handlePrint = (row: MaterialPurchase) => {
  window.open(`/api/inventory/purchase/${row.id}/print/`, '_blank')
}
</script>

<style scoped>
.purchase-list-container {
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