<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-book-open-variant</v-icon>
              <span class="text-h5">课程管理</span>
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">
              添加课程
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜索和筛选 -->
            <v-row class="mb-4">
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
              <v-col cols="12" md="3">
                <v-select
                  v-model="teacherFilter"
                  :items="teacherOptions"
                  label="授课教师"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- 数据表格 -->
            <v-data-table
              :headers="headers"
              :items="filteredCourses"
              :loading="loading"
              item-value="course_id"
              class="elevation-1"
            >
              <template #item.credits="{ item }">
                {{ item.credits }} 学分
              </template>

              <template #item.type="{ item }">
                <v-chip :color="getTypeColor(item.type)" size="small">
                  {{ item.type }}
                </v-chip>
              </template>

              <template #item.enrollment_status="{ item }">
                <v-chip 
                  :color="item.current_enrollment >= item.max_enrollment ? 'error' : 'success'"
                  size="small"
                >
                  {{ item.current_enrollment }}/{{ item.max_enrollment }}
                </v-chip>
              </template>
              
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  color="primary"
                  variant="text"
                  @click="editCourse(item)"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  variant="text"
                  @click="deleteCourse(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 添加/编辑对话框 -->
    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-6">
          <v-icon class="mr-3">{{ isEdit ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
          {{ isEdit ? '编辑课程' : '添加课程' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="valid" @submit.prevent="saveCourse">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedCourse.course_id"
                  label="课程编号"
                  variant="outlined"
                  :rules="[v => !!v || '课程编号不能为空']"
                  :disabled="isEdit"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedCourse.course_name"
                  label="课程名称"
                  variant="outlined"
                  :rules="[v => !!v || '课程名称不能为空']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedCourse.credits"
                  label="学分"
                  type="number"
                  variant="outlined"
                  :rules="[v => !!v || '学分不能为空', v => v > 0 || '学分必须大于0']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedCourse.type"
                  :items="typeOptions"
                  label="课程类型"
                  variant="outlined"
                  :rules="[v => !!v || '请选择课程类型']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedCourse.teacher_id"
                  :items="teacherOptions"
                  label="授课教师"
                  variant="outlined"
                  :rules="[v => !!v || '请选择授课教师']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedCourse.max_enrollment"
                  label="最大选课人数"
                  type="number"
                  variant="outlined"
                  :rules="[v => !!v || '最大选课人数不能为空', v => v > 0 || '最大选课人数必须大于0']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="editedCourse.description"
                  label="课程描述"
                  variant="outlined"
                  rows="3"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-6">
          <v-spacer />
          <v-btn color="grey" variant="text" @click="closeDialog">
            取消
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="saving"
            @click="saveCourse"
          >
            {{ isEdit ? '更新' : '添加' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="mr-3" color="error">mdi-delete</v-icon>
          确认删除
        </v-card-title>
        <v-card-text>
          确定要删除课程 "{{ deleteItem?.course_name }}" 吗？此操作不可撤销。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="deleteDialog = false">
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="confirmDelete"
          >
            删除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
const saving = ref(false)
const deleting = ref(false)
const courses = ref([])
const teachers = ref([])
const search = ref('')
const typeFilter = ref('')
const teacherFilter = ref('')

const dialog = ref(false)
const deleteDialog = ref(false)
const valid = ref(false)
const isEdit = ref(false)
const form = ref(null)

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const deleteItem = ref(null)

const editedCourse = ref({
  course_id: '',
  course_name: '',
  credits: null,
  type: '',
  teacher_id: '',
  max_enrollment: null,
  description: ''
})

const defaultCourse = {
  course_id: '',
  course_name: '',
  credits: null,
  type: '',
  teacher_id: '',
  max_enrollment: null,
  description: ''
}

const headers = [
  { title: '课程编号', key: 'course_id', sortable: true },
  { title: '课程名称', key: 'course_name', sortable: true },
  { title: '学分', key: 'credits', sortable: true },
  { title: '类型', key: 'type', sortable: true },
  { title: '授课教师', key: 'teacher_name', sortable: true },
  { title: '选课情况', key: 'enrollment_status', sortable: false },
  { title: '操作', key: 'actions', sortable: false, width: 120 }
]

const typeOptions = [
  { title: '必修', value: '必修' },
  { title: '选修', value: '选修' },
  { title: '通识', value: '通识' }
]

const teacherOptions = computed(() => 
  teachers.value.map(teacher => ({
    title: teacher.name,
    value: teacher.teacher_id
  }))
)

const filteredCourses = computed(() => {
  let filtered = courses.value

  if (search.value) {
    filtered = filtered.filter(course =>
      course.course_name.includes(search.value) ||
      course.course_id.includes(search.value) ||
      course.teacher_name.includes(search.value)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(course => course.type === typeFilter.value)
  }

  if (teacherFilter.value) {
    filtered = filtered.filter(course => course.teacher_id === teacherFilter.value)
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

const loadCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/courses')
    courses.value = response
  } catch (error) {
    showMessage('加载课程列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    const response = await api.get('/admin/teachers')
    teachers.value = response
  } catch (error) {
    showMessage('加载教师列表失败', 'error')
  }
}

const openAddDialog = () => {
  isEdit.value = false
  editedCourse.value = { ...defaultCourse }
  dialog.value = true
}

const editCourse = (course) => {
  isEdit.value = true
  editedCourse.value = { ...course }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  form.value?.reset()
}

const saveCourse = async () => {
  if (!valid.value) return

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/courses/${editedCourse.value.course_id}`, editedCourse.value)
      showMessage('课程信息更新成功', 'success')
    } else {
      await api.post('/admin/courses', editedCourse.value)
      showMessage('课程添加成功', 'success')
    }
    closeDialog()
    loadCourses()
  } catch (error) {
    showMessage(error.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const deleteCourse = (course) => {
  deleteItem.value = course
  deleteDialog.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.delete(`/admin/courses/${deleteItem.value.course_id}`)
    showMessage('课程删除成功', 'success')
    deleteDialog.value = false
    loadCourses()
  } catch (error) {
    showMessage(error.message || '删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

const showMessage = (text, color = 'success') => {
  message.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadCourses()
  loadTeachers()
})
</script>
