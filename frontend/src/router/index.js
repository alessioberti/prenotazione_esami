import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../views/MainLayout.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ResetPassword from '../views/ResetPassword.vue'
import Home from '../views/HomeView.vue'
import ExamSelection from '../views/ExamSelection.vue'
import BookView from '../views/BookView.vue'
import ManageView from '../views/ManageView.vue'
import { useAuth } from '../composables/useAuth'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: Home
      },
      {
        path: '/book',
        name: 'book',
        component: ExamSelection,
        meta: { requiresAuth: true }
      },
      {
        path: '/slots',
        name: 'slots',
        component: BookView,
        meta: { requiresAuth: true }
      },
      {
        path: '/manage',
        name: 'manage',
        component: ManageView,
        meta: { requiresAuth: true }
      },
      {
        path: '/login',
        name: 'login',
        component: LoginView
      },
      {
        path: '/register',
        name: 'register',
        component: RegisterView
      },
      {
        path: '/reset-password',
        name: 'reset-password',
        component: ResetPassword
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, checkAuth } = useAuth()


  if (to.meta.requiresAuth) {
    try {
      
      await checkAuth()

      if (isLoggedIn.value) {
        next()
      } else {
        next({ name: 'login' })
      }
    } catch (err) {
      console.error('Errore nel controllo autenticazione:', err)
      next({ name: 'login' })
    }
  } else {
    next()
  }
})

export default router
