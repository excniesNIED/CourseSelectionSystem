<template>
  <div>
    <v-row class="mb-6">
      <v-col cols="12">
        <h2 class="text-h4 font-weight-bold mb-2">
          欢迎，{{ authStore.user?.name }}！
        </h2>
        <p class="text-subtitle-1 text-grey-darken-1">
          学号：{{ authStore.user?.student_id }} | 班级：{{ profile.class_name }}
        </p>
      </v-col>
    </v-row>

    <!-- 统计卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="primary" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-book-open-variant</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.enrolledCourses }}</div>
            <div class="text-subtitle-1">已选课程</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="success" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-trophy</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.totalCredits }}</div>
            <div class="text-subtitle-1">已修学分</div>
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

      <v-col cols="12" sm="6" md="3">
        <v-card class="h-100" color="warning" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-bookmark-plus</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.availableCourses }}</div>
            <div class="text-subtitle-1">可选课程</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- 我的课程 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-book-open-variant</v-icon>
            我的课程
          </v-card-title>
          <v-card-text>
            <v-list v-if="enrolledCourses.length > 0">
              <v-list-item
                v-for="course in enrolledCourses.slice(0, 5)"
                :key="course.course_id"
              >
                <template #prepend>
                  <v-avatar :color="getTypeColor(course.type)" size="32">
                    <v-icon>mdi-book</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ course.course_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ course.credits }}学分 · {{ course.teacher_name }}
                </v-list-item-subtitle>
                <template #append>
                  <v-chip :color="getGradeColor(course.grade)" size="small">
                    {{ course.grade || '未评分' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-1">mdi-book-plus</v-icon>
              <div class="text-h6 mt-3">暂无选课</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 快速操作 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-flash</v-icon>
            快速操作
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-btn
                  block
                  size="large"
                  color="primary"
                  prepend-icon="mdi-book-search"
                  @click="$router.push('/student/courses')"
                >
                  浏览课程
                </v-btn>
              </v-col>
              <v-col cols="12">
                <v-btn
                  block
                  size="large"
                  color="success"
                  prepend-icon="mdi-bookmark-plus"
                  @click="$router.push('/student/enrollment')"
                >
                  选课管理
                </v-btn>
              </v-col>
              <v-col cols="12">
                <v-btn
                  block
                  size="large"
                  color="info"
                  prepend-icon="mdi-trophy"
                  @click="$router.push('/student/grades')"
                >
                  查看成绩
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
  enrolledCourses: 0,
  totalCredits: 0,
  avgGrade: 0,
  availableCourses: 0
})

const enrolledCourses = ref([])
const profile = ref({})

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
    const [statsResponse, coursesResponse, profileResponse] = await Promise.all([
      api.get('/student/stats'),
      api.get('/student/enrollments'),
      api.get('/student/profile')
    ])
    
    stats.value = statsResponse
    enrolledCourses.value = coursesResponse
    profile.value = profileResponse
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>
