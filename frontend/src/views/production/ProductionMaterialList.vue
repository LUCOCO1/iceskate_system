<template>
  <div class="production-material-list-container">
    <div class="page-header">
      <h2>生产用料记录</h2>
      <el-alert type="info" show-icon :closable="false">
        生产用料记录在开始生产时自动生成，记录实际使用的材料批次和数量
      </el-alert>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="生产订单">
          <el-input v-model="searchForm.production_order" placeholder="请输入生产订单号" clearable />
        </el-form-item>
        <el-form-item label="材料批次">
          <el-input v-model="searchForm.material_batch" placeholder="请输入批次号" clearable />
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
        <el-table-column prop="production_order_number" label="生产订单号" min-width="150" />
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column prop="batch_number" label="批次号" min-width="120" />
        <el-table-column prop="quantity_used" label="使用数量" width="120">
          <template #default="scope">
            {{ scope.row.quantity_used }}{{ scope.row.unit }}
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getProductionMaterialList } from '@/api/production'

// 搜索表单
const searchForm = reactive({
  production_order: '',
  material_batch: ''
})

// 表格数据
const loading = ref(false)
const materialList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 生命周期钩子
onMounted(() => {
  fetchMaterialList()
})

// 获取用料列表
const fetchMaterialList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.production_order) params.production_order = searchForm.production_order
    if (searchForm.material_batch) params.material_batch = searchForm.material_batch
    
    const res = await getProductionMaterialList(params)
    console.log('生产用料API响应:', res)
    
    // 因为axios拦截器已经返回了response.data，所以res就是实际的数据
    if (res?.results) {
      materialList.value = res.results
      total.value = res.count || 0
      console.log('设置后的列表数据:', materialList.value)
      console.log('数据总数:', total.value)
    } else {
      console.warn('响应数据格式不正确:', res)
    }
  } catch (error) {
    console.error('获取生产用料列表失败:', error)
    ElMessage.error('获取生产用料列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchMaterialList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.production_order = ''
  searchForm.material_batch = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchMaterialList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchMaterialList()
}
</script>

<style scoped>
.production-material-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.page-header h2 {
  color: #000;
  font-weight: 600;
  margin: 0;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.table-card {
  background-color: #fff;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: right;
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
</style>