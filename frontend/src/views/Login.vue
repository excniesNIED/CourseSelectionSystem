<template>
  <v-container fluid class="fill-height login-container">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="elevation-8 login-card">
          <v-card-title class="text-center pa-6">
            <div class="login-header">
              <v-icon size="48" color="primary" class="mb-2">mdi-school</v-icon>
              <h1 class="text-h4 font-weight-bold">教务系统</h1>
              <p class="text-body-1 text-medium-emphasis">选课管理平台</p>
            </div>
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
              <v-text-field
                v-model="loginForm.username"
                label="用户名/学号/工号"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="usernameRules"
                required
                class="mb-3"
              />

              <v-text-field
                v-model="loginForm.password"
                label="密码"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                :rules="passwordRules"
                required
                class="mb-3"
              />

              <v-select
                v-model="loginForm.user_type"
                label="用户类型"
                prepend-inner-icon="mdi-account-group"
                :items="userTypes"
                item-title="label"
                item-value="value"
                variant="outlined"
                :rules="userTypeRules"
                required
                class="mb-4"
              />              
              <v-btn
                type="button"
                block
                size="large"
                color="primary"
                :loading="loading"
                :disabled="!valid || !canSubmit || countdown > 0"
                class="mb-3"
                @click="handleSubmit"
              >
                <span v-if="countdown > 0">
                  请等待 {{ countdown }} 秒后重试
                </span>
                <span v-else>登录</span>
              </v-btn>
            </v-form>

            <v-alert
              v-if="errorMessage"
              type="error"
              variant="tonal"
              class="mt-3"
              closable
              @click:close="errorMessage = ''"
            >
              {{ errorMessage }}
            </v-alert>
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-spacer />
            <div class="text-caption text-medium-emphasis">
              <v-chip size="small" color="primary" variant="outlined" class="mr-2">
                <v-icon start>mdi-account-circle</v-icon>
                管理员: admin / admin123
              </v-chip>
              <br class="mb-2">
              <v-chip size="small" color="secondary" variant="outlined" class="mr-2">
                <v-icon start>mdi-account-tie</v-icon>
                教师: T001 / teacher123
              </v-chip>
              <br class="mb-2">
              <v-chip size="small" color="tertiary" variant="outlined">
                <v-icon start>mdi-account-school</v-icon>
                学生: 202301001001 / student123
              </v-chip>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref(null)
const valid = ref(false)
const loading = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')
const countdown = ref(0)
const canSubmit = ref(true)
const lastSubmitTime = ref(0) // 添加最后提交时间记录

let countdownTimer = null

// 强制重置所有状态
const resetLoginState = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
  canSubmit.value = true
  loading.value = false
  errorMessage.value = ''
}

// 组件销毁时清理计时器
onUnmounted(() => {
  resetLoginState()
})

const loginForm = reactive({
  username: '',
  password: '',
  user_type: 'student'
})

const userTypes = [
  { label: '学生', value: 'student' },
  { label: '教师', value: 'teacher' },
  { label: '管理员', value: 'admin' }
]

const usernameRules = [
  v => !!v || '用户名不能为空',
  v => v.length >= 2 || '用户名至少2个字符'
]

const passwordRules = [
  v => !!v || '密码不能为空',
  v => v.length >= 6 || '密码至少6个字符'
]

const userTypeRules = [
  v => !!v || '请选择用户类型'
]

const handleSubmit = (e) => {
  if (e) {
    e.preventDefault()
    e.stopPropagation()
  }
  
  const currentTime = Date.now()
  
  console.log('handleSubmit called:', {
    valid: valid.value,
    canSubmit: canSubmit.value,
    countdown: countdown.value,
    loading: loading.value,
    timeSinceLastSubmit: currentTime - lastSubmitTime.value
  })
  
  // 防抖：1秒内只能提交一次
  if (currentTime - lastSubmitTime.value < 1000) {
    console.log('提交过于频繁，被阻止')
    return false
  }
  
  if (!valid.value || !canSubmit.value || countdown.value > 0 || loading.value) {
    console.log('提交被阻止')
    return false
  }
  
  lastSubmitTime.value = currentTime
  login()
  return false
}

const startCountdown = () => {
  console.log('开始倒计时')
  // 清除现有的计时器
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  
  canSubmit.value = false
  countdown.value = 5
  
  countdownTimer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      resetLoginState()
    }
  }, 1000)
}

const login = async () => {
  // 再次检查表单有效性
  const { valid: formIsValid } = await form.value.validate()
  if (!formIsValid) {
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(loginForm)
    
    // 登录成功后，重置状态并导航
    resetLoginState()
    
    const userType = authStore.user.type
    if (userType === 'admin') {
      router.push('/admin/overview')
    } else if (userType === 'teacher') {
      router.push('/teacher/overview')
    } else {
      router.push('/student/overview')
    }
  } catch (error) {
    console.error('登录失败:', error)
    
    // 处理登录失败
    errorMessage.value = error.message || '登录时发生未知错误'
    
    // 如果是密码错误，则开始倒计时
    if (error.message && error.message.includes('用户名或密码错误')) {
      startCountdown()
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #15AD66 0%, #0A7B4A 100%);
  min-height: 100vh;
}

.login-card {
  border-radius: 16px !important;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
}

.v-card-title {
  background: linear-gradient(45deg, #15AD66, #0A7B4A);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}
</style>
