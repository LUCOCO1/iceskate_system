<template>
  <div class="inventory-form-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>{{ isEdit ? '编辑盘点单' : '新建盘点单' }}</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="submitForm">
          <el-icon><Check /></el-icon>保存
        </el-button>
      </div>
    </div>

    <el-card class="form-card" v-loading="loading">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="盘点单号" prop="inventory_number">
          <el-input v-model="formData.inventory_number" placeholder="系统自动生成" disabled />
        </el-form-item>
        <el-form-item label="盘点日期" prop="inventory_date">
          <el-date-picker
            v-model="formData.inventory_date"
            type="date"
            placeholder="选择盘点日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="formData.notes"
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="materials-card">
      <template #header>
        <div class="card-header">
          <span>盘点明细</span>
          <el-button type="primary" @click="addMaterial">
            <el-icon><Plus /></el-icon>添加材料
          </el-button>
        </div>
      </template>

      <el-table :data="formData.items" border style="width: 100%">
        <el-table-column label="材料" min-width="200">
          <template #default="scope">
            <el-select
              v-model="scope.row.material"
              filterable
              remote
              reserve-keyword
              placeholder="请输入材料名称或编码"
              :remote-method="searchMaterials"
              :loading="materialsLoading"
              style="width: 100%"
              @change="handleMaterialChange($event, scope.$index)"
            >
              <el-option
                v-for="item in materialOptions"
                :key="item.id"
                :label="`${item.name} (${item.code})`"
                :value="item.id"
              >
                <span>{{ item.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ item.code }}
                </span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="material_name" label="材料名称" min-width="150" />
        <el-table-column label="系统数量" width="150">
          <template #default="scope">
            <span>{{ scope.row.system_quantity }} {{ scope.row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实际数量" width="200">
          <template #default="scope">
            <el-input-number
              v-model="scope.row.actual_quantity"
              :min="0"
              :precision="2"
              style="width: 100%"
              @change="calculateDifference(scope.$index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="差异数量" width="150">
          <template #default="scope">
            <span :class="getDifferenceClass(scope.row.difference)">
              {{ scope.row.difference }} {{ scope.row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button
              type="danger"
              size="small"
              @click="removeMaterial(scope.$index)"
              text
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import { ArrowLeft, Check, Plus, Delete } from '@element-plus/icons-vue'
import { getMaterialList, createInventory, getInventoryDetail, updateInventory } from '@/api/inventory'
import type { Inventory, InventoryItem, Material } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => route.name === 'InventoryEdit')
const inventoryId = isEdit.value ? Number(route.params.id) : 0

// 自定义类型，扩展InventoryItem类型
interface ExtendedInventoryItem extends Partial<InventoryItem> {
  unit?: string;
}

// 表单数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const formData = reactive<Partial<Inventory & { items: ExtendedInventoryItem[] }>>({
  inventory_number: '系统自动生成',
  inventory_date: new Date().toISOString().split('T')[0],
  status: 'draft',
  notes: '',
  items: []
})

// 表单验证规则
const rules = {
  inventory_date: [
    { required: true, message: '请选择盘点日期', trigger: 'change' }
  ]
}

// 材料选择相关
const materialOptions = ref<Material[]>([])
const materialsLoading = ref(false)

// 获取盘点单详情
const fetchInventoryDetail = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const res = await getInventoryDetail(inventoryId)
    // 确保res是正确的类型
    if (res && typeof res === 'object') {
      Object.assign(formData, res)
    }
  } catch (error) {
    console.error('获取盘点单详情失败:', error)
    ElMessage.error('获取盘点单详情失败')
  } finally {
    loading.value = false
  }
}

// 搜索材料
const searchMaterials = async (query: string) => {
  if (query.length < 1) return
  
  materialsLoading.value = true
  try {
    const res = await getMaterialList({
      search: query,
      limit: 10
    })
    // 确保res.results存在
    if (res && typeof res === 'object' && 'results' in res) {
      materialOptions.value = res.results as Material[]
    }
  } catch (error) {
    console.error('搜索材料失败:', error)
  } finally {
    materialsLoading.value = false
  }
}

// 处理材料选择变化
const handleMaterialChange = async (materialId: number, index: number) => {
  const material = materialOptions.value.find(item => item.id === materialId)
  if (!material) return
  
  formData.items![index].material_name = material.name
  formData.items![index].system_quantity = material.stock
  formData.items![index].unit = material.unit
  formData.items![index].actual_quantity = material.stock
  calculateDifference(index)
}

// 计算差异数量
const calculateDifference = (index: number) => {
  const item = formData.items![index]
  item.difference = Number(item.actual_quantity) - Number(item.system_quantity)
}

// 添加材料
const addMaterial = () => {
  formData.items!.push({
    material: undefined,
    material_name: '',
    system_quantity: 0,
    actual_quantity: 0,
    difference: 0,
    unit: '',
    notes: ''
  })
}

// 移除材料
const removeMaterial = (index: number) => {
  formData.items!.splice(index, 1)
}

// 获取差异样式
const getDifferenceClass = (difference: number) => {
  if (difference < 0) {
    return 'difference-negative'
  } else if (difference > 0) {
    return 'difference-positive'
  }
  return ''
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (formData.items!.length === 0) {
        ElMessage.warning('请至少添加一项盘点明细')
        return
      }
      
      for (const item of formData.items!) {
        if (!item.material) {
          ElMessage.warning('请选择材料')
          return
        }
      }
      
      loading.value = true
      try {
        if (isEdit.value) {
          await updateInventory(inventoryId, formData)
          ElMessage.success('更新成功')
        } else {
          await createInventory(formData)
          ElMessage.success('创建成功')
        }
        router.push('/inventory/inventories')
      } catch (error) {
        console.error(isEdit.value ? '更新失败:' : '创建失败:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchInventoryDetail()
})
</script>

<style scoped>
.inventory-form-container {
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

.form-card,
.materials-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.difference-negative {
  color: #f56c6c;
  font-weight: bold;
}

.difference-positive {
  color: #67c23a;
  font-weight: bold;
}
</style> 