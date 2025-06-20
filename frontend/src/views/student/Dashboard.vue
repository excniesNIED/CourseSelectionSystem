<template>
  <v-layout>    <!-- 侧边导航栏 -->
    <v-navigation-drawer
      v-model="drawer"
      permanent
      width="280"
      class="border-e navigation-drawer"
    >
      <v-list-item
        :title="authStore.user?.name || authStore.userName"
        subtitle="学生"
        class="mb-2"
      >
        <template #prepend>
          <v-avatar>
            <v-icon>mdi-account-school</v-icon>
          </v-avatar>
        </template>
      </v-list-item>
      
      <v-divider />      <v-list nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.value"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="xl"
          class="ma-2 main-nav-item"
        />
      </v-list><template #append>
        <v-list>
          <v-list-item
            prepend-icon="mdi-account-circle"
            title="个人信息"
            @click="$router.push('/student/profile')"
            class="ma-2 nav-item"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="退出登录"
            @click="logout"
            class="ma-2 nav-item"
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
    title: '概览',
    icon: 'mdi-view-dashboard',
    value: 'overview',
    to: '/student/overview'
  },
  {
    title: '课程浏览',
    icon: 'mdi-book-open-variant',
    value: 'courses',
    to: '/student/courses'
  },
  {
    title: '选课管理',
    icon: 'mdi-bookmark-plus',
    value: 'enrollment',
    to: '/student/enrollment'
  },
  {
    title: '我的成绩',
    icon: 'mdi-trophy',
    value: 'grades',
    to: '/student/grades'
  }
]

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.to === route.path)
  return currentItem ? currentItem.title : '学生控制台'
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

.navigation-drawer {
  height: 100vh !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.navigation-drawer :deep(.v-navigation-drawer__content) {
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.navigation-drawer :deep(.v-list:first-of-type) {
  flex: 1 !important;
  overflow-y: auto !important;
  min-height: 0 !important;
}

.navigation-drawer :deep(.v-navigation-drawer__append) {
  flex-shrink: 0 !important;
  margin-top: auto !important;
}

.nav-item {
  transition: all 0.2s ease-in-out !important;
  border-radius: 12px !important;
}

.nav-item:hover {
  background-color: rgba(21, 173, 102, 0.08) !important;
  transform: translateX(4px) !important;
}

.nav-item:active {
  transform: translateX(2px) scale(0.98) !important;
}

.main-nav-item {
  transition: all 0.2s ease-in-out !important;
}

.main-nav-item:hover {
  background-color: rgba(21, 173, 102, 0.08) !important;
  transform: translateX(4px) !important;
}

.main-nav-item:active {
  transform: translateX(2px) scale(0.98) !important;
}

.v-list-item--active {
  background: rgba(21, 173, 102, 0.12) !important;
  color: #15AD66 !important;
}

.border-e {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.border-b {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
