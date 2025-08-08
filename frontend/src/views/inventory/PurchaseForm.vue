<template>
  <div class="purchase-form-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>{{ isEdit ? '编辑采购单' : '新增采购单' }}</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          <el-icon><Check /></el-icon>保存
        </el-button>
        <el-button @click="goBack">
          <el-icon><Close /></el-icon>取消
        </el-button>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="purchaseForm"
      :rules="rules"
      label-width="120px"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购单号" prop="purchase_number">
              <el-input 
                v-model="purchaseForm.purchase_number" 
                placeholder="提交时自动生成，无需填写"
                disabled
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier">
              <el-select 
                v-model="purchaseForm.supplier" 
                placeholder="请选择供应商"
                filterable
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="item in supplierOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购日期" prop="purchase_date">
              <el-date-picker
                v-model="purchaseForm.purchase_date"
                type="date"
                placeholder="选择采购日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交货日期" prop="delivery_date">
              <el-date-picker
                v-model="purchaseForm.delivery_date"
                type="date"
                placeholder="选择交货日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="purchaseForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-card>

      <!-- 采购明细 -->
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>采购明细</span>
            <el-button type="primary" @click="handleAddItem" plain>
              <el-icon><Plus /></el-icon>添加材料
            </el-button>
          </div>
        </template>
        <div v-if="purchaseForm.items && purchaseForm.items.length > 0">
          采购明细数量: {{ purchaseForm.items.length }}
        </div>
        <div v-else>
          无采购明细数据
        </div>
        <el-table :data="purchaseForm.items || []" border style="width: 100%">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column label="材料名称" min-width="150">
            <template #default="scope">
              <el-select
                v-model="scope.row.material"
                placeholder="选择材料"
                filterable
                clearable
                style="width: 100%"
                @change="(val: number | undefined) => handleMaterialChange(val, scope.$index)"
              >
                <el-option
                  v-for="item in materialOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="规格" min-width="120">
            <template #default="scope">
              <el-input v-model="scope.row.specification" placeholder="规格" />
            </template>
          </el-table-column>
          <el-table-column label="管制单号" width="150">
            <template #default="scope">
              <el-input v-model="scope.row.control_number" placeholder="管制单号" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="120">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="单位" width="80">
            <template #default="scope">
              <el-input v-model="scope.row.unit" placeholder="单位" />
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="120">
            <template #default="scope">
              <el-input v-model="scope.row.notes" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="scope">
              <el-button
                type="danger"
                @click="handleRemoveItem(scope.$index)"
                circle
                plain
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="empty-data" v-if="!purchaseForm.items || purchaseForm.items.length === 0">
          <el-empty description="暂无采购明细，请添加材料" />
        </div>
      </el-card>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { ArrowLeft, Check, Close, Plus, Delete } from '@element-plus/icons-vue'
import { getSupplierList, getMaterialList, getPurchaseDetail, createPurchase, updatePurchase } from '@/api/inventory'
import type { MaterialPurchase, PurchaseItem, Supplier, Material } from '@/types/inventory'

// 扩展PurchaseItem接口，添加供应方式字段
interface ExtendedPurchaseItem extends PurchaseItem {
  control_number: string;      // 管制编号
  specification: string;        // 规格尺寸
  quantity: number;            // 数量
  unit: string;                // 单位
  notes?: string;              // 备注
  material_type: string;       // 改为必填字段
}

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)
const purchaseId = computed(() => Number(route.params.id) || 0)

// 表单数据
const purchaseForm = reactive<MaterialPurchase>({
  id: 0,
  purchase_number: '',
  supplier: undefined as unknown as number,
  supplier_name: '',
  purchase_date: new Date().toISOString().split('T')[0],
  delivery_date: '',
  status: 'draft',
  notes: '',
  items: [] as PurchaseItem[],
  created_at: '',
  updated_at: ''
})

// 表单验证规则
const rules = {
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  purchase_date: [{ required: true, message: '请选择采购日期', trigger: 'change' }]
}

// 加载状态
const loading = ref(false)
const submitting = ref(false)

// 选项数据
const supplierOptions = ref<Supplier[]>([])
const materialOptions = ref<Material[]>([])

// 获取供应商列表
const fetchSuppliers = async () => {
  try {
    const res = await getSupplierList({ page_size: 1000 })
    if (res && typeof res === 'object') {
      const data = res.data || res
      if ('results' in data) {
        supplierOptions.value = data.results
      }
    }
  } catch (error) {
    console.error('获取供应商列表失败:', error)
  }
}

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

// 获取采购单详情
const fetchPurchaseDetail = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const res = await getPurchaseDetail(purchaseId.value)
    if (res && typeof res === 'object') {
      const data = res.data || res
      
      // 添加日志查看后端返回的数据结构
      console.log('后端返回的采购单详情:', JSON.stringify(data, null, 2))
      
      // 确保items数组正确解析
      if (data.items && Array.isArray(data.items)) {
        // 转换后端返回的明细项以符合前端格式
        data.items = data.items.map((item: any) => ({
          id: item.id,
          purchase: item.purchase,
          material: item.material,
          material_name: item.material_name || `${item.material_name || ''}`,
          control_number: item.control_number || '',
          specification: item.specification || '',
          quantity: item.quantity || 0,
          received_quantity: item.received_quantity || 0,
          unit: item.unit || '个',
          material_type: item.material_type || '平板料',
          notes: item.notes || ''
        }))
      } else {
        // 如果后端没有返回items数组或格式不对，初始化一个空数组
        data.items = []
      }
      
      Object.assign(purchaseForm, data)
      
      // 检查赋值后的数据
      console.log('前端处理后的采购单数据:', JSON.stringify(purchaseForm, null, 2))
      
      // 在获取采购单详情时，再额外检查明细数据的结构
      console.log('获取到的明细原始数据:', data.items);
    }
  } catch (error) {
    console.error('获取采购单详情失败:', error)
    ElMessage.error('获取采购单详情失败')
  } finally {
    loading.value = false
  }
}

// 材料选择变更
const handleMaterialChange = (materialId: number | undefined, index: number) => {
  if (!materialId) return;
  
  const material = materialOptions.value.find(item => item.id === materialId);
  if (material && purchaseForm.items) {
    // 更新材料名称，包括材料编码
    purchaseForm.items[index].material_name = `${material.name} (${material.code})`;
    purchaseForm.items[index].specification = material.specification || '';
    purchaseForm.items[index].unit = material.unit || '个';
  }
}

// 添加采购明细项
const handleAddItem = () => {
  const newItem: ExtendedPurchaseItem = {
    id: 0,
    purchase: purchaseId.value,
    material: undefined as unknown as number,
    control_number: '',
    specification: '',
    quantity: 1,
    received_quantity: 0,
    unit: '个',
    material_type: '平板料',
    notes: ''
  }
  if (purchaseForm.items) {
    purchaseForm.items.push(newItem as PurchaseItem)
  } else {
    purchaseForm.items = [newItem as PurchaseItem]
  }
}

// 移除采购明细项
const handleRemoveItem = (index: number) => {
  if (purchaseForm.items) {
    purchaseForm.items.splice(index, 1)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请检查表单填写是否正确')
      return
    }
    
    if (!purchaseForm.items || purchaseForm.items.length === 0) {
      ElMessage.error('请至少添加一项采购明细')
      return
    }
    
    // 验证明细项
    for (const item of purchaseForm.items) {
      if (!item.material) {
        ElMessage.error('请选择材料')
        return
      }
      if (!item.quantity || item.quantity <= 0) {
        ElMessage.error('请输入有效的数量')
        return
      }
      // 确保必填字段有值
      if (!item.control_number) {
        item.control_number = `CN-${Date.now()}-${Math.floor(Math.random() * 1000)}`
      }
      if (!item.material_type) {
        item.material_type = '平板料'
      }
    }
    
    // 准备提交的数据
    const submitData: any = { ...purchaseForm }
    
    // 确保采购单号不为空
    if (!submitData.purchase_number && !isEdit.value) {
      // 生成临时采购单号，格式：PO-年月日-随机数
      const now = new Date();
      const dateStr = now.getFullYear().toString() +
                     (now.getMonth() + 1).toString().padStart(2, '0') +
                     now.getDate().toString().padStart(2, '0');
      const randomStr = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
      submitData.purchase_number = `PO-${dateStr}-${randomStr}`;
    }
    
    // 确保日期格式正确
    if (submitData.purchase_date && typeof submitData.purchase_date === 'string') {
      // 确保日期格式为YYYY-MM-DD
      if (!/^\d{4}-\d{2}-\d{2}$/.test(submitData.purchase_date)) {
        const date = new Date(submitData.purchase_date)
        submitData.purchase_date = date.toISOString().split('T')[0]
      }
    }
    
    if (submitData.delivery_date && typeof submitData.delivery_date === 'string') {
      // 确保日期格式为YYYY-MM-DD
      if (!/^\d{4}-\d{2}-\d{2}$/.test(submitData.delivery_date)) {
        const date = new Date(submitData.delivery_date)
        submitData.delivery_date = date.toISOString().split('T')[0]
      }
    }
    
    // 移除可能导致问题的字段
    if (!isEdit.value) {
      delete submitData.id
      delete submitData.created_at
      delete submitData.updated_at
    }
    
    // 确保items中的每个项目都有正确的字段
    if (submitData.items) {
      submitData.items = submitData.items.map((item: ExtendedPurchaseItem) => ({
        material: item.material,
        material_name: item.material_name,
        control_number: item.control_number,
        specification: item.specification,
        quantity: item.quantity,
        unit: item.unit,
        notes: item.notes,
        material_type: item.material_type || '平板料'
      }))
    }
    
    console.log('采购明细数据:', JSON.stringify(submitData.items, null, 2));
    
    console.log('提交的数据:', JSON.stringify(submitData, null, 2))
    
    submitting.value = true
    try {
      if (isEdit.value) {
        await updatePurchase(purchaseId.value, submitData)
        ElMessage.success('采购单更新成功')
        
        // 暂时注释掉可能有问题的代码
        // const result = await getPurchaseDetail(purchaseId.value)
        // console.log('保存后立即获取的数据:', result)
      } else {
        await createPurchase(submitData)
        ElMessage.success('采购单创建成功')
      }
      router.push('/inventory/purchases')
    } catch (error: any) {
      console.error('保存采购单失败:', error)
      // 显示更详细的错误信息
      if (error.response) {
        console.log('错误响应数据:', error.response)
        if (error.response.data) {
          if (typeof error.response.data === 'object') {
            // 如果是对象，格式化显示
            const errorMessages = Object.entries(error.response.data)
              .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
              .join('\n');
            ElMessage.error(`保存采购单失败:\n${errorMessages}`);
          } else {
            // 如果不是对象，直接显示
            ElMessage.error(`保存采购单失败: ${error.response.data}`);
          }
        } else {
          ElMessage.error(`保存采购单失败: 状态码 ${error.response.status}`);
        }
      } else if (error.request) {
        ElMessage.error('保存采购单失败: 服务器未响应');
      } else {
        ElMessage.error(`保存采购单失败: ${error.message}`);
      }
    } finally {
      submitting.value = false
    }
  })
}

// 返回上一页
const goBack = () => {
  ElMessageBox.confirm(
    '确定要离开当前页面吗？未保存的数据将会丢失',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    router.back()
  }).catch(() => {})
}

onMounted(() => {
  fetchSuppliers()
  fetchMaterials()
  fetchPurchaseDetail()
  
  // 如果是新建模式，预生成一个采购单号（仅用于显示）
  if (!isEdit.value && !purchaseForm.purchase_number) {
    const now = new Date();
    const dateStr = now.getFullYear().toString() +
                   (now.getMonth() + 1).toString().padStart(2, '0') +
                   now.getDate().toString().padStart(2, '0');
    const randomStr = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    purchaseForm.purchase_number = `PO-${dateStr}-${randomStr} (预览)`;
  }
})
</script>

<style scoped>
.purchase-form-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-data {
  margin: 20px 0;
}
</style> 