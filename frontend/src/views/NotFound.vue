<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" md="6" class="text-center">
        <v-icon size="120" color="primary" class="mb-4">
          mdi-emoticon-sad-outline
        </v-icon>
        
        <h1 class="text-h2 font-weight-bold mb-4">404</h1>
        <h2 class="text-h4 mb-4">页面未找到</h2>
        <p class="text-body-1 text-medium-emphasis mb-6">
          抱歉，您访问的页面不存在或已被移除。
        </p>
        
        <v-btn
          color="primary"
          size="large"
          prepend-icon="mdi-home"
          @click="goHome"
        >
          返回首页
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const goHome = () => {
  if (authStore.isAuthenticated) {
    const redirectMap = {
      admin: '/admin',
      teacher: '/teacher',
      student: '/student'
    }
    router.push(redirectMap[authStore.userType] || '/login')
  } else {
    router.push('/login')
  }
}
</script>
