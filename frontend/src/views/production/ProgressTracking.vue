<template>
  <div class="progress-tracking-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <h2>生产进度跟踪</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleUpdateProgress" :disabled="!currentOrder">
          <el-icon><Edit /></el-icon>更新进度
        </el-button>
      </div>
    </div>

    <el-card v-if="loading" class="loading-card">
      <el-skeleton :rows="10" animated />
    </el-card>

    <template v-else-if="currentOrder">
      <!-- 订单信息 -->
      <el-card class="order-info-card">
        <template #header>
          <div class="card-header">
            <span>订单基本信息</span>
            <el-tag :type="getStatusTagType(currentOrder.status)">
              {{ getStatusLabel(currentOrder.status) }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">{{ currentOrder.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="产品名称">{{ currentOrder.productName }}</el-descriptions-item>
          <el-descriptions-item label="生产数量">{{ currentOrder.quantity }}</el-descriptions-item>
          <el-descriptions-item label="计划开始日期">{{ currentOrder.planStartDate }}</el-descriptions-item>
          <el-descriptions-item label="计划完成日期">{{ currentOrder.planEndDate }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentOrder.createTime }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 进度信息 -->
      <el-card class="progress-card">
        <template #header>
          <div class="card-header">
            <span>生产进度</span>
            <div class="progress-percentage">
              <span class="percentage-text">{{ currentOrder.progress }}%</span>
              <el-progress
                :percentage="currentOrder.progress"
                :status="getProgressStatus(currentOrder)"
                :stroke-width="20"
              />
            </div>
          </div>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="(stage, index) in productionStages"
            :key="index"
            :type="getTimelineItemType(stage, currentOrder.progress)"
            :color="getTimelineItemColor(stage, currentOrder.progress)"
            :timestamp="stage.time || ''"
          >
            <h4>{{ stage.name }}</h4>
            <p>{{ stage.description }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 问题记录 -->
      <el-card class="issues-card">
        <template #header>
          <div class="card-header">
            <span>问题记录</span>
            <el-button type="primary" size="small" @click="handleAddIssue">
              <el-icon><Plus /></el-icon>添加记录
            </el-button>
          </div>
        </template>
        
        <el-table :data="issueList" border style="width: 100%">
          <el-table-column prop="time" label="记录时间" width="180" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="scope">
              <el-tag :type="getIssueTypeTag(scope.row.type)">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已解决' ? 'success' : 'warning'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="handler" label="处理人" width="120" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button
                size="small"
                type="success"
                @click="handleResolveIssue(scope.row)"
                :disabled="scope.row.status === '已解决'"
              >解决</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <el-empty v-else description="未找到订单信息" />

    <!-- 更新进度对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="更新生产进度"
      width="500px"
    >
      <el-form
        ref="progressFormRef"
        :model="progressForm"
        :rules="progressRules"
        label-width="100px"
      >
        <el-form-item label="当前进度" prop="progress">
          <el-slider
            v-model="progressForm.progress"
            :min="0"
            :max="100"
            :step="5"
            show-input
          />
        </el-form-item>
        <el-form-item label="当前阶段" prop="currentStage">
          <el-select v-model="progressForm.currentStage" placeholder="请选择当前阶段" style="width: 100%">
            <el-option
              v-for="(stage, index) in productionStages"
              :key="index"
              :label="stage.name"
              :value="index"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="progressForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入进度更新备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="progressDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProgressForm">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加问题记录对话框 -->
    <el-dialog
      v-model="issueDialogVisible"
      title="添加问题记录"
      width="500px"
    >
      <el-form
        ref="issueFormRef"
        :model="issueForm"
        :rules="issueRules"
        label-width="100px"
      >
        <el-form-item label="问题类型" prop="type">
          <el-select v-model="issueForm.type" placeholder="请选择问题类型" style="width: 100%">
            <el-option label="材料问题" value="材料问题" />
            <el-option label="设备故障" value="设备故障" />
            <el-option label="人员问题" value="人员问题" />
            <el-option label="质量问题" value="质量问题" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="issueForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入问题描述"
          />
        </el-form-item>
        <el-form-item label="处理人" prop="handler">
          <el-input v-model="issueForm.handler" placeholder="请输入处理人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="issueDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitIssueForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { ArrowLeft, Edit, Plus } from '@element-plus/icons-vue'
import { 
  getProductionOrderDetail, 
  recordProductionProgress 
} from '@/api/production'

const router = useRouter()
const route = useRoute()

// 定义订单类型接口
interface Order {
  id: number
  orderNo: string
  productName: string
  quantity: number
  planStartDate: string
  planEndDate: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  progress: number
  createTime: string
  remark?: string
}

// 定义生产阶段接口
interface ProductionStage {
  name: string
  description: string
  progressRange: [number, number]
  time?: string
}

// 定义问题记录接口
interface Issue {
  id: number
  time: string
  type: string
  description: string
  status: '待解决' | '已解决'
  handler: string
}

// 页面状态
const loading = ref(true)
const currentOrder = ref<Order | null>(null)
const productionStages = reactive<ProductionStage[]>([
  {
    name: '备料阶段',
    description: '准备生产所需的原材料和工具',
    progressRange: [0, 20],
    time: '2023-03-05 08:00:00'
  },
  {
    name: '加工阶段',
    description: '对原材料进行切割、成型等加工',
    progressRange: [20, 50],
    time: '2023-03-07 10:30:00'
  },
  {
    name: '组装阶段',
    description: '将各个部件组装成产品',
    progressRange: [50, 80],
    time: '2023-03-10 14:15:00'
  },
  {
    name: '质检阶段',
    description: '对产品进行质量检测',
    progressRange: [80, 90],
    time: ''
  },
  {
    name: '包装入库',
    description: '产品包装并入库',
    progressRange: [90, 100],
    time: ''
  }
])

// 问题记录
const issueList = ref<Issue[]>([
  {
    id: 1,
    time: '2023-03-06 09:30:00',
    type: '材料问题',
    description: '部分钢材规格不符合要求',
    status: '已解决',
    handler: '张工'
  },
  {
    id: 2,
    time: '2023-03-08 14:20:00',
    type: '设备故障',
    description: '切割机出现故障，需要维修',
    status: '待解决',
    handler: '李工'
  }
])

// 进度更新对话框
const progressDialogVisible = ref(false)
const progressFormRef = ref<FormInstance>()
const progressForm = reactive({
  progress: 0,
  currentStage: 0,
  remark: ''
})

// 问题记录对话框
const issueDialogVisible = ref(false)
const issueFormRef = ref<FormInstance>()
const issueForm = reactive({
  type: '',
  description: '',
  handler: ''
})

// 表单验证规则
const progressRules = {
  progress: [
    { required: true, message: '请设置当前进度', trigger: 'change' }
  ],
  currentStage: [
    { required: true, message: '请选择当前阶段', trigger: 'change' }
  ]
}

const issueRules = {
  type: [
    { required: true, message: '请选择问题类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' }
  ],
  handler: [
    { required: true, message: '请输入处理人', trigger: 'blur' }
  ]
}

// 生命周期钩子
onMounted(() => {
  const orderId = route.query.orderId
  if (orderId) {
    fetchOrderDetail(Number(orderId))
  } else {
    loading.value = false
  }
})

// 获取订单详情
const fetchOrderDetail = async (orderId: number) => {
  loading.value = true
  try {
    const res = await getProductionOrderDetail(orderId)
    console.log('获取到的订单详情:', res)
    
    if (res && res.data) {
      const orderData = res.data
      currentOrder.value = {
        id: orderData.id,
        orderNo: orderData.order_number,
        productName: orderData.product_name,
        quantity: orderData.planned_quantity,
        planStartDate: orderData.start_date,
        planEndDate: orderData.end_date,
        status: orderData.status,
        progress: orderData.progress || 0,
        createTime: orderData.created_at
      }
      
      // 初始化进度表单
      if (currentOrder.value) {
        progressForm.progress = currentOrder.value.progress
        
        // 根据进度确定当前阶段
        for (let i = 0; i < productionStages.length; i++) {
          const [min, max] = productionStages[i].progressRange
          if (currentOrder.value.progress >= min && currentOrder.value.progress <= max) {
            progressForm.currentStage = i
            break
          }
        }
      }
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    ElMessage.error('获取订单详情失败')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.push('/production/orders')
}

// 更新进度
const handleUpdateProgress = () => {
  progressDialogVisible.value = true
}

// 提交进度表单
const submitProgressForm = async () => {
  if (!progressFormRef.value) return
  
  await progressFormRef.value.validate(async (valid) => {
    if (valid && currentOrder.value) {
      try {
        // 计算本次增加的进度数量
        const currentProgress = currentOrder.value.progress
        const newProgress = progressForm.progress
        const progressIncrease = newProgress - currentProgress
        
        if (progressIncrease <= 0) {
          ElMessage.warning('新进度必须大于当前进度')
          return
        }
        
        // 计算对应的完成数量（基于进度百分比）
        const totalQuantity = currentOrder.value.quantity
        const completedQuantity = (progressIncrease / 100) * totalQuantity
        
        // 调用记录进度API
        await recordProductionProgress(currentOrder.value.id, {
          completed_quantity: completedQuantity,
          notes: progressForm.remark
        })
        
        // 更新本地数据
        currentOrder.value.progress = progressForm.progress
        
        // 更新阶段时间
        const now = new Date()
        const timeStr = now.toLocaleString()
        productionStages[progressForm.currentStage].time = timeStr
        
        // 如果进度到100%，更新订单状态为已完成
        if (progressForm.progress === 100) {
          currentOrder.value.status = 'completed'
        }
        
        ElMessage.success('进度更新成功')
        progressDialogVisible.value = false
      } catch (error) {
        console.error('更新进度失败:', error)
        ElMessage.error('更新进度失败')
      }
    }
  })
}

// 添加问题记录
const handleAddIssue = () => {
  issueForm.type = ''
  issueForm.description = ''
  issueForm.handler = ''
  issueDialogVisible.value = true
}

// 提交问题表单
const submitIssueForm = async () => {
  if (!issueFormRef.value) return
  
  await issueFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该调用API保存数据
      const now = new Date()
      const newIssue: Issue = {
        id: issueList.value.length + 1,
        time: now.toLocaleString(),
        type: issueForm.type,
        description: issueForm.description,
        status: '待解决',
        handler: issueForm.handler
      }
      
      issueList.value.unshift(newIssue)
      ElMessage.success('问题记录添加成功')
      issueDialogVisible.value = false
    }
  })
}

// 解决问题
const handleResolveIssue = (issue: Issue) => {
  ElMessageBox.confirm(
    `确定将问题 "${issue.description}" 标记为已解决吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    // 这里应该调用API更新数据
    issue.status = '已解决'
    ElMessage.success('问题已标记为已解决')
  }).catch(() => {})
}

// 获取状态标签样式
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待生产',
    in_progress: '生产中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || '未知'
}

// 获取进度条状态
const getProgressStatus = (order: Order) => {
  if (order.status === 'completed') return 'success'
  if (order.status === 'cancelled') return 'exception'
  return ''
}

// 获取时间线项目类型
const getTimelineItemType = (stage: ProductionStage, progress: number) => {
  const [min, max] = stage.progressRange
  if (progress >= max) return 'success'
  if (progress >= min && progress < max) return 'primary'
  return ''
}

// 获取时间线项目颜色
const getTimelineItemColor = (stage: ProductionStage, progress: number) => {
  const [min, max] = stage.progressRange
  if (progress >= max) return '#67C23A'
  if (progress >= min && progress < max) return '#409EFF'
  return ''
}

// 获取问题类型标签
const getIssueTypeTag = (type: string) => {
  const map: Record<string, string> = {
    '材料问题': 'danger',
    '设备故障': 'warning',
    '人员问题': 'info',
    '质量问题': 'error',
    '其他': ''
  }
  return map[type] || ''
}
</script>

<style scoped>
.progress-tracking-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left h2 {
  margin-left: 15px;
}

.loading-card,
.order-info-card,
.progress-card,
.issues-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-percentage {
  display: flex;
  align-items: center;
  width: 300px;
}

.percentage-text {
  width: 50px;
  text-align: right;
  margin-right: 10px;
  font-weight: bold;
}
</style> 