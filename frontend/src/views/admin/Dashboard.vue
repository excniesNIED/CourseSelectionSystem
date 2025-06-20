<template>
  <v-layout>
    <!-- 侧边导航栏 -->
    <v-navigation-drawer
      v-model="drawer"
      permanent
      width="280"
      class="border-e"
    >      <v-list-item
        :title="authStore.userName"
        subtitle="系统管理员"
        class="mb-2"
      >
        <template #prepend>
          <v-avatar>
            <v-icon>mdi-account-circle</v-icon>
          </v-avatar>
        </template>
      </v-list-item>
      
      <v-divider />

      <v-list nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.value"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="xl"
          class="ma-2"
        />
      </v-list>

      <template #append>
        <v-list>
          <v-list-item
            prepend-icon="mdi-logout"
            title="退出登录"
            @click="logout"
            class="ma-2"
          />
        </v-list>
      </template>
    </v-navigation-drawer>

    <!-- 主内容区域 -->
    <v-main class="bg-surface-variant">
      <v-app-bar flat class="border-b bg-surface">
        <v-app-bar-nav-icon @click="drawer = !drawer" />
        <v-toolbar-title>{{ currentPageTitle }}</v-toolbar-title>
        <v-spacer />
        <v-btn icon="mdi-bell-outline" variant="text" />
        <v-btn icon="mdi-account-circle" variant="text" />
      </v-app-bar>

      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const drawer = ref(true)

const menuItems = [
  {
    title: '总览',
    icon: 'mdi-view-dashboard',
    value: 'overview',
    to: '/admin/overview'
  },
  {
    title: '教师管理',
    icon: 'mdi-account-tie',
    value: 'teachers',
    to: '/admin/teachers'
  },
  {
    title: '学生管理',
    icon: 'mdi-account-school',
    value: 'students',
    to: '/admin/students'
  },
  {
    title: '课程管理',
    icon: 'mdi-book-open-variant',
    value: 'courses',
    to: '/admin/courses'
  },
  {
    title: '班级管理',
    icon: 'mdi-account-group',
    value: 'classes',
    to: '/admin/classes'
  },
  {
    title: '个人信息',
    icon: 'mdi-account-circle',
    value: 'profile',
    to: '/admin/profile'
  }
]

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.to === route.path)
  return currentItem ? currentItem.title : '管理员控制台'
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.v-navigation-drawer {
  background: rgba(255, 255, 255, 0.98) !important;
}

.v-list-item--active {
  background: rgba(103, 80, 164, 0.12) !important;
  color: #6750A4 !important;
}

.border-e {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.border-b {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
