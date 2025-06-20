<template>
  <div>
    <!-- 统计卡片 -->
    <v-row class="mb-6">
      <v-col
        v-for="stat in statistics"
        :key="stat.title"
        cols="12"
        sm="6"
        md="4"
        lg="2"
      >
        <v-card class="pa-4 text-center stat-card">
          <v-icon :color="stat.color" size="48" class="mb-2">
            {{ stat.icon }}
          </v-icon>
          <div class="text-h4 font-weight-bold mb-1">
            {{ stat.value }}
          </div>
          <div class="text-body-2 text-medium-emphasis">
            {{ stat.title }}
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 快速操作 -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-flash</v-icon>
            快速操作
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                v-for="action in quickActions"
                :key="action.title"
                cols="12"
                sm="6"
                md="3"
              >
                <v-card
                  :to="action.to"
                  class="quick-action-card pa-4 text-center"
                  hover
                  variant="outlined"
                >
                  <v-icon :color="action.color" size="36" class="mb-2">
                    {{ action.icon }}
                  </v-icon>
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ action.title }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ action.description }}
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 最近活动 -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-timeline</v-icon>
            系统概览
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="item in systemInfo"
                :key="item.title"
                :prepend-icon="item.icon"
              >
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.value }}</v-list-item-subtitle>
                <template #append>
                  <v-chip
                    :color="item.status === 'success' ? 'success' : 'warning'"
                    size="small"
                    variant="flat"
                  >
                    {{ item.statusText }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-information</v-icon>
            系统信息
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>系统版本</v-list-item-title>
                <v-list-item-subtitle>v1.0.0</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>数据库状态</v-list-item-title>
                <v-list-item-subtitle>正常连接</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>最后更新</v-list-item-title>
                <v-list-item-subtitle>{{ new Date().toLocaleDateString() }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const statistics = ref([
  { title: '教师总数', value: 0, icon: 'mdi-account-tie', color: 'primary' },
  { title: '学生总数', value: 0, icon: 'mdi-account-school', color: 'secondary' },
  { title: '课程总数', value: 0, icon: 'mdi-book-open-variant', color: 'tertiary' },
  { title: '班级总数', value: 0, icon: 'mdi-account-group', color: 'success' },
  { title: '开课数量', value: 0, icon: 'mdi-calendar-check', color: 'warning' },
  { title: '选课记录', value: 0, icon: 'mdi-clipboard-list', color: 'info' }
])

const quickActions = [
  {
    title: '添加教师',
    description: '新增教师信息',
    icon: 'mdi-account-plus',
    color: 'primary',
    to: '/admin/teachers'
  },
  {
    title: '添加学生',
    description: '新增学生信息',
    icon: 'mdi-account-school-outline',
    color: 'secondary',
    to: '/admin/students'
  },
  {
    title: '添加课程',
    description: '新增课程信息',
    icon: 'mdi-book-plus',
    color: 'tertiary',
    to: '/admin/courses'
  },
  {
    title: '添加班级',
    description: '新增班级信息',
    icon: 'mdi-account-group-outline',
    color: 'success',
    to: '/admin/classes'
  }
]

const systemInfo = ref([
  {
    title: '数据库连接',
    value: 'MySQL 连接正常',
    icon: 'mdi-database',
    status: 'success',
    statusText: '正常'
  },
  {
    title: '系统运行时间',
    value: '1天 12小时 30分钟',
    icon: 'mdi-clock',
    status: 'success',
    statusText: '稳定'
  },
  {
    title: '内存使用',
    value: '512MB / 2GB',
    icon: 'mdi-memory',
    status: 'success',
    statusText: '良好'
  },
  {
    title: '存储空间',
    value: '2.1GB / 10GB',
    icon: 'mdi-harddisk',
    status: 'success',
    statusText: '充足'
  }
])

const loadStatistics = async () => {
  try {
    const response = await api.get('/admin/statistics')
    
    statistics.value[0].value = response.teacher_count
    statistics.value[1].value = response.student_count
    statistics.value[2].value = response.course_count
    statistics.value[3].value = response.class_count
    statistics.value[4].value = response.offering_count
    statistics.value[5].value = response.enrollment_count
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.stat-card {
  height: 140px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.quick-action-card {
  height: 120px;
  transition: all 0.2s;
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
</style>
