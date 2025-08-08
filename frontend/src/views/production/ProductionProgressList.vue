<template>
  <div class="production-progress-list-container">
    <div class="page-header">
      <h2>生产进度</h2>
      <div class="header-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>记录进度
        </el-button>
        <el-button v-if="progressList && progressList.length === 0" type="success" @click="createTestData">
          <el-icon><Setting /></el-icon>创建测试数据
        </el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="生产订单">
          <el-input v-model="searchForm.production_order" placeholder="请输入生产订单号" clearable />
        </el-form-item>
        <el-form-item label="记录日期">
          <el-date-picker
            v-model="searchForm.record_date"
            type="date"
            placeholder="选择记录日期"
            clearable
          />
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
        :data="progressList"
        border
        style="width: 100%"
        :empty-text="emptyText"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="production_order_number" label="生产订单号" min-width="150" />
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="record_date" label="记录日期" width="120" />
        <el-table-column prop="quantity" label="本次数量" width="120" />
        <el-table-column prop="accumulated_quantity" label="累计数量" width="120" />
        <el-table-column prop="progress" label="进度(%)" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="Number(scope.row.progress)" 
              :stroke-width="8"
              :show-text="false"
            />
            <span style="margin-left: 8px;">{{ scope.row.progress }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="can_edit" label="可修改" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.can_edit ? 'success' : 'info'">
              {{ scope.row.can_edit ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              @click="handleEdit(scope.row)"
              :disabled="!scope.row.can_edit"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleCancel(scope.row)"
              :disabled="!scope.row.can_edit"
            >
              取消
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '记录生产进度' : '编辑生产进度'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="生产订单" prop="production_order">
          <el-select v-model="form.production_order" placeholder="选择生产订单" style="width: 100%">
            <el-option
              v-for="order in productionOrderOptions"
              :key="order.id"
              :label="order.order_number"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择记录日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="本次数量" prop="quantity">
          <el-input-number
            v-model="form.quantity"
            :min="0.01"
            :precision="2"
            style="width: 100%"
            placeholder="请输入本次完成数量"
          />
        </el-form-item>
        <el-form-item label="实际效率" prop="actual_efficiency">
          <el-input-number
            v-model="form.actual_efficiency"
            :min="0"
            :max="200"
            :precision="2"
            style="width: 100%"
            placeholder="请输入实际效率(%)"
          />
          <div style="color: #999; font-size: 12px; margin-top: 4px;">
            实际完成数量/计划数量的百分比
          </div>
        </el-form-item>
        <el-form-item label="延迟原因" prop="delay_reason">
          <el-input v-model="form.delay_reason" type="textarea" :rows="2" placeholder="如有延迟请说明原因" />
        </el-form-item>
        <el-form-item label="质量问题数量" prop="quality_issues">
          <el-input-number
            v-model="form.quality_issues"
            :min="0"
            style="width: 100%"
            placeholder="质量问题数量"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh, Setting } from '@element-plus/icons-vue'
import { 
  getProductionProgressList, 
  getProductionOrderList,
  createProductionProgress,
  updateProductionProgress,
  cancelProgress
} from '@/api/production'

// 搜索表单
const searchForm = reactive({
  production_order: '',
  record_date: ''
})

// 表格数据
const loading = ref(false)
const progressList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 选项数据
const productionOrderOptions = ref<any[]>([])

// 计算属性
const emptyText = computed(() => {
  if (progressList.value && progressList.value.length === 0) {
    return '暂无生产进度记录，点击上方"记录进度"按钮开始记录'
  }
  return '没有数据'
})

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  production_order: '',
  record_date: '',
  quantity: 0,
  actual_efficiency: 100,
  delay_reason: '',
  quality_issues: 0,
  notes: ''
})

// 表单验证规则
const rules = {
  production_order: [
    { required: true, message: '请选择生产订单', trigger: 'change' }
  ],
  record_date: [
    { required: true, message: '请选择记录日期', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入本次数量', trigger: 'blur' }
  ],
  actual_efficiency: [
    { required: true, message: '请输入实际效率', trigger: 'blur' }
  ]
}

// 生命周期钩子
onMounted(() => {
  fetchProgressList()
  fetchOptions()
})

// 获取选项数据
const fetchOptions = async () => {
  try {
    console.log('获取生产订单选项...')
    const orderRes = await getProductionOrderList({ page_size: 1000 })
    console.log('生产订单API响应:', orderRes)
    
    // 处理不同的响应格式
    let actualData = orderRes
    
    // 如果是axios响应格式，提取data字段
    if (orderRes && typeof orderRes === 'object' && 'data' in orderRes) {
      actualData = orderRes.data
      console.log('提取axios的data字段:', actualData)
    }
    
    if (actualData && typeof actualData === 'object') {
      let orderData
      
      // 处理不同的响应格式
      if (actualData.results && Array.isArray(actualData.results)) {
        // DRF分页格式
        console.log('检测到DRF分页格式')
        orderData = actualData.results
      } else if (Array.isArray(actualData)) {
        // 直接数组格式
        console.log('检测到直接数组格式')
        orderData = actualData
      } else {
        console.warn('未知的订单数据格式:', actualData)
        orderData = []
      }
      
      console.log('提取的订单数据:', orderData)
      console.log('订单数据长度:', Array.isArray(orderData) ? orderData.length : '不是数组')
      
      if (Array.isArray(orderData)) {
        // 只选择生产中的订单用于进度记录
        const inProgressOrders = orderData.filter(order => 
          order.status === 'in_production' || order.status === 'material_ready'
        )
        productionOrderOptions.value = inProgressOrders
        console.log('可记录进度的订单数量:', productionOrderOptions.value.length)
      } else {
        productionOrderOptions.value = []
      }
    } else {
      productionOrderOptions.value = []
    }
  } catch (error) {
    console.error('获取选项数据失败:', error)
    productionOrderOptions.value = []
  }
}

// 获取进度列表
const fetchProgressList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.production_order) params.production_order = searchForm.production_order
    if (searchForm.record_date) params.record_date = searchForm.record_date
    
    console.log('请求生产进度列表参数:', params)
    const res = await getProductionProgressList(params)
    console.log('生产进度列表API完整响应:', res)
    console.log('响应类型:', typeof res)
    console.log('响应keys:', Object.keys(res || {}))
    
    // 处理不同的响应格式
    let actualData = res
    
    // 如果是axios响应格式，提取data字段
    if (res && typeof res === 'object' && 'data' in res) {
      actualData = res.data
      console.log('提取axios的data字段:', actualData)
      console.log('data字段类型:', typeof actualData)
      console.log('data字段键:', Object.keys(actualData || {}))
    }
    
    if (actualData && typeof actualData === 'object') {
      let progressData
      let totalCount = 0
      
      // 处理不同的响应格式
      if (actualData.results && Array.isArray(actualData.results)) {
        // DRF分页格式
        console.log('检测到DRF分页格式')
        progressData = actualData.results
        totalCount = actualData.count || 0
      } else if (Array.isArray(actualData)) {
        // 直接数组格式
        console.log('检测到直接数组格式')
        progressData = actualData
        totalCount = actualData.length
      } else if (actualData.data && Array.isArray(actualData.data)) {
        // 嵌套的data数组
        console.log('检测到嵌套data数组格式')
        progressData = actualData.data
        totalCount = actualData.data.length
      } else {
        console.warn('未知的进度数据格式，尝试直接使用:', actualData)
        // 尝试将对象转换为数组（可能是单个对象）
        progressData = [actualData]
        totalCount = 1
      }
      
      console.log('提取的进度数据:', progressData)
      console.log('进度数据类型:', typeof progressData)
      console.log('是否为数组:', Array.isArray(progressData))
      console.log('进度数据长度:', Array.isArray(progressData) ? progressData.length : '不是数组')
      
      if (Array.isArray(progressData)) {
        progressList.value = progressData
        total.value = totalCount
        console.log('设置进度列表数据:', progressList.value)
        console.log('设置总数:', total.value)
        
        if (progressData.length > 0) {
          console.log('第一条进度记录:', progressData[0])
        } else {
          console.log('进度数据为空数组')
        }
      } else {
        console.warn('进度数据不是有效数组:', progressData)
        progressList.value = []
        total.value = 0
      }
    } else {
      console.error('进度数据响应无效:', actualData)
      progressList.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('获取生产进度列表失败:', error)
    progressList.value = []
    total.value = 0
    
    if (error.response) {
      console.error('API错误响应:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      })
      ElMessage.error(`获取生产进度列表失败: ${error.response.status} - ${error.response.statusText}`)
    } else if (error.request) {
      console.error('网络请求失败:', error.request)
      ElMessage.error('网络请求失败，请检查后端服务是否启动')
    } else {
      console.error('其他错误:', error.message)
      ElMessage.error(`获取生产进度列表失败: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchProgressList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.production_order = ''
  searchForm.record_date = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchProgressList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchProgressList()
}

// 添加
const handleAdd = () => {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.production_order = row.production_order
  form.record_date = row.record_date
  form.quantity = row.quantity
  form.actual_efficiency = row.actual_efficiency || 100
  form.delay_reason = row.delay_reason || ''
  form.quality_issues = row.quality_issues || 0
  form.notes = row.notes || ''
  dialogVisible.value = true
}

// 取消进度记录
const handleCancel = (row: any) => {
  ElMessageBox.confirm(
    `确定要取消进度记录 "${row.production_order_number}" 的记录吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelProgress(row.id)
      ElMessage.success('取消成功')
      fetchProgressList()
    } catch (error) {
      console.error('取消失败:', error)
      ElMessage.error('取消失败')
    }
  })
}

// 重置表单
const resetForm = () => {
  form.id = 0
  form.production_order = ''
  form.record_date = ''
  form.quantity = 0
  form.actual_efficiency = 100
  form.delay_reason = ''
  form.quality_issues = 0
  form.notes = ''
}

// 提交表单
const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const formData = {
          production_order: form.production_order,
          record_date: form.record_date,
          quantity: form.quantity,
          actual_efficiency: form.actual_efficiency,
          delay_reason: form.delay_reason,
          quality_issues: form.quality_issues,
          notes: form.notes
        }
        
        if (dialogType.value === 'add') {
          await createProductionProgress(formData)
          ElMessage.success('添加成功')
        } else {
          await updateProductionProgress(form.id, formData)
          ElMessage.success('更新成功')
        }
        
        dialogVisible.value = false
        fetchProgressList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }
  })
}

// 创建测试数据
const createTestData = async () => {
  if (!productionOrderOptions.value || productionOrderOptions.value.length === 0) {
    ElMessage.warning('没有可用的生产订单，请先创建生产订单并开始生产')
    return
  }
  
  try {
    ElMessage.info('正在创建测试数据...')
    
    // 为前3个生产订单创建测试进度数据
    const testOrders = productionOrderOptions.value.slice(0, 3)
    
    for (let i = 0; i < testOrders.length; i++) {
      const order = testOrders[i]
      if (!order || !order.id || !order.order_number) {
        console.warn(`跳过无效订单 ${i}:`, order)
        continue
      }
      
      const today = new Date()
      
      // 创建2条进度记录
      for (let j = 1; j <= 2; j++) {
        const recordDate = new Date(today)
        recordDate.setDate(today.getDate() - (2 - j)) // 前2天和前1天的记录
        
        const testData = {
          production_order: order.id,
          record_date: recordDate.toISOString().split('T')[0],
          quantity: 10 + (j * 5), // 递增的数量
          actual_efficiency: 90 + (j * 5), // 递增的效率
          delay_reason: j === 1 ? '材料延迟到货' : '',
          quality_issues: j === 1 ? 2 : 0,
          notes: `测试进度记录 ${j} - 订单 ${order.order_number}`
        }
        
        console.log(`创建测试数据 ${i + 1}-${j}:`, testData)
        await createProductionProgress(testData)
      }
    }
    
    ElMessage.success(`成功创建了测试进度记录`)
    fetchProgressList()
  } catch (error) {
    console.error('创建测试数据失败:', error)
    ElMessage.error('创建测试数据失败')
  }
}
</script>

<style scoped>
.production-progress-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-buttons {
  display: flex;
  gap: 10px;
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
</style> 