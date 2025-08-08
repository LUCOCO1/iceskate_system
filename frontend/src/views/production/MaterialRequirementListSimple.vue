<template>
  <div class="material-requirement-container">
    <h2>材料需求管理</h2>
    <el-card>
      <div v-if="loading">加载中...</div>
      <div v-else>
        <p>材料需求功能正在维护中，请稍后再试。</p>
        <el-button type="primary" @click="handleRefresh">刷新</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const handleRefresh = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('功能正在开发中')
  }, 1000)
}
</script>

<style scoped>
.material-requirement-container {
  padding: 20px;
}
</style> 