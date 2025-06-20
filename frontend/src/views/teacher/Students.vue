<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-account-group</v-icon>
              <span class="text-h5">学生排名查看</span>
            </div>
          </v-card-title>

          <v-card-text>
            <!-- 查看模式选择 -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-select
                  v-model="viewMode"
                  :items="viewModeOptions"
                  label="查看方式"
                  variant="outlined"
                  density="compact"
                  @update:model-value="onViewModeChange"
                />
              </v-col>
              <v-col cols="12" md="4" v-if="viewMode === 'class'">
                <v-select
                  v-model="selectedClass"
                  :items="classOptions"
                  label="选择班级"
                  variant="outlined"
                  density="compact"
                  @update:model-value="loadClassRanking"
                />
              </v-col>
              <v-col cols="12" md="4" v-if="viewMode === 'course'">
                <v-select
                  v-model="selectedCourse"
                  :items="courseOptions"
                  label="选择课程"
                  variant="outlined"
                  density="compact"
                  @update:model-value="loadCourseStudents"
                />
              </v-col>
            </v-row>

            <!-- 班级排名视图 -->
            <div v-if="viewMode === 'class' && selectedClass">
              <v-card class="mb-4">
                <v-card-title class="text-h6">
                  {{ currentClassInfo.class_name }} - 学生均绩排名
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="classHeaders"
                    :items="classStudents"
                    :loading="loading"
                    item-value="student_id"
                    class="elevation-1"
                  >
                    <template #item.rank="{ item }">
                      <v-chip
                        :color="getRankColor(item.rank)"
                        size="small"
                      >
                        第{{ item.rank }}名
                      </v-chip>
                    </template>

                    <template #item.avg_score="{ item }">
                      <span :class="getScoreClass(item.avg_score)">
                        {{ item.avg_score }}
                      </span>
                    </template>

                    <template #item.total_credits="{ item }">
                      {{ item.total_credits }} 学分
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </div>

            <!-- 课程学生视图 -->
            <div v-if="viewMode === 'course' && selectedCourse">
              <v-card class="mb-4">
                <v-card-title class="text-h6">
                  {{ currentCourseInfo.course_name }} - 学生成绩排名
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="courseHeaders"
                    :items="courseStudents"
                    :loading="loading"
                    item-value="student_id"
                    class="elevation-1"
                  >
                    <template #item.rank="{ item }">
                      <v-chip
                        v-if="item.score !== null"
                        :color="getRankColor(item.rank)"
                        size="small"
                      >
                        第{{ item.rank }}名
                      </v-chip>
                      <span v-else class="text-grey">未录入</span>
                    </template>

                    <template #item.score="{ item }">
                      <v-chip 
                        v-if="item.score !== null"
                        :color="getScoreColor(item.score)"
                        size="small"
                      >
                        {{ item.score }}分
                      </v-chip>
                      <span v-else class="text-grey">未录入</span>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </div>

            <!-- 空状态 -->
            <div v-if="!selectedClass && !selectedCourse" class="text-center py-8">
              <v-icon size="64" color="grey">mdi-account-search</v-icon>
              <div class="text-h6 mt-4 text-grey">
                请选择{{ viewMode === 'class' ? '班级' : '课程' }}以查看学生信息
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
const viewMode = ref('class')
const selectedClass = ref('')
const selectedCourse = ref('')
const classes = ref([])
const courses = ref([])
const classStudents = ref([])
const courseStudents = ref([])

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const viewModeOptions = [
  { title: '按班级查看', value: 'class' },
  { title: '按课程查看', value: 'course' }
]

const classHeaders = [
  { title: '排名', key: 'rank', sortable: false, width: 100 },
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '性别', key: 'gender', sortable: true },
  { title: '平均分', key: 'avg_score', sortable: true },
  { title: '课程数', key: 'course_count', sortable: true },
  { title: '已修学分', key: 'total_credits', sortable: true }
]

const courseHeaders = [
  { title: '排名', key: 'rank', sortable: false, width: 100 },
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '班级', key: 'class_name', sortable: true },
  { title: '成绩', key: 'score', sortable: true }
]

const classOptions = computed(() => 
  classes.value.map(cls => ({
    title: cls.class_name,
    value: cls.class_id
  }))
)

const courseOptions = computed(() => 
  courses.value.map(course => ({
    title: `${course.course_name} (${course.course_id})`,
    value: course.offering_id
  }))
)

const currentClassInfo = computed(() => {
  const cls = classes.value.find(c => c.class_id === selectedClass.value)
  return cls || {}
})

const currentCourseInfo = computed(() => {
  const course = courses.value.find(c => c.offering_id === selectedCourse.value)
  return course || {}
})

const getRankColor = (rank) => {
  if (rank === 1) return 'error'
  if (rank <= 3) return 'warning'
  if (rank <= 5) return 'info'
  return 'grey'
}

const getScoreColor = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'info'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'orange'
  return 'error'
}

const getScoreClass = (score) => {
  if (score >= 90) return 'text-success font-weight-bold'
  if (score >= 80) return 'text-info font-weight-medium'
  if (score >= 70) return 'text-warning'
  if (score >= 60) return 'text-orange'
  return 'text-error'
}

const onViewModeChange = () => {
  selectedClass.value = ''
  selectedCourse.value = ''
  classStudents.value = []
  courseStudents.value = []
  
  if (viewMode.value === 'course') {
    loadMyCourses()
  }
}

const loadClasses = async () => {
  try {
    const response = await api.get('/admin/classes')
    classes.value = response
  } catch (error) {
    showMessage('加载班级列表失败', 'error')
  }
}

const loadMyCourses = async () => {
  try {
    const response = await api.get('/teacher/courses')
    courses.value = response
  } catch (error) {
    showMessage('加载课程列表失败', 'error')
  }
}

const loadClassRanking = async () => {
  if (!selectedClass.value) return

  loading.value = true
  try {
    const response = await api.get(`/teacher/students/class/${selectedClass.value}`)
    classStudents.value = response.students || []
  } catch (error) {
    showMessage('加载班级排名失败', 'error')
  } finally {
    loading.value = false
  }
}

const loadCourseStudents = async () => {
  if (!selectedCourse.value) return

  loading.value = true
  try {
    const response = await api.get(`/teacher/courses/${selectedCourse.value}/students`)
    courseStudents.value = response.students || []
  } catch (error) {
    showMessage('加载课程学生失败', 'error')
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
  loadClasses()
})
</script>
