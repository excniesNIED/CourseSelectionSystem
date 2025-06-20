<template>
  <v-layout>
    <v-app-bar color="primary" prominent>
      <template #prepend>
        <v-app-bar-nav-icon @click="drawer = !drawer" />
      </template>
      
      <v-app-bar-title>
        <v-icon class="mr-3">mdi-school</v-icon>
        课程选择系统 - 教师端
      </v-app-bar-title>

      <v-spacer />

      <v-menu>
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar size="32">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ authStore.user?.name }}</v-list-item-title>
            <v-list-item-subtitle>教师</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item @click="$router.push('/teacher/profile')">
            <v-list-item-title>个人信息</v-list-item-title>
            <template #prepend>
              <v-icon>mdi-account-circle</v-icon>
            </template>
          </v-list-item>
          <v-list-item @click="authStore.logout">
            <v-list-item-title>退出登录</v-list-item-title>
            <template #prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" :permanent="!mobile">
      <v-list>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          exact
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <div class="pa-6">
        <router-view />
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const { mobile } = useDisplay()

const drawer = ref(!mobile.value)

const menuItems = [
  {
    title: '概览',
    icon: 'mdi-view-dashboard',
    to: '/teacher/overview'
  },
  {
    title: '我的课程',
    icon: 'mdi-book-open-variant',
    to: '/teacher/courses'
  },
  {
    title: '学生管理',
    icon: 'mdi-account-group',
    to: '/teacher/students'
  },
  {
    title: '成绩管理',
    icon: 'mdi-clipboard-text',
    to: '/teacher/grades'
  },
  {
    title: '统计分析',
    icon: 'mdi-chart-bar',
    to: '/teacher/statistics'
  }
]
</script>
