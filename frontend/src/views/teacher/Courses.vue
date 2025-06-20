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
          </v-card-title>

          <v-card-text>
            <!-- 搜索和筛选 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="search"
                  label="搜索课程"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="typeFilter"
                  :items="typeOptions"
                  label="课程类型"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- 课程卡片 -->
            <v-row>
              <v-col
                v-for="course in filteredCourses"
                :key="course.course_id"
                cols="12"
                md="6"
                lg="4"
              >
                <v-card class="h-100">
                  <v-card-title class="d-flex justify-space-between">
                    <span>{{ course.course_name }}</span>
                    <v-chip :color="getTypeColor(course.type)" size="small">
                      {{ course.type }}
                    </v-chip>
                  </v-card-title>

                  <v-card-subtitle>
                    课程编号：{{ course.course_id }}
                  </v-card-subtitle>

                  <v-card-text>
                    <div class="mb-3">
                      <v-icon class="mr-2">mdi-trophy</v-icon>
                      {{ course.credits }} 学分
                    </div>

                    <div class="mb-3">
                      <v-icon class="mr-2">mdi-account-group</v-icon>
                      {{ course.current_enrollment }}/{{ course.max_enrollment }} 人
                    </div>

                    <v-progress-linear
                      :model-value="(course.current_enrollment / course.max_enrollment) * 100"
                      :color="course.current_enrollment >= course.max_enrollment ? 'error' : 'success'"
                      height="8"
                      rounded
                    />

                    <div v-if="course.description" class="mt-3 text-body-2">
                      {{ course.description }}
                    </div>
                  </v-card-text>

                  <v-card-actions>
                    <v-btn
                      color="primary"
                      variant="text"
                      prepend-icon="mdi-account-group"
                      @click="viewStudents(course)"
                    >
                      学生列表
                    </v-btn>
                    <v-btn
                      color="success"
                      variant="text"
                      prepend-icon="mdi-clipboard-text"
                      @click="manageGrades(course)"
                    >
                      成绩管理
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>

            <div v-if="filteredCourses.length === 0" class="text-center py-8">
              <v-icon size="64" color="grey-lighten-1">mdi-book-plus</v-icon>
              <div class="text-h6 mt-3 text-grey-darken-1">
                {{ courses.length === 0 ? '暂无课程' : '没有符合条件的课程' }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 学生列表对话框 -->
    <v-dialog v-model="studentsDialog" max-width="800px">
      <v-card>
        <v-card-title class="text-h6 pa-6">
          <v-icon class="mr-3">mdi-account-group</v-icon>
          {{ selectedCourse?.course_name }} - 学生列表
        </v-card-title>

        <v-card-text class="pa-6">
          <v-data-table
            :headers="studentHeaders"
            :items="courseStudents"
            :loading="studentsLoading"
            item-value="student_id"
            class="elevation-1"
          >
            <template #item.grade="{ item }">
              <v-chip 
                :color="getGradeColor(item.grade)"
                size="small"
              >
                {{ item.grade || '未评分' }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn color="grey" variant="text" @click="studentsDialog = false">
            关闭
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()

const courses = ref([])
const courseStudents = ref([])
const search = ref('')
const typeFilter = ref('')

const studentsDialog = ref(false)
const studentsLoading = ref(false)
const selectedCourse = ref(null)

const typeOptions = [
  { title: '必修', value: '必修' },
  { title: '选修', value: '选修' },
  { title: '通识', value: '通识' }
]

const studentHeaders = [
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '班级', key: 'class_name', sortable: true },
  { title: '成绩', key: 'grade', sortable: true }
]

const filteredCourses = computed(() => {
  let filtered = courses.value

  if (search.value) {
    filtered = filtered.filter(course =>
      course.course_name.includes(search.value) ||
      course.course_id.includes(search.value)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(course => course.type === typeFilter.value)
  }

  return filtered
})

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

const loadCourses = async () => {
  try {
    const response = await api.get('/teacher/courses')
    courses.value = Array.isArray(response) ? response.map(course => ({
      ...course,
      type: '必修', // 默认类型
      current_enrollment: course.current_students,
      max_enrollment: course.max_students
    })) : []
  } catch (error) {
    console.error('加载课程列表失败:', error)
    courses.value = []
  }
}

const viewStudents = async (course) => {
  selectedCourse.value = course
  studentsDialog.value = true
  studentsLoading.value = true

  try {
    const response = await api.get(`/teacher/courses/${course.offering_id}/students`)
    courseStudents.value = response.students || []
  } catch (error) {
    console.error('加载学生列表失败:', error)
    courseStudents.value = []
  } finally {
    studentsLoading.value = false
  }
}

const manageGrades = (course) => {
  router.push('/teacher/grades')
}

onMounted(() => {
  loadCourses()
})
</script>
