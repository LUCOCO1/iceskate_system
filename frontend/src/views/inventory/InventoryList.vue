<template>
  <div class="inventory-list-container">
    <div class="page-header">
      <h2>库存管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>导出库存
        </el-button>
        <el-button type="success" @click="handleInventoryCheck">
          <el-icon><Check /></el-icon>库存盘点
        </el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="物料类型">
          <el-select
            v-model="searchForm.inventory_type"
            placeholder="选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="材料" value="material" />
            <el-option label="产品" value="product" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称/编码">
          <el-input
            v-model="searchForm.keyword"
            placeholder="输入名称或编码"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="库位">
          <el-input
            v-model="searchForm.location"
            placeholder="输入库位"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="库存状态">
          <el-select
            v-model="searchForm.stock_status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="正常" value="normal" />
            <el-option label="低库存" value="low" />
            <el-option label="超库存" value="high" />
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
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="材料库存" name="material">
          <el-table :data="inventoryList" border style="width: 100%">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="material_name" label="材料名称" min-width="150" />
            <el-table-column prop="material_code" label="材料编码" width="120" />
            <el-table-column prop="specification" label="规格" min-width="120" />
            <el-table-column label="库存数量" width="120">
              <template #default="scope">
                {{ scope.row.quantity }} {{ scope.row.unit }}
              </template>
            </el-table-column>
            <el-table-column prop="location" label="库位" width="120" />
            <el-table-column label="库存状态" width="100">
              <template #default="scope">
                <el-tag :type="getStockStatusType(scope.row)">
                  {{ getStockStatusLabel(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_update_time" label="最后更新" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleView(scope.row)"
                  text
                >
                  <el-icon><View /></el-icon>详情
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="handleAdjust(scope.row)"
                  text
                >
                  <el-icon><Edit /></el-icon>调整
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="产品库存" name="product">
          <el-table :data="inventoryList" border style="width: 100%">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="product_name" label="产品名称" min-width="150" />
            <el-table-column prop="product_code" label="产品编码" width="120" />
            <el-table-column prop="specification" label="规格" min-width="120" />
            <el-table-column label="库存数量" width="120">
              <template #default="scope">
                {{ scope.row.quantity }} {{ scope.row.unit }}
              </template>
            </el-table-column>
            <el-table-column prop="location" label="库位" width="120" />
            <el-table-column label="库存状态" width="100">
              <template #default="scope">
                <el-tag :type="getStockStatusType(scope.row)">
                  {{ getStockStatusLabel(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_update_time" label="最后更新" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleView(scope.row)"
                  text
                >
                  <el-icon><View /></el-icon>详情
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="handleAdjust(scope.row)"
                  text
                >
                  <el-icon><Edit /></el-icon>调整
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

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
import { Download, Check, Search, Refresh, View, Edit } from '@element-plus/icons-vue'
import { getInventoryList } from '@/api/inventory'
import type { Inventory } from '@/types/inventory'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  inventory_type: 'material',
  keyword: '',
  location: '',
  stock_status: undefined as string | undefined
})

// 当前选中的标签页
const activeTab = ref('material')

// 监听标签页变化
watch(activeTab, (val) => {
  searchForm.inventory_type = val
  handleSearch()
})

// 数据列表
const inventoryList = ref<Inventory[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 获取库存列表
const fetchInventoryList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    const res = await getInventoryList(params)
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data && 'count' in data) {
        inventoryList.value = data.results
        total.value = data.count
      }
    }
  } catch (error) {
    console.error('获取库存列表失败:', error)
    ElMessage.error('获取库存列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchInventoryList()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.location = ''
  searchForm.stock_status = undefined
  currentPage.value = 1
  fetchInventoryList()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchInventoryList()
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchInventoryList()
}

// 标签页切换
const handleTabChange = () => {
  // 标签页切换时重置分页
  currentPage.value = 1
}

// 查看详情
const handleView = (row: any) => {
  // 使用any类型避免类型错误，因为Inventory类型可能与实际返回的数据结构不匹配
  ElMessageBox.alert(`盘点项目: ${row.inventory_type || '未知'}\n名称: ${row.name || '未知'}\nID: ${row.id || '未知'}\n库存数量: ${row.quantity || '无'}\n库位: ${row.location || '无'}\n备注: ${row.notes || '无'}`, '库存详情', {
    confirmButtonText: '确定'
  })
}

// 调整库存
const handleAdjust = (row: Inventory) => {
  ElMessage.info('库存调整功能待实现')
}

// 导出库存
const handleExport = () => {
  ElMessage.info('导出库存功能待实现')
}

// 库存盘点
const handleInventoryCheck = () => {
  ElMessage.info('库存盘点功能待实现')
}

// 获取库存状态标签类型
const getStockStatusType = (row: any) => {
  if (row.quantity <= (row.min_stock || 0)) {
    return 'danger'
  } else if (row.quantity >= (row.max_stock || Infinity)) {
    return 'warning'
  }
  return 'success'
}

// 获取库存状态标签文本
const getStockStatusLabel = (row: any) => {
  if (row.quantity <= (row.min_stock || 0)) {
    return '低库存'
  } else if (row.quantity >= (row.max_stock || Infinity)) {
    return '超库存'
  }
  return '正常'
}

onMounted(() => {
  fetchInventoryList()
})
</script>

<style scoped>
.inventory-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
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