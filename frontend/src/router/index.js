import { createRouter, createWebHistory } from 'vue-router'
import MainFeed from '../views/MainFeed.vue'
import LandingView from '../views/LandingView.vue'
import BestAnswers from '../views/BestAnswers.vue'
import ProfilePage from '../views/ProfilePage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import AuthPage from '../views/AuthPage.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView
  },
  {
    path: '/feed',
    name: 'feed',
    component: MainFeed
  },
  {
    path: '/best',
    name: 'best',
    component: BestAnswers
  },
  {
    path: '/profile/:username?',
    name: 'profile',
    component: ProfilePage,
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/auth',
    name: 'auth',
    component: AuthPage
  },
  {
    path: '/google/callback',
    name: 'google-callback',
    component: () => import('../views/GoogleCallback.vue')
  },
  {
    path: '/login/callback',
    name: 'google-callback-legacy', // 유저가 현재 설정한 경로 지원
    component: () => import('../views/GoogleCallback.vue')
  },
  {
    path: '/naver/callback',
    name: 'naver-callback',
    component: () => import('../views/NaverCallback.vue')
  },
  {
    path: '/login/naver/callback',
    name: 'naver-callback-legacy',
    component: () => import('../views/NaverCallback.vue')
  },
  {
    path: '/login/kakao/callback',
    name: 'kakao-callback',
    component: () => import('../views/KakaoCallback.vue')
  },
  {
    path: '/test-dots',
    name: 'test-dots',
    component: () => import('../views/TestConnectingDots.vue')
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 전역 가드
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.')
    next('/auth')
  } else {
    next()
  }
})

export default router