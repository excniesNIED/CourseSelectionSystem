import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 导入页面组件
import Login from '@/views/Login.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import TeacherDashboard from '@/views/teacher/Dashboard.vue'
import StudentDashboard from '@/views/student/Dashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, userType: 'admin' },
    children: [
      {
        path: '',
        name: 'AdminDefault',
        redirect: '/admin/overview'
      },
      {
        path: 'overview',
        name: 'AdminOverview',
        component: () => import('@/views/admin/Overview.vue')
      },
      {
        path: 'teachers',
        name: 'TeacherManagement',
        component: () => import('@/views/admin/TeacherManagement.vue')
      },
      {
        path: 'students',
        name: 'StudentManagement',
        component: () => import('@/views/admin/StudentManagement.vue')
      },
      {
        path: 'courses',
        name: 'CourseManagement',
        component: () => import('@/views/admin/CourseManagement.vue')
      },
      {
        path: 'classes',
        name: 'ClassManagement',
        component: () => import('@/views/admin/ClassManagement.vue')
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/common/Profile.vue')
      }
    ]
  },  {
    path: '/teacher',
    name: 'TeacherDashboard',
    component: TeacherDashboard,
    meta: { requiresAuth: true, userType: 'teacher' },
    children: [
      {
        path: '',
        name: 'TeacherDefault',
        redirect: '/teacher/overview'
      },
      {
        path: 'overview',
        name: 'TeacherOverview',
        component: () => import('@/views/teacher/Overview.vue')
      },
      {
        path: 'courses',
        name: 'TeacherCourses',
        component: () => import('@/views/teacher/Courses.vue')
      },
      {
        path: 'students',
        name: 'TeacherStudents',
        component: () => import('@/views/teacher/Students.vue')
      },
      {
        path: 'grades',
        name: 'GradeManagement',
        component: () => import('@/views/teacher/Grades.vue')
      },
      {
        path: 'statistics',
        name: 'TeacherStatistics',
        component: () => import('@/views/teacher/Statistics.vue')
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: () => import('@/views/common/Profile.vue')
      }
    ]
  },  {
    path: '/student',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, userType: 'student' },
    children: [
      {
        path: '',
        name: 'StudentDefault',
        redirect: '/student/overview'
      },
      {
        path: 'overview',
        name: 'StudentOverview',
        component: () => import('@/views/student/Overview.vue')
      },
      {
        path: 'courses',
        name: 'StudentCourses',
        component: () => import('@/views/student/Courses.vue')
      },
      {
        path: 'enrollment',
        name: 'CourseEnrollment',
        component: () => import('@/views/student/Enrollment.vue')
      },
      {
        path: 'grades',
        name: 'StudentGrades',
        component: () => import('@/views/student/Grades.vue')
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('@/views/common/Profile.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  if (!authStore.isAuthenticated && authStore.token) {
    authStore.initAuth()
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }

    // 检查用户类型权限
    if (to.meta.userType && authStore.userType !== to.meta.userType) {
      // 根据用户类型重定向到对应的仪表板
      const redirectMap = {
        admin: '/admin',
        teacher: '/teacher',
        student: '/student'
      }
      next(redirectMap[authStore.userType] || '/login')
      return
    }
  }

  // 如果已登录用户访问登录页，重定向到对应仪表板
  if (to.name === 'Login' && authStore.isAuthenticated) {
    const redirectMap = {
      admin: '/admin',
      teacher: '/teacher',
      student: '/student'
    }
    next(redirectMap[authStore.userType] || '/')
    return
  }

  next()
})

export default router
