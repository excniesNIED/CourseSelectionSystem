<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-clipboard-text</v-icon>
              <span class="text-h5">成绩管理</span>
            </div>
          </v-card-title>

          <v-card-text>
            <!-- 课程选择 -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedYear"
                  :items="academicYears"
                  label="学年"
                  variant="outlined"
                  density="compact"
                  @update:model-value="loadMyCourses"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedSemester"
                  :items="semesterOptions"
                  label="学期"
                  variant="outlined"
                  density="compact"
                  @update:model-value="loadMyCourses"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedCourse"
                  :items="courseOptions"
                  label="选择课程"
                  variant="outlined"
                  density="compact"
                  clearable
                  @update:model-value="loadStudents"
                />
              </v-col>
            </v-row>

            <!-- 学生成绩表 -->
            <div v-if="selectedCourse">
              <v-card class="mb-4">
                <v-card-title class="text-h6">
                  {{ currentCourseInfo.course_name }} - 学生成绩
                  <v-spacer />
                  <v-btn 
                    color="primary" 
                    prepend-icon="mdi-content-save"
                    :loading="saving"
                    @click="saveScores"
                  >
                    保存成绩
                  </v-btn>
                </v-card-title>

                <v-card-text>
                  <v-data-table
                    :headers="headers"
                    :items="students"
                    :loading="loading"
                    item-value="student_id"
                    class="elevation-1"
                  >
                    <template #item.rank="{ item, index }">
                      {{ item.score !== null ? item.rank : '-' }}
                    </template>

                    <template #item.score="{ item }">
                      <v-text-field
                        v-model.number="item.score"
                        type="number"
                        min="0"
                        max="100"
                        variant="outlined"
                        density="compact"
                        hide-details
                        @blur="validateScore(item)"
                      />
                    </template>

                    <template #item.status="{ item }">
                      <v-chip 
                        v-if="item.score !== null && item.score !== undefined"
                        :color="item.score >= 60 ? 'success' : 'error'"
                        size="small"
                      >
                        {{ item.score >= 60 ? '及格' : '不及格' }}
                      </v-chip>
                      <span v-else class="text-grey">未录入</span>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>

              <!-- 成绩统计 -->
              <v-card>
                <v-card-title class="text-h6">成绩统计</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="6" md="3">
                      <v-card color="primary" dark class="text-center pa-4">
                        <div class="text-h4">{{ courseStats.total_students }}</div>
                        <div>总人数</div>
                      </v-card>
                    </v-col>
                    <v-col cols="6" md="3">
                      <v-card color="success" dark class="text-center pa-4">
                        <div class="text-h4">{{ courseStats.passed_students }}</div>
                        <div>及格人数</div>
                      </v-card>
                    </v-col>
                    <v-col cols="6" md="3">
                      <v-card color="warning" dark class="text-center pa-4">
                        <div class="text-h4">{{ courseStats.pass_rate }}%</div>
                        <div>及格率</div>
                      </v-card>
                    </v-col>
                    <v-col cols="6" md="3">
                      <v-card color="info" dark class="text-center pa-4">
                        <div class="text-h4">{{ courseStats.avg_score }}</div>
                        <div>平均分</div>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </div>

            <!-- 选择提示 -->
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey">mdi-clipboard-outline</v-icon>
              <div class="text-h6 mt-4 text-grey">请选择课程以查看学生名单</div>
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
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const saving = ref(false)
const courses = ref([])
const students = ref([])
const selectedYear = ref('2024')
const selectedSemester = ref(1)
const selectedCourse = ref('')

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const headers = [
  { title: '排名', key: 'rank', sortable: false, width: 80 },
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '班级', key: 'class_name', sortable: true },
  { title: '成绩', key: 'score', sortable: false, width: 150 },
  { title: '状态', key: 'status', sortable: false, width: 100 }
]

const academicYears = ['2024', '2023', '2022']

const semesterOptions = [
  { title: '春季学期', value: 0 },
  { title: '秋季学期', value: 1 }
]

const courseOptions = computed(() => 
  courses.value.map(course => ({
    title: `${course.course_name} (${course.course_id})`,
    value: course.offering_id
  }))
)

const currentCourseInfo = computed(() => {
  const course = courses.value.find(c => c.offering_id === selectedCourse.value)
  return course || {}
})

const courseStats = computed(() => {
  const validScores = students.value.filter(s => s.score !== null && s.score !== undefined)
  const passedStudents = validScores.filter(s => s.score >= 60)
  const totalScore = validScores.reduce((sum, s) => sum + s.score, 0)
  
  return {
    total_students: students.value.length,
    passed_students: passedStudents.length,
    pass_rate: students.value.length > 0 ? Math.round(passedStudents.length / students.value.length * 100) : 0,
    avg_score: validScores.length > 0 ? Math.round(totalScore / validScores.length * 10) / 10 : 0
  }
})

const loadMyCourses = async () => {
  try {
    const params = {
      academic_year: selectedYear.value,
      semester: selectedSemester.value
    }

    const response = await api.get('/teacher/courses', { params })
    courses.value = response
    selectedCourse.value = ''
    students.value = []
  } catch (error) {
    showMessage('加载课程列表失败', 'error')
  }
}

const loadStudents = async () => {
  if (!selectedCourse.value) {
    students.value = []
    return
  }

  loading.value = true
  try {
    const response = await api.get(`/teacher/courses/${selectedCourse.value}/students`)
    students.value = response.students || []
  } catch (error) {
    showMessage('加载学生名单失败', 'error')
  } finally {
    loading.value = false
  }
}

const validateScore = (student) => {
  if (student.score !== null && student.score !== undefined) {
    if (student.score < 0) student.score = 0
    if (student.score > 100) student.score = 100
  }
}

const saveScores = async () => {
  if (!selectedCourse.value) return

  saving.value = true
  try {
    const scores = students.value
      .filter(s => s.score !== null && s.score !== undefined)
      .map(s => ({
        student_id: s.student_id,
        score: s.score
      }))

    await api.put(`/teacher/courses/${selectedCourse.value}/scores`, { scores })
    showMessage('成绩保存成功', 'success')
    loadStudents() // 重新加载以获取排名
  } catch (error) {
    showMessage(error.message || '保存成绩失败', 'error')
  } finally {
    saving.value = false
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadMyCourses()
})
</script>
