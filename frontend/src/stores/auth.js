import { defineStore } from 'pinia'
import api from '@/utils/api'
import { useUserStore } from './user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: false
  }),

  getters: {
    userType: (state) => state.user?.type || null,
    userName: (state) => state.user?.name || '',
    userId: (state) => state.user?.id || ''
  },
  actions: {
    async login(credentials) {
      try {
        const response = await api.post('/auth/login', credentials)
        
        this.token = response.access_token
        this.user = response.user
        this.isAuthenticated = true
        
        // 保存token到localStorage
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        // 设置用户角色并获取详细信息
        const userStore = useUserStore()
        userStore.setUserRole(this.user.type)
        await userStore.fetchUserProfile()
        
        return response
      } catch (error) {
        // 抛出后端返回的实际错误信息
        throw error.response?.data || error
      }
    },

    async changePassword(passwordData) {
      try {
        const response = await api.post('/auth/change-password', passwordData)
        return response
      } catch (error) {
        throw error
      }
    },

    async verifyToken() {
      if (!this.token) {
        return false
      }

      try {
        const response = await api.post('/auth/verify-token')
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      // 清空用户store
      const userStore = useUserStore()
      userStore.clearUser()
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    // 初始化认证状态（从localStorage恢复）
    async initAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.isAuthenticated = true
        
        // 初始化用户store
        const userStore = useUserStore()
        userStore.setUserRole(this.user.type)
        await userStore.fetchUserProfile()
      }
    }
  }
})
