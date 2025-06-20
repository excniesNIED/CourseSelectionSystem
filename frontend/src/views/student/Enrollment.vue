<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-school</v-icon>
              <span class="text-h5">选课管理</span>
            </div>
            <v-btn color="secondary" prepend-icon="mdi-book-open" to="/student/courses">
              我的课程
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
                  @update:model-value="loadAvailableCourses"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="selectedSemester"
                  :items="semesterOptions"
                  label="学期"
                  variant="outlined"
                  density="compact"
                  @update:model-value="loadAvailableCourses"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="search"
                  label="搜索课程"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- 可选课程列表 -->
            <v-data-table
              :headers="headers"
              :items="filteredCourses"
              :loading="loading"
              item-value="offering_id"
              class="elevation-1"
            >
              <template #item.credits="{ item }">
                {{ item.credits }} 学分
              </template>

              <template #item.enrollment_status="{ item }">
                <v-chip 
                  :color="item.available ? 'success' : 'error'"
                  size="small"
                >
                  {{ item.current_students }}/{{ item.max_students }}
                </v-chip>
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  color="primary"
                  size="small"
                  variant="elevated"
                  :disabled="!item.available || enrolling"
                  :loading="enrollingId === item.offering_id"
                  @click="enrollCourse(item)"
                >
                  {{ item.available ? '选课' : '已满' }}
                </v-btn>
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
const enrolling = ref(false)
const enrollingId = ref(null)
const availableCourses = ref([])
const selectedYear = ref('2024')
const selectedSemester = ref(1)
const search = ref('')

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
  { title: '选课人数', key: 'enrollment_status', sortable: true },
  { title: '操作', key: 'actions', sortable: false, width: 120 }
]

const academicYears = ['2024', '2023', '2022']

const semesterOptions = [
  { title: '春季学期', value: 0 },
  { title: '秋季学期', value: 1 }
]

const filteredCourses = computed(() => {
  if (!search.value) return availableCourses.value
  
  return availableCourses.value.filter(course =>
    course.course_name.includes(search.value) ||
    course.course_id.includes(search.value) ||
    course.teacher_name.includes(search.value)
  )
})

const loadAvailableCourses = async () => {
  loading.value = true
  try {
    const params = {
      academic_year: selectedYear.value,
      semester: selectedSemester.value
    }

    const response = await api.get('/student/courses/available', { params })
    availableCourses.value = response
  } catch (error) {
    showMessage('加载可选课程失败', 'error')
  } finally {
    loading.value = false
  }
}

const enrollCourse = async (course) => {
  enrolling.value = true
  enrollingId.value = course.offering_id
  
  try {
    await api.post(`/student/courses/${course.offering_id}/enroll`)
    showMessage(`成功选择课程：${course.course_name}`, 'success')
    loadAvailableCourses() // 重新加载列表
  } catch (error) {
    showMessage(error.message || '选课失败', 'error')
  } finally {
    enrolling.value = false
    enrollingId.value = null
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadAvailableCourses()
})
</script>
