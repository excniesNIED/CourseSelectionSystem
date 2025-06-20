<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-book-open-variant</v-icon>
              <span class="text-h5">我的课程</span>
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" to="/student/enrollment">
              选课管理
            </v-btn>
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
                  @update:model-value="loadCourses"
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
                  @update:model-value="loadCourses"
                />
              </v-col>
            </v-row>

            <!-- 课程列表 -->
            <v-data-table
              :headers="headers"
              :items="courses"
              :loading="loading"
              item-value="offering_id"
              class="elevation-1"
            >
              <template #item.credits="{ item }">
                {{ item.credits }} 学分
              </template>

              <template #item.semester="{ item }">
                {{ item.academic_year }} {{ item.semester ? '秋季学期' : '春季学期' }}
              </template>

              <template #item.score="{ item }">
                <v-chip 
                  v-if="item.score !== null"
                  :color="item.score >= 60 ? 'success' : 'error'"
                  size="small"
                >
                  {{ item.score }}分
                </v-chip>
                <span v-else class="text-grey">未录入</span>
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  v-if="item.score === null"
                  icon="mdi-close"
                  size="small"
                  color="error"
                  variant="text"
                  @click="dropCourse(item)"
                  title="退选"
                />
              </template>
            </v-data-table>
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
const courses = ref([])
const selectedYear = ref('')
const selectedSemester = ref('')

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const headers = [
  { title: '课程代码', key: 'course_id', sortable: true },
  { title: '课程名称', key: 'course_name', sortable: true },
  { title: '授课教师', key: 'teacher_name', sortable: true },
  { title: '职称', key: 'teacher_title', sortable: true },
  { title: '学分', key: 'credits', sortable: true },
  { title: '课时', key: 'hours', sortable: true },
  { title: '考核方式', key: 'exam_type', sortable: true },
  { title: '学期', key: 'semester', sortable: true },
  { title: '成绩', key: 'score', sortable: true },
  { title: '操作', key: 'actions', sortable: false, width: 100 }
]

const academicYears = ['2024', '2023', '2022']

const semesterOptions = [
  { title: '春季学期', value: 0 },
  { title: '秋季学期', value: 1 }
]

const loadCourses = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedSemester.value !== '') params.semester = selectedSemester.value

    const response = await api.get('/student/courses', { params })
    courses.value = response
  } catch (error) {
    showMessage('加载课程列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const dropCourse = async (course) => {
  try {
    await api.delete(`/student/courses/${course.offering_id}/drop`)
    showMessage('退选成功', 'success')
    loadCourses()
  } catch (error) {
    showMessage(error.message || '退选失败', 'error')
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadCourses()
})
</script>
