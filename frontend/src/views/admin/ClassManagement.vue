<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon class="mr-3">mdi-school</v-icon>
              <span class="text-h5">班级管理</span>
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">
              添加班级
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜索 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="search"
                  label="搜索班级"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>            <!-- 数据表格 -->
            <CrudDataTable
              title=""
              :headers="headers"
              :items="filteredClasses"
              :loading="loading"
              item-value="class_id"
              enable-add
              @add-item="openAddDialog"
              @edit-item="editClass"
              @delete-item="deleteClass"
            >
              <!-- 自定义学生人数列显示 -->
              <template #item.student_count="{ value }">
                <v-chip color="primary" size="small">
                  {{ value || 0 }} 人
                </v-chip>
              </template>
              
              <!-- 自定义操作列显示 -->
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  color="info"
                  variant="text"
                  @click="viewStudents(item)"
                  title="查看学生"
                />
              </template>
            </CrudDataTable>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 添加/编辑对话框 -->
    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card>
        <v-card-title class="text-h6 pa-6">
          <v-icon class="mr-3">{{ isEdit ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
          {{ isEdit ? '编辑班级' : '添加班级' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="valid" @submit.prevent="saveClass">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedClass.class_id"
                  label="班级编号"
                  variant="outlined"
                  :rules="[v => !!v || '班级编号不能为空']"
                  :disabled="isEdit"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedClass.class_name"
                  label="班级名称"
                  variant="outlined"
                  :rules="[v => !!v || '班级名称不能为空']"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="editedClass.description"
                  label="班级描述"
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
            @click="saveClass"
          >
            {{ isEdit ? '更新' : '添加' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 学生列表对话框 -->
    <v-dialog v-model="studentsDialog" max-width="800px">
      <v-card>
        <v-card-title class="text-h6 pa-6">
          <v-icon class="mr-3">mdi-account-group</v-icon>
          {{ selectedClass?.class_name }} - 学生列表
        </v-card-title>

        <v-card-text class="pa-6">
          <v-data-table
            :headers="studentHeaders"
            :items="classStudents"
            :loading="studentsLoading"
            item-value="student_id"
            class="elevation-1"
          >
            <template #item.total_credits="{ item }">
              {{ item.total_credits || 0 }} 学分
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

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="mr-3" color="error">mdi-delete</v-icon>
          确认删除
        </v-card-title>
        <v-card-text>
          确定要删除班级 "{{ deleteItem?.class_name }}" 吗？此操作不可撤销。
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
const studentsLoading = ref(false)
const classes = ref([])
const classStudents = ref([])
const search = ref('')

const dialog = ref(false)
const studentsDialog = ref(false)
const deleteDialog = ref(false)
const valid = ref(false)
const isEdit = ref(false)
const form = ref(null)

const snackbar = ref(false)
const message = ref('')
const snackbarColor = ref('success')

const deleteItem = ref(null)
const selectedClass = ref(null)

const editedClass = ref({
  class_id: '',
  class_name: '',
  description: ''
})

const defaultClass = {
  class_id: '',
  class_name: '',
  description: ''
}

const headers = [
  { title: '班级编号', key: 'class_id', sortable: true },
  { title: '班级名称', key: 'class_name', sortable: true },
  { title: '学生人数', key: 'student_count', sortable: true },
  { title: '描述', key: 'description', sortable: false },
  { title: '操作', key: 'actions', sortable: false, width: 150 }
]

const studentHeaders = [
  { title: '学号', key: 'student_id', sortable: true },
  { title: '姓名', key: 'name', sortable: true },
  { title: '性别', key: 'gender', sortable: true },
  { title: '年龄', key: 'age', sortable: true },
  { title: '生源所在地', key: 'hometown', sortable: true },
  { title: '已修学分', key: 'total_credits', sortable: true }
]

const filteredClasses = computed(() => {
  const classArray = Array.isArray(classes.value) ? classes.value : []
  if (!search.value) return classArray

  return classArray.filter(cls =>
    cls.class_name.includes(search.value) ||
    cls.class_id.includes(search.value) ||
    cls.description?.includes(search.value)
  )
})

const loadClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/classes')
    classes.value = response.classes || []
  } catch (error) {
    showMessage('加载班级列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const loadClassStudents = async (classId) => {
  studentsLoading.value = true
  try {
    const response = await api.get(`/admin/classes/${classId}/students`)
    classStudents.value = response.students || []
  } catch (error) {
    showMessage('加载学生列表失败', 'error')
  } finally {
    studentsLoading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  editedClass.value = { ...defaultClass }
  dialog.value = true
}

const editClass = (cls) => {
  isEdit.value = true
  editedClass.value = { ...cls }
  dialog.value = true
}

const viewStudents = (cls) => {
  selectedClass.value = cls
  studentsDialog.value = true
  loadClassStudents(cls.class_id)
}

const closeDialog = () => {
  dialog.value = false
  form.value?.reset()
}

const saveClass = async () => {
  if (!valid.value) return

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/classes/${editedClass.value.class_id}`, editedClass.value)
      showMessage('班级信息更新成功', 'success')
    } else {
      await api.post('/admin/classes', editedClass.value)
      showMessage('班级添加成功', 'success')
    }
    closeDialog()
    loadClasses()
  } catch (error) {
    showMessage(error.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const deleteClass = (cls) => {
  deleteItem.value = cls
  deleteDialog.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.delete(`/admin/classes/${deleteItem.value.class_id}`)
    showMessage('班级删除成功', 'success')
    deleteDialog.value = false
    loadClasses()
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
  loadClasses()
})
</script>
