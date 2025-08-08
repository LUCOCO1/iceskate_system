<template>
  <div class="material-movement-list-container">
    <div class="page-header">
      <h2>材料移动记录</h2>
      <el-button type="primary" @click="handleAddMovement">
        <el-icon><Plus /></el-icon>新增移动记录
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="材料名称">
          <el-select
            v-model="searchForm.material"
            placeholder="选择材料"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="item in materialOptions"
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
            <el-option label="调整" value="adjust" />
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
        <el-table-column prop="movement_date" label="移动日期" width="150" />
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column prop="specification" label="规格" min-width="120" />
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
        <el-table-column prop="source_info" label="来源信息" width="180" />
        <el-table-column prop="reference_number" label="关联单号" width="150" />
        <el-table-column prop="batch" label="批次信息" width="150">
          <template #default="scope">
            <span v-if="scope.row.batch">批次: {{ scope.row.batch_number || scope.row.batch }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleView()"
            >
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Delete } from '@element-plus/icons-vue'
import { getMaterialMovementList, deleteMaterialMovement, getMaterialList } from '@/api/inventory'
import type { MaterialMovement, Material } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  material: undefined as number | undefined,
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

// 材料选项
const materialOptions = ref<Material[]>([])

// 数据列表
const movementList = ref<MaterialMovement[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 获取材料列表
const fetchMaterials = async () => {
  try {
    const res = await getMaterialList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        materialOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取材料列表失败:', error)
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
    
    const res = await getMaterialMovementList(params)
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
  router.push('/inventory/material-movement-form')
}

// 查看详情
const handleView = () => {
  ElMessage.info('查看详情功能待实现')
}

// 删除记录
const handleDelete = (row: MaterialMovement) => {
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
      await deleteMaterialMovement(row.id)
      ElMessage.success('删除成功')
      fetchMovementList()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 判断是否可以删除
const canDelete = (row: MaterialMovement) => {
  // 只允许删除用户手动创建的记录，不允许删除系统生成的记录（如采购入库）
  return !row.purchase; // 如果关联了采购单，则不允许删除
}

// 获取移动类型标签样式
const getMovementTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'in': 'success',
    'out': 'danger',
    'adjust': 'warning'
  }
  return map[type] || 'info'
}

// 获取移动类型显示文本
const getMovementTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    'in': '入库',
    'out': '出库',
    'adjust': '调整'
  }
  return map[type] || type
}

onMounted(() => {
  fetchMaterials()
  fetchMovementList()
})
</script>

<style scoped>
.material-movement-list-container {
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

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-button) {
  min-width: 80px;
  margin: 2px;
  font-weight: normal;
}

.el-button--primary,
.el-button--success,
.el-button--warning,
.el-button--danger,
.el-button--info {
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