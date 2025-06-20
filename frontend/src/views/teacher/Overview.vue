<template>
  <div>
    <v-row class="mb-6">
      <v-col cols="12">
        <h2 class="text-h4 font-weight-bold mb-2">
          欢迎回来，{{ authStore.user?.name }}！
        </h2>
        <p class="text-subtitle-1 text-grey-darken-1">
          今天是 {{ new Date().toLocaleDateString('zh-CN') }}
        </p>
      </v-col>
    </v-row>

    <!-- 统计卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="primary" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-book-open-variant</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.totalCourses }}</div>
            <div class="text-subtitle-1">授课门数</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="success" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.totalStudents }}</div>
            <div class="text-subtitle-1">学生总数</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="warning" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-clipboard-text</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.pendingGrades }}</div>
            <div class="text-subtitle-1">待评分</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="info" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-chart-line</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.avgGrade.toFixed(1) }}</div>
            <div class="text-subtitle-1">平均分</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- 我的课程 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-book-open-variant</v-icon>
              我的课程
            </div>
            <v-btn
              color="primary"
              variant="text"
              size="small"
              @click="$router.push('/teacher/courses')"
            >
              查看全部
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-list v-if="courses.length > 0">
              <v-list-item
                v-for="course in courses.slice(0, 5)"
                :key="course.course_id"
              >
                <template #prepend>
                  <v-avatar :color="getTypeColor(course.type)" size="32">
                    <v-icon>mdi-book</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ course.course_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ course.credits }}学分 · {{ course.current_enrollment }}/{{ course.max_enrollment }}人
                </v-list-item-subtitle>

                <template #append>
                  <v-chip :color="getTypeColor(course.type)" size="small">
                    {{ course.type }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>

            <div v-else class="text-center py-8 text-grey-darken-1">
              <v-icon size="64" class="mb-3">mdi-book-plus</v-icon>
              <div>暂无课程</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 最近成绩 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-clipboard-text</v-icon>
              最近成绩
            </div>
            <v-btn
              color="primary"
              variant="text"
              size="small"
              @click="$router.push('/teacher/grades')"
            >
              查看全部
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-list v-if="recentGrades.length > 0">
              <v-list-item
                v-for="grade in recentGrades.slice(0, 5)"
                :key="`${grade.student_id}-${grade.course_id}`"
              >
                <template #prepend>
                  <v-avatar color="grey-lighten-2" size="32">
                    <v-icon>mdi-account</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ grade.student_name }}</v-list-item-title>
                <v-list-item-subtitle>{{ grade.course_name }}</v-list-item-subtitle>

                <template #append>
                  <v-chip 
                    :color="getGradeColor(grade.grade)"
                    size="small"
                  >
                    {{ grade.grade || '未评分' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>

            <div v-else class="text-center py-8 text-grey-darken-1">
              <v-icon size="64" class="mb-3">mdi-clipboard-plus</v-icon>
              <div>暂无成绩记录</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 快速操作 -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-flash</v-icon>
            快速操作
          </v-card-title>

          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  size="large"
                  color="primary"
                  variant="outlined"
                  prepend-icon="mdi-account-group"
                  @click="$router.push('/teacher/students')"
                >
                  学生管理
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  size="large"
                  color="success"
                  variant="outlined"
                  prepend-icon="mdi-clipboard-text"
                  @click="$router.push('/teacher/grades')"
                >
                  成绩录入
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  size="large"
                  color="info"
                  variant="outlined"
                  prepend-icon="mdi-chart-bar"
                  @click="$router.push('/teacher/statistics')"
                >
                  统计分析
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  size="large"
                  color="warning"
                  variant="outlined"
                  prepend-icon="mdi-account-circle"
                  @click="$router.push('/teacher/profile')"
                >
                  个人信息
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()

const stats = ref({
  totalCourses: 0,
  totalStudents: 0,
  pendingGrades: 0,
  avgGrade: 0
})

const courses = ref([])
const recentGrades = ref([])

const getTypeColor = (type) => {
  switch (type) {
    case '必修': return 'error'
    case '选修': return 'primary'
    case '通识': return 'success'
    default: return 'grey'
  }
}

const getGradeColor = (grade) => {
  if (!grade) return 'grey'
  if (grade >= 90) return 'success'
  if (grade >= 80) return 'info'
  if (grade >= 70) return 'warning'
  if (grade >= 60) return 'orange'
  return 'error'
}

const loadData = async () => {
  try {
    // 加载统计数据
    const statsResponse = await api.get('/teacher/stats')
    stats.value = statsResponse

    // 加载课程列表
    const coursesResponse = await api.get('/teacher/courses')
    courses.value = coursesResponse

    // 加载最近成绩
    const gradesResponse = await api.get('/teacher/grades/recent')
    recentGrades.value = gradesResponse
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>
