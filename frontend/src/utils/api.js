import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const authStore = useAuthStore()
    // 对 401 做全局处理，跳转登录，但排除登录接口本身
    if (error.response?.status === 401 && !error.config?.url?.endsWith('/auth/login')) {
      authStore.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error.response?.data || error.message)
  }
)

export default api
