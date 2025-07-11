<template>  <div>
    <!-- 统计卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.basic_stats?.total_students || 0"
          label="学生总数"
          icon="mdi-account-group"
          icon-color="primary"
          card-color="primary"
          card-variant="tonal"
          :loading="loading"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.basic_stats?.total_teachers || 0"
          label="教师总数"
          icon="mdi-account-tie"
          icon-color="success"
          card-color="success"
          card-variant="tonal"
          :loading="loading"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.basic_stats?.total_courses || 0"
          label="课程总数"
          icon="mdi-book-open-variant"
          icon-color="info"
          card-color="info"
          card-variant="tonal"
          :loading="loading"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.course_stats?.total_offerings || 0"
          label="开课数量"
          icon="mdi-school"
          icon-color="warning"
          card-color="warning"
          card-variant="tonal"
          :loading="loading"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.course_stats?.total_enrolled || 0"
          label="选课人次"
          icon="mdi-bookmark-check"
          icon-color="secondary"
          card-color="secondary"
          card-variant="tonal"
          :loading="loading"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="4" lg="2">
        <StatCard
          :value="statistics.course_stats?.avg_enrollment_rate || 0"
          label="选课率"
          subtitle="平均选课率"
          icon="mdi-chart-pie"
          icon-color="error"
          card-color="error"
          card-variant="tonal"
          value-type="percentage"
          :precision="1"
          :loading="loading"
        />
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
import StatCard from '@/components/common/StatCard.vue'

const statistics = ref({})
const loading = ref(true)

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
    loading.value = true
    const response = await api.get('/admin/statistics/overview')
    statistics.value = response
  } catch (error) {
    console.error('加载统计信息失败:', error)
  } finally {
    loading.value = false
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
