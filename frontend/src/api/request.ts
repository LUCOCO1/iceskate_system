import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 60000,
  withCredentials: true
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    let message = '请求失败'
    
    if (error.response) {
      const { status } = error.response
      
      // 处理常见错误
      if (status === 401) {
        message = '未授权，请重新登录'
        localStorage.removeItem('token')
        router.push('/login')
      } else if (status === 403) {
        message = '拒绝访问'
      } else if (status === 404) {
        message = '请求的资源不存在'
      } else if (status === 500) {
        message = '服务器错误'
      } else {
        message = error.response.data.message || error.response.data.error || `请求失败(${status})`
      }
    } else if (error.request) {
      message = '服务器无响应'
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查网络连接'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service 