<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- 成绩统计卡片 -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-card color="primary" dark>
              <v-card-text class="text-center">
                <v-icon size="48" class="mb-2">mdi-book-open</v-icon>
                <div class="text-h4">{{ statistics.total_credits }}</div>
                <div>已修学分</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="success" dark>
              <v-card-text class="text-center">
                <v-icon size="48" class="mb-2">mdi-chart-line</v-icon>
                <div class="text-h4">{{ statistics.overall_gpa }}</div>
                <div>加权平均分</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="info" dark>
              <v-card-text class="text-center">
                <v-icon size="48" class="mb-2">mdi-check-circle</v-icon>
                <div class="text-h4">{{ statistics.passed_courses }}</div>
                <div>通过课程</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="warning" dark>
              <v-card-text class="text-center">
                <v-icon size="48" class="mb-2">mdi-percent</v-icon>
                <div class="text-h4">{{ statistics.pass_rate }}%</div>
                <div>通过率</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 成绩详情 -->
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-file-document</v-icon>
              <span class="text-h5">我的成绩</span>
            </div>
          </v-card-title>

          <v-card-text>
            <!-- 筛选条件 -->
            <v-row class="mb-4">
              <v-col cols="12" md="3">
                <v-select
                  v-model="selectedYear"
                  :items="academicYears"
                  label="学年"
                  variant="outlined"
                  density="compact"
                  clearable
                  @update:model-value="loadScores"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="selectedSemester"
                  :items="semesterOptions"
                  label="学期"
                  variant="outlined"
                  density="compact"
                  clearable
                  @update:model-value="loadScores"
                />
              </v-col>
            </v-row>

            <!-- 学期分组展示 -->
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate></v-progress-circular>
            </div>

            <v-expansion-panels v-else multiple>
              <v-expansion-panel
                v-for="semester in scoreData.semesters"
                :key="`${semester.academic_year}-${semester.semester}`"
              >
                <v-expansion-panel-title>
                  <div class="d-flex justify-space-between align-center w-100">
                    <span class="text-h6">
                      {{ semester.academic_year }} {{ semester.semester ? '秋季学期' : '春季学期' }}
                    </span>
                    <div class="d-flex align-center">
                      <v-chip color="primary" size="small" class="mr-2">
                        {{ semester.semester_credits }} 学分
                      </v-chip>
                      <v-chip color="success" size="small">
                        平均分：{{ semester.semester_gpa }}
                      </v-chip>
                    </div>
                  </div>
                </v-expansion-panel-title>

                <v-expansion-panel-text>
                  <v-data-table
                    :headers="headers"
                    :items="semester.courses"
                    item-value="offering_id"
                    class="elevation-1"
                    hide-default-footer
                    disable-pagination
                  >
                    <template #item.credits="{ item }">
                      {{ item.credits }} 学分
                    </template>

                    <template #item.score="{ item }">
                      <v-chip 
                        :color="getScoreColor(item.score)"
                        size="small"
                      >
                        {{ item.score }}分
                      </v-chip>
                    </template>

                    <template #item.passed="{ item }">
                      <v-icon 
                        :color="item.passed ? 'success' : 'error'"
                        :icon="item.passed ? 'mdi-check-circle' : 'mdi-close-circle'"
                      />
                    </template>
                  </v-data-table>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- 无成绩提示 -->
            <div v-if="!loading && scoreData.semesters.length === 0" class="text-center py-8">
              <v-icon size="64" color="grey">mdi-file-document-outline</v-icon>
              <div class="text-h6 mt-4 text-grey">暂无成绩记录</div>
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
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const scoreData = ref({ semesters: [], total_credits: 0, overall_gpa: 0 })
const statistics = ref({
  total_credits: 0,
  overall_gpa: 0,
  passed_courses: 0,
  pass_rate: 0
})
const selectedYear = ref('')
const selectedSemester = ref('')

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const headers = [
  { title: '课程代码', key: 'course_id', sortable: true },
  { title: '课程名称', key: 'course_name', sortable: true },
  { title: '授课教师', key: 'teacher_name', sortable: true },
  { title: '学分', key: 'credits', sortable: true },
  { title: '考核方式', key: 'exam_type', sortable: true },
  { title: '成绩', key: 'score', sortable: true },
  { title: '通过', key: 'passed', sortable: true }
]

const academicYears = ['2024', '2023', '2022']

const semesterOptions = [
  { title: '春季学期', value: 0 },
  { title: '秋季学期', value: 1 }
]

const getScoreColor = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'info'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'orange'
  return 'error'
}

const loadScores = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedSemester.value !== '') params.semester = selectedSemester.value

    const response = await api.get('/student/scores', { params })
    scoreData.value = response
  } catch (error) {
    showMessage('加载成绩信息失败', 'error')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await api.get('/student/statistics')
    statistics.value = response
  } catch (error) {
    showMessage('加载统计信息失败', 'error')
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadScores()
  loadStatistics()
})
</script>
