<template>
  <div class="material-batch-list-container">
    <div class="page-header">
      <h2>材料批次</h2>
      <div class="header-buttons">
        <el-button type="primary" @click="handleAddBatch">
          <el-icon><Plus /></el-icon>新建批次
        </el-button>
        <el-button v-if="batchList && batchList.length === 0" type="success" @click="createTestData">
          <el-icon><Setting /></el-icon>创建测试数据
        </el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="批次号">
          <el-input v-model="searchForm.batch_number" placeholder="请输入批次号" clearable />
        </el-form-item>
        <el-form-item label="材料">
          <el-select v-model="searchForm.material" placeholder="请选择材料" clearable filterable>
            <el-option
              v-for="item in materialOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="normal" />
            <el-option label="已过期" value="expired" />
            <el-option label="已耗尽" value="depleted" />
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
        :data="batchList"
        border
        style="width: 100%"
        :empty-text="batchList && batchList.length === 0 ? '暂无材料批次记录，通常在材料采购时自动创建' : '没有数据'"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="batch_number" label="批次号" min-width="150" />
        <el-table-column prop="material_name" label="材料" min-width="150" />
        <el-table-column prop="initial_quantity" label="初始数量" width="120" />
        <el-table-column prop="remaining_quantity" label="剩余数量" width="120" />
        <el-table-column label="数量进度" width="150">
          <template #default="scope">
            <el-progress 
              :percentage="calculateProgress(scope.row)" 
              :color="getProgressColor(scope.row)"
              :show-text="false"
            />
            <span class="progress-text">
              {{ scope.row.remaining_quantity }}/{{ scope.row.initial_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="production_date" label="生产日期" width="120" />
        <el-table-column prop="expiry_date" label="有效期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleViewDetail(scope.row)"
            >
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button 
              v-if="scope.row.status === 'normal'"
              type="success" 
              size="small" 
              @click="handleEdit(scope.row)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.remaining_quantity > 0"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { 
  Plus, 
  Search, 
  Refresh, 
  View, 
  Edit, 
  Delete,
  Setting
} from '@element-plus/icons-vue'
import { 
  getMaterialBatchList, 
  deleteMaterialBatch, 
  getMaterialList 
} from '@/api/inventory'
import type { MaterialBatch, MaterialBatchQuery } from '@/types/batch'
import type { Material } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  batch_number: '',
  material: '',
  status: ''
})

// 查询参数
const query = reactive<MaterialBatchQuery>({
  page: 1,
  page_size: 10
})

// 批次列表数据
const batchList = ref<MaterialBatch[]>([])
const loading = ref(false)
const total = ref(0)

// 材料选项
const materialOptions = ref<Material[]>([])

// 生命周期钩子
onMounted(() => {
  fetchBatchList()
  fetchMaterials()
})

// 获取批次列表
const fetchBatchList = async () => {
  loading.value = true
  try {
    const params: any = {
      ...query,
      ...searchForm
    }
    
    // 移除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    console.log('请求材料批次列表参数:', params)
    const response = await getMaterialBatchList(params)
    console.log('材料批次列表API完整响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应keys:', Object.keys(response || {}))
    
    // 处理不同的响应格式
    let actualData = response
    
    // 如果是axios响应格式，提取data字段
    if (response && typeof response === 'object' && 'data' in response) {
      actualData = response.data
      console.log('提取axios的data字段:', actualData)
      console.log('data字段类型:', typeof actualData)
      console.log('data字段键:', Object.keys(actualData || {}))
    }
    
    if (actualData && typeof actualData === 'object') {
      let batchData
      let totalCount = 0
      
      // 处理不同的响应格式
      if (actualData.results && Array.isArray(actualData.results)) {
        // DRF分页格式
        console.log('检测到DRF分页格式')
        batchData = actualData.results
        totalCount = actualData.count || 0
      } else if (Array.isArray(actualData)) {
        // 直接数组格式
        console.log('检测到直接数组格式')
        batchData = actualData
        totalCount = actualData.length
      } else if (actualData.data && Array.isArray(actualData.data)) {
        // 嵌套的data数组
        console.log('检测到嵌套data数组格式')
        batchData = actualData.data
        totalCount = actualData.data.length
      } else {
        console.warn('未知的批次数据格式，尝试直接使用:', actualData)
        batchData = [actualData]
        totalCount = 1
      }
      
      console.log('提取的批次数据:', batchData)
      console.log('批次数据类型:', typeof batchData)
      console.log('是否为数组:', Array.isArray(batchData))
      console.log('批次数据长度:', Array.isArray(batchData) ? batchData.length : '不是数组')
      
      if (Array.isArray(batchData)) {
        batchList.value = batchData
        total.value = totalCount
        console.log('设置批次列表数据:', batchList.value)
        console.log('设置总数:', total.value)
        
        if (batchData.length > 0) {
          console.log('第一条批次记录:', batchData[0])
        } else {
          console.log('批次数据为空数组')
        }
      } else {
        console.warn('批次数据不是有效数组:', batchData)
        batchList.value = []
        total.value = 0
      }
    } else {
      console.error('批次数据响应无效:', actualData)
      batchList.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('获取批次列表失败:', error)
    batchList.value = []
    total.value = 0
    
    if (error.response) {
      console.error('API错误响应:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      })
      ElMessage.error(`获取批次列表失败: ${error.response.status} - ${error.response.statusText}`)
    } else if (error.request) {
      console.error('网络请求失败:', error.request)
      ElMessage.error('网络请求失败，请检查后端服务是否启动')
    } else {
      console.error('其他错误:', error.message)
      ElMessage.error(`获取批次列表失败: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

// 获取材料列表
const fetchMaterials = async () => {
  try {
    console.log('获取材料选项...')
    const response = await getMaterialList({ page_size: 1000 })
    console.log('材料列表API响应:', response)
    
    // 处理不同的响应格式
    let actualData = response
    
    // 如果是axios响应格式，提取data字段
    if (response && typeof response === 'object' && 'data' in response) {
      actualData = response.data
      console.log('提取axios的data字段:', actualData)
    }
    
    if (actualData && typeof actualData === 'object') {
      let materialData
      
      // 处理不同的响应格式
      if (actualData.results && Array.isArray(actualData.results)) {
        // DRF分页格式
        console.log('检测到DRF分页格式')
        materialData = actualData.results
      } else if (Array.isArray(actualData)) {
        // 直接数组格式
        console.log('检测到直接数组格式')
        materialData = actualData
      } else {
        console.warn('未知的材料数据格式:', actualData)
        materialData = []
      }
      
      console.log('提取的材料数据:', materialData)
      console.log('材料数据长度:', Array.isArray(materialData) ? materialData.length : '不是数组')
      
      if (Array.isArray(materialData)) {
        materialOptions.value = materialData
        console.log('材料选项数量:', materialOptions.value.length)
      } else {
        materialOptions.value = []
      }
    } else {
      materialOptions.value = []
    }
  } catch (error) {
    console.error('获取材料列表失败:', error)
    materialOptions.value = []
  }
}

// 搜索处理
const handleSearch = () => {
  query.page = 1
  fetchBatchList()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  query.page = 1
  fetchBatchList()
}

// 分页处理
const handleSizeChange = (val: number) => {
  query.page_size = val
  fetchBatchList()
}

const handleCurrentChange = (val: number) => {
  query.page = val
  fetchBatchList()
}

// 计算进度百分比
const calculateProgress = (row: MaterialBatch) => {
  if (row.initial_quantity <= 0) return 0
  return Math.round((row.remaining_quantity / row.initial_quantity) * 100)
}

// 获取进度条颜色
const getProgressColor = (row: MaterialBatch) => {
  const percentage = calculateProgress(row)
  if (percentage <= 20) return '#f56c6c' // 红色
  if (percentage <= 50) return '#e6a23c' // 橙色
  return '#67c23a' // 绿色
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'normal': 'success',
    'expired': 'danger',
    'depleted': 'info'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'normal': '正常',
    'expired': '已过期',
    'depleted': '已耗尽'
  }
  return map[status] || '未知'
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 新建批次
const handleAddBatch = () => {
  ElMessage.info('新建批次功能通常在材料采购时自动创建')
}

// 编辑批次
const handleEdit = (row: MaterialBatch) => {
  ElMessage.info(`编辑批次 ${row.batch_number} - 功能待开发`)
}

// 查看详情
const handleViewDetail = (row: MaterialBatch) => {
  router.push({
    name: 'MaterialBatchDetail',
    params: { id: row.id.toString() }
  })
}

// 删除批次
const handleDelete = (row: MaterialBatch) => {
  if (row.remaining_quantity > 0) {
    ElMessage.warning('批次还有剩余库存，无法删除')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除批次 "${row.batch_number}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteMaterialBatch(row.id)
      ElMessage.success('删除成功')
      fetchBatchList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 创建测试数据
const createTestData = () => {
  ElMessage.info('材料批次通常在采购单创建时自动生成。\n您可以：\n1. 创建采购单来生成真实的材料批次\n2. 或者等待真实的采购业务产生批次数据')
}
</script>

<style scoped>
.material-batch-list-container {
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

.header-buttons {
  display: flex;
  gap: 10px;
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

.progress-text {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

:deep(.el-button) {
  min-width: 80px;
  margin: 2px;
  font-weight: normal;
}

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

:deep(.el-progress-bar__outer) {
  height: 8px;
}
</style> 