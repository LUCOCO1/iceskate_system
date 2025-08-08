<template>
  <div class="test-page">
    <el-card>
      <template #header>
        <h2>API接口测试页面</h2>
      </template>
      
      <el-space direction="vertical" :size="20" style="width: 100%">
        <!-- 测试按钮区域 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-button type="success" @click="testLoginAPI" :loading="loading.login">
              测试登录API
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="testCustomerAPI" :loading="loading.customer">
              测试客户API
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="testOrderAPI" :loading="loading.order">
              测试订单API
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="warning" @click="clearResults">
              清空结果
            </el-button>
          </el-col>
        </el-row>

        <!-- 结果显示区域 -->
        <el-divider content-position="left">测试结果</el-divider>
        
        <!-- 登录API测试结果 -->
        <el-card v-if="results.login" shadow="never">
          <template #header>
            <span>登录API测试结果</span>
            <el-tag :type="results.login.success ? 'success' : 'danger'" style="margin-left: 10px">
              {{ results.login.success ? '成功' : '失败' }}
            </el-tag>
          </template>
          <pre>{{ results.login.data }}</pre>
        </el-card>
        
        <!-- 客户API测试结果 -->
        <el-card v-if="results.customer" shadow="never">
          <template #header>
            <span>客户API测试结果</span>
            <el-tag :type="results.customer.success ? 'success' : 'danger'" style="margin-left: 10px">
              {{ results.customer.success ? '成功' : '失败' }}
            </el-tag>
          </template>
          <pre>{{ results.customer.data }}</pre>
        </el-card>

        <!-- 订单API测试结果 -->
        <el-card v-if="results.order" shadow="never">
          <template #header>
            <span>订单API测试结果</span>
            <el-tag :type="results.order.success ? 'success' : 'danger'" style="margin-left: 10px">
              {{ results.order.success ? '成功' : '失败' }}
            </el-tag>
          </template>
          <pre>{{ results.order.data }}</pre>
        </el-card>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { login } from '@/api/user'
import { getCustomerList, getOrderList } from '@/api/orders'

const loading = reactive({
  login: false,
  customer: false,
  order: false
})

const results = reactive<{
  login?: { success: boolean; data: string }
  customer?: { success: boolean; data: string }
  order?: { success: boolean; data: string }
}>({})

const testLoginAPI = async () => {
  loading.login = true
  try {
    console.log('=== 开始测试登录API ===')
    const res = await login({ username: 'admin', password: 'admin123' })
    console.log('登录API原始响应:', res)
    
    results.login = {
      success: true,
      data: JSON.stringify({
        message: '登录成功！',
        token: res.token ? `${res.token.substring(0, 10)}...` : 'N/A',
        user: res.user,
        fullResponse: res
      }, null, 2)
    }
    
    ElMessage.success('登录API测试成功')
  } catch (error: any) {
    console.error('登录API测试失败:', error)
    results.login = {
      success: false,
      data: JSON.stringify({
        error: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        fullURL: `${error.config?.baseURL}${error.config?.url}`,
        response: error.response?.data,
        requestConfig: {
          method: error.config?.method,
          url: error.config?.url,
          baseURL: error.config?.baseURL,
          headers: error.config?.headers
        }
      }, null, 2)
    }
    ElMessage.error('登录API测试失败')
  } finally {
    loading.login = false
  }
}

const testCustomerAPI = async () => {
  loading.customer = true
  try {
    console.log('=== 开始测试客户API ===')
    const res = await getCustomerList({ page_size: 10 })
    console.log('客户API原始响应:', res)
    
    results.customer = {
      success: true,
      data: JSON.stringify({
        responseType: typeof res,
        hasData: !!res?.data,
        dataType: typeof res?.data,
        isArray: Array.isArray(res?.data),
        hasPagination: res?.data && 'results' in res.data && 'count' in res.data,
        actualData: res?.data,
        count: res?.data?.count || (Array.isArray(res?.data) ? res.data.length : 0)
      }, null, 2)
    }
    
    ElMessage.success('客户API测试成功')
  } catch (error: any) {
    console.error('客户API测试失败:', error)
    results.customer = {
      success: false,
      data: JSON.stringify({
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        full: error
      }, null, 2)
    }
    ElMessage.error('客户API测试失败')
  } finally {
    loading.customer = false
  }
}

const testOrderAPI = async () => {
  loading.order = true
  try {
    console.log('=== 开始测试订单API ===')
    const res = await getOrderList({ page_size: 10 })
    console.log('订单API原始响应:', res)
    
    results.order = {
      success: true,
      data: JSON.stringify({
        responseType: typeof res,
        hasData: !!res?.data,
        dataType: typeof res?.data,
        isArray: Array.isArray(res?.data),
        hasPagination: res?.data && 'results' in res.data && 'count' in res.data,
        actualData: res?.data,
        count: res?.data?.count || (Array.isArray(res?.data) ? res.data.length : 0)
      }, null, 2)
    }
    
    ElMessage.success('订单API测试成功')
  } catch (error: any) {
    console.error('订单API测试失败:', error)
    results.order = {
      success: false,
      data: JSON.stringify({
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        full: error
      }, null, 2)
    }
    ElMessage.error('订单API测试失败')
  } finally {
    loading.order = false
  }
}

const clearResults = () => {
  results.login = undefined
  results.customer = undefined
  results.order = undefined
}
</script>

<style scoped>
.test-page {
  padding: 20px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style> 