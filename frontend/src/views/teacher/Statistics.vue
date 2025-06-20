<template>
  <v-container>
    <!-- 统计概览卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card color="primary" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-book-open-variant</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.total_courses }}</div>
            <div class="text-subtitle-1">教授课程</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="success" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.current_students }}</div>
            <div class="text-subtitle-1">当前学生</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="info" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-chart-line</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.average_score }}</div>
            <div class="text-subtitle-1">平均分</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="warning" theme="dark">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-3">mdi-clipboard-check</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.graded_assignments }}</div>
            <div class="text-subtitle-1">已评成绩</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- 课程统计 -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-chart-bar</v-icon>
              <span>课程统计</span>
            </div>
            <v-select
              v-model="selectedYear"
              :items="academicYears"
              label="学年"
              variant="outlined"
              density="compact"
              style="max-width: 200px"
              @update:model-value="loadCourseStatistics"
            />
          </v-card-title>

          <v-card-text>
            <v-data-table
              :headers="courseHeaders"
              :items="courseStatistics.courses"
              :loading="loading"
              item-value="offering_id"
              class="elevation-1"
            >
              <template #item.semester="{ item }">
                {{ item.semester ? '秋季学期' : '春季学期' }}
              </template>

              <template #item.avg_score="{ item }">
                <v-chip 
                  :color="getScoreColor(item.avg_score)"
                  size="small"
                >
                  {{ item.avg_score }}
                </v-chip>
              </template>

              <template #item.student_count="{ item }">
                {{ item.student_count }} 人
              </template>
            </v-data-table>

            <v-divider class="my-4" />

            <div class="text-center">
              <div class="text-h6 mb-2">学年总体统计</div>
              <v-chip color="primary" class="mr-2">
                总课程数: {{ courseStatistics.course_count }}
              </v-chip>
              <v-chip color="success">
                总平均分: {{ courseStatistics.total_avg_score }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 成绩分析 -->
      <v-col cols="12" lg="4">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon class="mr-3">mdi-chart-pie</v-icon>
            成绩分布
          </v-card-title>
          <v-card-text>
            <div v-if="gradeDistribution.length > 0">
              <div 
                v-for="grade in gradeDistribution" 
                :key="grade.range"
                class="d-flex justify-space-between align-center mb-2"
              >
                <span>{{ grade.range }}</span>
                <v-chip :color="grade.color" size="small">
                  {{ grade.count }}人 ({{ grade.percentage }}%)
                </v-chip>
              </div>
            </div>
            <div v-else class="text-center text-grey">
              暂无成绩数据
            </div>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>
            <v-icon class="mr-3">mdi-trending-up</v-icon>
            教学趋势
          </v-card-title>
          <v-card-text>
            <div class="text-center">
              <div class="text-h3 font-weight-bold mb-2" :class="getTrendColor()">
                {{ teachingTrend.direction }}
              </div>
              <div class="text-subtitle-1">
                相比上学期平均分{{ teachingTrend.change }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 消息提示 -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const selectedYear = ref('2024')
const stats = ref({
  total_courses: 0,
  current_students: 0,
  average_score: 0,
  graded_assignments: 0
})
const courseStatistics = ref({
  courses: [],
  course_count: 0,
  total_avg_score: 0
})

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const academicYears = ['2024', '2023', '2022']

const courseHeaders = [
  { title: '课程代码', key: 'course_id', sortable: true },
  { title: '课程名称', key: 'course_name', sortable: true },
  { title: '学期', key: 'semester', sortable: true },
  { title: '学生数', key: 'student_count', sortable: true },
  { title: '平均分', key: 'avg_score', sortable: true }
]

const gradeDistribution = computed(() => {
  const courses = courseStatistics.value.courses
  if (!courses || courses.length === 0) return []

  const ranges = [
    { range: '90-100分', color: 'success', min: 90, max: 100 },
    { range: '80-89分', color: 'info', min: 80, max: 89 },
    { range: '70-79分', color: 'warning', min: 70, max: 79 },
    { range: '60-69分', color: 'orange', min: 60, max: 69 },
    { range: '60分以下', color: 'error', min: 0, max: 59 }
  ]

  const total = courses.reduce((sum, course) => sum + course.student_count, 0)

  return ranges.map(range => {
    const count = courses.reduce((sum, course) => {
      if (course.avg_score >= range.min && course.avg_score <= range.max) {
        return sum + course.student_count
      }
      return sum
    }, 0)

    return {
      ...range,
      count,
      percentage: total > 0 ? Math.round(count / total * 100) : 0
    }
  }).filter(range => range.count > 0)
})

const teachingTrend = computed(() => {
  const currentYear = courseStatistics.value.total_avg_score
  // 这里可以添加与历史数据的比较逻辑
  const change = Math.random() > 0.5 ? '提升2.3分' : '下降1.2分'
  const direction = change.includes('提升') ? '↗' : '↘'
  
  return { direction, change }
})

const getScoreColor = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'info'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'orange'
  return 'error'
}

const getTrendColor = () => {
  return teachingTrend.value.direction === '↗' ? 'text-success' : 'text-error'
}

const loadTeacherStats = async () => {
  try {
    const response = await api.get('/teacher/stats')
    stats.value = response
  } catch (error) {
    showMessage('加载统计信息失败', 'error')
  }
}

const loadCourseStatistics = async () => {
  loading.value = true
  try {
    const params = { academic_year: selectedYear.value }
    const response = await api.get('/teacher/statistics/courses', { params })
    courseStatistics.value = response
  } catch (error) {
    showMessage('加载课程统计失败', 'error')
  } finally {
    loading.value = false
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadTeacherStats()
  loadCourseStatistics()
})
</script>
