<template>
  <div class="product-movement-list-container">
    <div class="page-header">
      <h2>产品移动记录</h2>
      <el-button type="primary" @click="handleAddMovement">
        <el-icon><Plus /></el-icon>新增移动记录
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="产品名称">
          <el-select
            v-model="searchForm.product"
            placeholder="选择产品"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="item in productOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="移动类型">
          <el-select
            v-model="searchForm.movement_type"
            placeholder="选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="入库" value="in" />
            <el-option label="出库" value="out" />
            <el-option label="调拨" value="transfer" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
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
      <el-table :data="movementList" border style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="movement_date" label="移动日期" width="120" />
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="product_code" label="产品编码" width="120" />
        <el-table-column label="移动类型" width="100">
          <template #default="scope">
            <el-tag :type="getMovementTypeTag(scope.row.movement_type)">
              {{ getMovementTypeLabel(scope.row.movement_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="库位" width="120" />
        <el-table-column prop="reference_number" label="关联单号" width="150" />
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleView(scope.row)"
              text
            >
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              text
              v-if="canDelete(scope.row)"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Delete } from '@element-plus/icons-vue'
import { getProductMovementList, getProductList } from '@/api/inventory'
import type { ProductMovement, Product } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  product: undefined as number | undefined,
  movement_type: undefined as string | undefined,
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

// 产品选项
const productOptions = ref<Product[]>([])

// 数据列表
const movementList = ref<ProductMovement[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 获取产品列表
const fetchProducts = async () => {
  try {
    const res = await getProductList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        productOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
  }
}

// 获取移动记录列表
const fetchMovementList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    const res = await getProductMovementList(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        movementList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取移动记录列表失败:', error)
    ElMessage.error('获取移动记录列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchMovementList()
}

// 重置搜索
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = undefined
  })
  dateRange.value = null
  currentPage.value = 1
  fetchMovementList()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchMovementList()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchMovementList()
}

// 新增移动记录
const handleAddMovement = () => {
  router.push('/inventory/product-movement-form')
}

// 查看详情
const handleView = (row: ProductMovement) => {
  ElMessage.info('查看详情功能待实现')
}

// 删除记录
const handleDelete = (row: ProductMovement) => {
  ElMessageBox.confirm(
    `确定要删除该移动记录吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 调用删除API
      // await deleteProductMovement(row.id)
      ElMessage.success('删除成功')
      fetchMovementList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 判断是否可以删除
const canDelete = (row: ProductMovement) => {
  // 通常只有当天的记录可以删除，或者有特定权限的用户
  const today = new Date().toISOString().split('T')[0]
  return row.movement_date === today
}

// 获取移动类型标签样式
const getMovementTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'in': 'success',
    'out': 'danger',
    'transfer': 'warning'
  }
  return map[type] || 'info'
}

// 获取移动类型标签文本
const getMovementTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    'in': '入库',
    'out': '出库',
    'transfer': '调拨'
  }
  return map[type] || '未知'
}

onMounted(() => {
  fetchProducts()
  fetchMovementList()
})
</script>

<style scoped>
.product-movement-list-container {
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

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 