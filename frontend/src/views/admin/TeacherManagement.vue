<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-account-tie</v-icon>
              <span class="text-h5">教师管理</span>
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">
              添加教师
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜索和筛选 -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="search"
                  label="搜索教师"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="titleFilter"
                  :items="titleOptions"
                  label="职称筛选"
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
            </v-row>            <!-- 数据表格 -->
            <CrudDataTable
              title=""
              :headers="headers"
              :items="filteredTeachers"
              :loading="loading"
              item-value="teacher_id"
              enable-add
              @add-item="openAddDialog"
              @edit-item="editTeacher"
              @delete-item="deleteTeacher"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 添加/编辑对话框 -->
    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-6">
          <v-icon class="mr-3">{{ isEdit ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
          {{ isEdit ? '编辑教师' : '添加教师' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="valid" @submit.prevent="saveTeacher">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedTeacher.teacher_id"
                  label="教师编号"
                  variant="outlined"
                  :rules="[v => !!v || '教师编号不能为空']"
                  :disabled="isEdit"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedTeacher.name"
                  label="姓名"
                  variant="outlined"
                  :rules="[v => !!v || '姓名不能为空']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedTeacher.gender"
                  :items="genderOptions"
                  label="性别"
                  variant="outlined"
                  :rules="[v => !!v || '请选择性别']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedTeacher.age"
                  label="年龄"
                  type="number"
                  variant="outlined"
                  :rules="[v => !!v || '年龄不能为空', v => v > 0 || '年龄必须大于0']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedTeacher.title"
                  :items="titleOptions"
                  label="职称"
                  variant="outlined"
                  :rules="[v => !!v || '请选择职称']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedTeacher.phone"
                  label="电话"
                  variant="outlined"
                  :rules="[v => !!v || '电话不能为空']"
                />
              </v-col>
            </v-row>

            <v-row v-if="!isEdit">
              <v-col cols="12">
                <v-text-field
                  v-model="editedTeacher.password"
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
            @click="saveTeacher"
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
          确定要删除教师 "{{ deleteItem?.name }}" 吗？此操作不可撤销。
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
import CrudDataTable from '@/components/common/CrudDataTable.vue'

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const teachers = ref([])
const search = ref('')
const titleFilter = ref('')
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

const editedTeacher = ref({
  teacher_id: '',
  name: '',
  gender: '',
  age: null,
  title: '',
  phone: '',
  password: ''
})

const defaultTeacher = {
  teacher_id: '',
  name: '',
  gender: '',
  age: null,
  title: '',
  phone: '',
  password: ''
}

const headers = [
  { title: '教师编号', key: 'teacher_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '性别', key: 'gender', sortable: true },
  { title: '年龄', key: 'age', sortable: true },
  { title: '职称', key: 'title', sortable: true },
  { title: '电话', key: 'phone', sortable: false },
  { title: '操作', key: 'actions', sortable: false, width: 120 }
]

const genderOptions = [
  { title: '男', value: '男' },
  { title: '女', value: '女' }
]

const titleOptions = [
  { title: '教授', value: '教授' },
  { title: '副教授', value: '副教授' },
  { title: '讲师', value: '讲师' },
  { title: '助教', value: '助教' }
]

const filteredTeachers = computed(() => {
  let filtered = Array.isArray(teachers.value) ? teachers.value : []

  if (search.value) {
    filtered = filtered.filter(teacher =>
      teacher.name.includes(search.value) ||
      teacher.teacher_id.includes(search.value) ||
      teacher.phone.includes(search.value)
    )
  }

  if (titleFilter.value) {
    filtered = filtered.filter(teacher => teacher.title === titleFilter.value)
  }

  if (genderFilter.value) {
    filtered = filtered.filter(teacher => teacher.gender === genderFilter.value)
  }

  return filtered
})

const loadTeachers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/teachers')
    teachers.value = response.teachers || []
  } catch (error) {
    showMessage('加载教师列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  editedTeacher.value = { ...defaultTeacher }
  dialog.value = true
}

const editTeacher = (teacher) => {
  isEdit.value = true
  editedTeacher.value = { ...teacher }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  form.value?.reset()
}

const saveTeacher = async () => {
  if (!valid.value) return

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/teachers/${editedTeacher.value.teacher_id}`, editedTeacher.value)
      showMessage('教师信息更新成功', 'success')
    } else {
      await api.post('/admin/teachers', editedTeacher.value)
      showMessage('教师添加成功', 'success')
    }
    closeDialog()
    loadTeachers()
  } catch (error) {
    showMessage(error.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const deleteTeacher = (teacher) => {
  deleteItem.value = teacher
  deleteDialog.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.delete(`/admin/teachers/${deleteItem.value.teacher_id}`)
    showMessage('教师删除成功', 'success')
    deleteDialog.value = false
    loadTeachers()
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
  loadTeachers()
})
</script>
