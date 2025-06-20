<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-account-group</v-icon>
              <span class="text-h5">学生管理</span>
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">
              添加学生
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜索和筛选 -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="search"
                  label="搜索学生"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="classFilter"
                  :items="classOptions"
                  label="班级筛选"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="genderFilter"
                  :items="genderOptions"
                  label="性别筛选"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- 数据表格 -->
            <v-data-table
              :headers="headers"
              :items="filteredStudents"
              :loading="loading"
              item-value="student_id"
              class="elevation-1"
            >
              <template #item.total_credits="{ item }">
                {{ item.total_credits || 0 }} 学分
              </template>
              
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  color="primary"
                  variant="text"
                  @click="editStudent(item)"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  variant="text"
                  @click="deleteStudent(item)"
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
          {{ isEdit ? '编辑学生' : '添加学生' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="valid" @submit.prevent="saveStudent">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedStudent.student_id"
                  label="学号"
                  variant="outlined"
                  :rules="[v => !!v || '学号不能为空']"
                  :disabled="isEdit"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedStudent.name"
                  label="姓名"
                  variant="outlined"
                  :rules="[v => !!v || '姓名不能为空']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedStudent.gender"
                  :items="genderOptions"
                  label="性别"
                  variant="outlined"
                  :rules="[v => !!v || '请选择性别']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedStudent.age"
                  label="年龄"
                  type="number"
                  variant="outlined"
                  :rules="[v => !!v || '年龄不能为空', v => v > 0 || '年龄必须大于0']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedStudent.hometown"
                  label="生源所在地"
                  variant="outlined"
                  :rules="[v => !!v || '生源所在地不能为空']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedStudent.class_id"
                  :items="classOptions"
                  label="班级"
                  variant="outlined"
                  :rules="[v => !!v || '请选择班级']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedStudent.total_credits"
                  label="已修学分"
                  type="number"
                  variant="outlined"
                  suffix="学分"
                  :rules="[v => v >= 0 || '学分不能为负数']"
                />
              </v-col>
              <v-col cols="12" sm="6" v-if="!isEdit">
                <v-text-field
                  v-model="editedStudent.password"
                  label="初始密码"
                  type="password"
                  variant="outlined"
                  :rules="[v => !!v || '密码不能为空', v => v.length >= 6 || '密码至少6个字符']"
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
            @click="saveStudent"
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
          确定要删除学生 "{{ deleteItem?.name }}" 吗？此操作不可撤销。
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
const students = ref([])
const classes = ref([])
const search = ref('')
const classFilter = ref('')
const genderFilter = ref('')

const dialog = ref(false)
const deleteDialog = ref(false)
const valid = ref(false)
const isEdit = ref(false)
const form = ref(null)

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const deleteItem = ref(null)

const editedStudent = ref({
  student_id: '',
  name: '',
  gender: '',
  age: null,
  hometown: '',
  class_id: '',
  total_credits: 0,
  password: ''
})

const defaultStudent = {
  student_id: '',
  name: '',
  gender: '',
  age: null,
  hometown: '',
  class_id: '',
  total_credits: 0,
  password: ''
}

const headers = [
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '性别', key: 'gender', sortable: true },
  { title: '年龄', key: 'age', sortable: true },
  { title: '生源所在地', key: 'hometown', sortable: true },
  { title: '班级', key: 'class_name', sortable: true },
  { title: '已修学分', key: 'total_credits', sortable: true },
  { title: '操作', key: 'actions', sortable: false, width: 120 }
]

const genderOptions = [
  { title: '男', value: '男' },
  { title: '女', value: '女' }
]

const classOptions = computed(() => 
  classes.value.map(cls => ({
    title: cls.class_name,
    value: cls.class_id
  }))
)

const filteredStudents = computed(() => {
  let filtered = students.value

  if (search.value) {
    filtered = filtered.filter(student =>
      student.name.includes(search.value) ||
      student.student_id.includes(search.value) ||
      student.hometown.includes(search.value)
    )
  }

  if (classFilter.value) {
    filtered = filtered.filter(student => student.class_id === classFilter.value)
  }

  if (genderFilter.value) {
    filtered = filtered.filter(student => student.gender === genderFilter.value)
  }

  return filtered
})

const loadStudents = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/students')
    students.value = response
  } catch (error) {
    showMessage('加载学生列表失败', 'error')
  } finally {
    loading.value = false
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

const openAddDialog = () => {
  isEdit.value = false
  editedStudent.value = { ...defaultStudent }
  dialog.value = true
}

const editStudent = (student) => {
  isEdit.value = true
  editedStudent.value = { ...student }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  form.value?.reset()
}

const saveStudent = async () => {
  if (!valid.value) return

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/students/${editedStudent.value.student_id}`, editedStudent.value)
      showMessage('学生信息更新成功', 'success')
    } else {
      await api.post('/admin/students', editedStudent.value)
      showMessage('学生添加成功', 'success')
    }
    closeDialog()
    loadStudents()
  } catch (error) {
    showMessage(error.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const deleteStudent = (student) => {
  deleteItem.value = student
  deleteDialog.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.delete(`/admin/students/${deleteItem.value.student_id}`)
    showMessage('学生删除成功', 'success')
    deleteDialog.value = false
    loadStudents()
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
  loadStudents()
  loadClasses()
})
</script>
