<template>
  <div class="supplier-detail-container">
    <div class="page-header">
      <div class="title-container">
        <el-button @click="goBack" circle plain>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>供应商详情</h2>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="供应商编码">{{ supplier.code }}</el-descriptions-item>
        <el-descriptions-item label="供应商名称">{{ supplier.name }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ supplier.contact || '无' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ supplier.phone || '无' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ supplier.address || '无' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="supplier.is_active ? 'success' : 'danger'">
            {{ supplier.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ supplier.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import { getSupplierDetail } from '@/api/inventory'
import type { Supplier } from '@/types/inventory'

const route = useRoute()
const router = useRouter()
const supplierId = Number(route.params.id)

// 供应商详情
const supplier = ref<Supplier>({} as Supplier)
const loading = ref(true)

// 获取供应商详情
const fetchSupplierDetail = async () => {
  loading.value = true
  try {
    const res = await getSupplierDetail(supplierId)
    if (res && typeof res === 'object') {
      supplier.value = res.data || res
    }
  } catch (error) {
    console.error('获取供应商详情失败:', error)
    ElMessage.error('获取供应商详情失败')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑供应商
const handleEdit = () => {
  ElMessage.info('编辑功能待实现')
}

onMounted(() => {
  fetchSupplierDetail()
})
</script>

<style scoped>
.supplier-detail-container {
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

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 