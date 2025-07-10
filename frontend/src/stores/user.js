import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null,
    role: null,
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.profile,
    userName: (state) => state.profile?.name || '',
    userId: (state) => {
      if (!state.profile) return ''
      return state.profile.student_id || state.profile.teacher_id || state.profile.admin_id || ''
    },
    userDisplayInfo: (state) => {
      if (!state.profile) return {}
      
      switch (state.role) {
        case 'student':
          return {
            id: state.profile.student_id,
            name: state.profile.name,
            type: '学生',
            class: state.profile.class_name || state.profile.class_id,
            credits: state.profile.total_credits
          }
        case 'teacher':
          return {
            id: state.profile.teacher_id,
            name: state.profile.name,
            type: '教师',
            title: state.profile.title,
            phone: state.profile.phone
          }
        case 'admin':
          return {
            id: state.profile.admin_id,
            name: state.profile.name,
            type: '管理员',
            username: state.profile.username
          }
        default:
          return {}
      }
    }
  },

  actions: {
    async fetchUserProfile() {
      if (this.loading) return
      
      this.loading = true
      try {
        let response
        
        // 根据当前用户角色获取对应的用户信息
        if (this.role === 'student') {
          response = await api.get('/student/profile')
        } else if (this.role === 'teacher') {
          response = await api.get('/teacher/profile')
        } else if (this.role === 'admin') {
          response = await api.get('/admin/profile')
        } else {
          // 如果角色未知，尝试通用接口
          response = await api.get('/common/profile')
        }
        
        this.profile = response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 如果获取失败，清空用户信息
        this.profile = null
        this.role = null
      } finally {
        this.loading = false
      }
    },

    setUserRole(role) {
      this.role = role
    },

    clearUser() {
      this.profile = null
      this.role = null
      this.loading = false
    },

    async updateProfile(updateData) {
      try {
        let response
        
        if (this.role === 'student') {
          response = await api.put('/student/profile', updateData)
        } else if (this.role === 'teacher') {
          response = await api.put('/teacher/profile', updateData)
        } else if (this.role === 'admin') {
          response = await api.put('/admin/profile', updateData)
        }
        
        // 更新本地状态
        this.profile = { ...this.profile, ...response }
        
        return response
      } catch (error) {
        console.error('更新用户信息失败:', error)
        throw error
      }
    }
  }
})
