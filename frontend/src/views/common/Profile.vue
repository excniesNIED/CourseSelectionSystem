<template>
  <v-container fluid class="profile-container">
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="profile-card">
          <v-card-title class="text-h5 pa-6">
            <v-icon class="mr-3">mdi-account-circle</v-icon>
            个人信息
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="profileForm" v-model="profileValid">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.id"
                    :label="getIdLabel()"
                    prepend-inner-icon="mdi-identifier"
                    variant="outlined"
                    readonly
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.name"
                    label="姓名"
                    prepend-inner-icon="mdi-account"
                    variant="outlined"
                    readonly
                  />
                </v-col>
              </v-row>

              <v-row v-if="authStore.userType !== 'admin'">
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.gender"
                    label="性别"
                    prepend-inner-icon="mdi-gender-male-female"
                    variant="outlined"
                    readonly
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.age"
                    label="年龄"
                    prepend-inner-icon="mdi-calendar"
                    variant="outlined"
                    readonly
                  />
                </v-col>
              </v-row>

              <!-- 教师特有字段 -->
              <v-row v-if="authStore.userType === 'teacher'">
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.title"
                    label="职称"
                    prepend-inner-icon="mdi-account-tie"
                    variant="outlined"
                    readonly
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.phone"
                    label="电话"
                    prepend-inner-icon="mdi-phone"
                    variant="outlined"
                    readonly
                  />
                </v-col>
              </v-row>

              <!-- 学生特有字段 -->
              <v-row v-if="authStore.userType === 'student'">
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.hometown"
                    label="生源所在地"
                    prepend-inner-icon="mdi-map-marker"
                    variant="outlined"
                    readonly
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.total_credits"
                    label="已修学分"
                    prepend-inner-icon="mdi-trophy"
                    variant="outlined"
                    readonly
                    suffix="学分"
                  />
                </v-col>
              </v-row>

              <v-row v-if="authStore.userType === 'student'">
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.class_id"
                    label="班级编号"
                    prepend-inner-icon="mdi-account-group"
                    variant="outlined"
                    readonly
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profile.class_name"
                    label="班级名称"
                    prepend-inner-icon="mdi-school"
                    variant="outlined"
                    readonly
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>        <!-- 修改密码卡片 -->
        <v-card class="mt-6 password-card">
          <v-card-title class="text-h6 pa-6">
            <v-icon class="mr-3">mdi-lock-reset</v-icon>
            修改密码
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="passwordFormRef" v-model="passwordValid" @submit.prevent="changePassword">
              <v-text-field
                v-model="passwordForm.old_password"
                label="当前密码"
                prepend-inner-icon="mdi-lock"
                :type="showOldPassword ? 'text' : 'password'"
                :append-inner-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showOldPassword = !showOldPassword"
                variant="outlined"
                :rules="passwordRules"
                class="mb-3"
              />

              <v-text-field
                v-model="passwordForm.new_password"
                label="新密码"
                prepend-inner-icon="mdi-lock-plus"
                :type="showNewPassword ? 'text' : 'password'"
                :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showNewPassword = !showNewPassword"
                variant="outlined"
                :rules="newPasswordRules"
                class="mb-3"
              />

              <v-text-field
                v-model="passwordForm.confirm_password"
                label="确认新密码"
                prepend-inner-icon="mdi-lock-check"
                :type="showConfirmPassword ? 'text' : 'password'"
                :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
                variant="outlined"
                :rules="confirmPasswordRules"
                class="mb-4"
              />              <v-btn
                type="submit"
                color="primary"
                :loading="passwordLoading"
                :disabled="!passwordValid"
                block
                class="change-password-btn"
              >
                修改密码
              </v-btn>
            </v-form>

            <v-alert
              v-if="passwordMessage"
              :type="passwordMessageType"
              variant="tonal"
              class="mt-4"
              closable
              @click:close="passwordMessage = ''"
            >
              {{ passwordMessage }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()

const profileForm = ref(null)
const passwordFormRef = ref(null)
const profileValid = ref(false)
const passwordValid = ref(false)
const passwordLoading = ref(false)

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const passwordMessage = ref('')
const passwordMessageType = ref('success')

const profile = reactive({
  id: '',
  name: '',
  gender: '',
  age: '',
  title: '',
  phone: '',
  hometown: '',
  total_credits: '',
  class_id: '',
  class_name: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = [
  v => !!v || '密码不能为空',
  v => v.length >= 6 || '密码至少6个字符'
]

const newPasswordRules = [
  v => !!v || '新密码不能为空',
  v => v.length >= 6 || '新密码至少6个字符',
  v => v !== passwordForm.old_password || '新密码不能与当前密码相同'
]

const confirmPasswordRules = [
  v => !!v || '请确认新密码',
  v => v === passwordForm.new_password || '两次输入的密码不一致'
]

const getIdLabel = () => {
  const labels = {
    admin: '管理员编号',
    teacher: '教师编号',
    student: '学号'
  }
  return labels[authStore.userType] || 'ID'
}

const loadProfile = async () => {
  try {
    let endpoint = ''
    if (authStore.userType === 'teacher') {
      endpoint = '/teacher/profile'
    } else if (authStore.userType === 'student') {
      endpoint = '/student/profile'
    } else {
      // 管理员直接从store获取
      Object.assign(profile, authStore.user)
      return
    }

    const response = await api.get(endpoint)
    Object.assign(profile, response)
  } catch (error) {
    console.error('加载个人信息失败:', error)
  }
}

const changePassword = async () => {
  if (!passwordValid.value) return

  passwordLoading.value = true
  passwordMessage.value = ''

  try {
    await authStore.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    passwordMessage.value = '密码修改成功'
    passwordMessageType.value = 'success'
    
    // 清空表单
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    passwordFormRef.value?.reset()
  } catch (error) {
    passwordMessage.value = error.message || '密码修改失败'
    passwordMessageType.value = 'error'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 16px;
  min-height: 100%;
  overflow-y: auto;
}

.profile-card, .password-card {
  max-width: 100%;
  margin: 0 auto;
}

/* 确保在小屏幕设备上的良好显示 */
@media (max-width: 768px) {
  .profile-container {
    padding: 8px;
  }
  
  .v-card-title {
    padding: 16px !important;
    font-size: 1.2rem !important;
  }
  
  .v-card-text {
    padding: 16px !important;
  }
  
  .v-col {
    padding: 4px 8px !important;
  }
}

/* 确保表单元素在窄屏时不会溢出 */
.v-text-field {
  width: 100%;
}

/* 为按钮添加适当的间距和动画 */
.v-btn {
  margin-top: 8px;
}

.change-password-btn {
  transition: all 0.2s ease-in-out;
}

.change-password-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(21, 173, 102, 0.3);
}

.change-password-btn:active {
  transform: translateY(0);
}
</style>
