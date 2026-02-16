import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/api/axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const useAuthStore = defineStore('auth', () => {
  // 1. 상태 (State)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const currentUser = ref(JSON.parse(localStorage.getItem('user_info')) || null)

  // 2. 게터 (Getters)
  const isAuthenticated = computed(() => !!accessToken.value)

  // 프로필 이미지 전체 경로를 반환하는 새로운 게터 추가
  const profileImageUrl = computed(() => {
    if (!currentUser.value || !currentUser.value.profile_image) {
      // 이미지가 없는 경우 기본 아바타 반환
      return `https://ui-avatars.com/api/?name=${currentUser.value?.username || 'User'}`
    }

    const path = currentUser.value.profile_image
    // 1. http로 시작하면(Signed URL 등) 그대로 반환
    if (path.startsWith('http')) return path

    // 2. uploads/ 로 시작하면 Supabase Path인데 Signed URL 변환 실패한 경우일 수 있음
    // 이 경우 백엔드에서 Signed URL을 못 받았다는 뜻이므로, fallback 이미지나 재요청 필요하지만
    // 일단 API_BASE_URL 붙이는 건 의미 없으므로 제외 (또는 특정 처리)
    if (path.startsWith('uploads/')) {
      // 임시: 변환 실패 시 기본 이미지
      return `https://ui-avatars.com/api/?name=${currentUser.value?.username || 'User'}`
    }

    // 3. 그 외(로컬 미디어 경로 등)는 백엔드 주소 결합
    return `${API_BASE_URL}${path}`
  })

  // 3. 액션 (Actions)

  // [로그인] 백엔드 응답 구조: { user: {...}, tokens: { access: "...", refresh: "..." } }
  const login = async (credentials) => {
    try {
      const response = await axios.post('/accounts/login/', credentials)

      const userData = response.data.user
      const access = response.data.tokens.access
      const refresh = response.data.tokens.refresh

      accessToken.value = access
      refreshToken.value = refresh
      currentUser.value = userData

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user_info', JSON.stringify(userData))


      return true
    } catch (error) {
      console.error('Login error:', error.response?.data)
      throw error
    }
  }

  // [회원가입] 백엔드 필드: email, username, password, password_confirm
  const signup = async (formData) => {
    try {
      const response = await axios.post('/accounts/register/', {
        email: formData.email,
        username: formData.username,
        password: formData.password,
        // 백엔드 시리얼라이저가 password_confirm을 필수 체크
        password_confirm: formData.password_confirm || formData.password
      })

      const userData = response.data.user
      const access = response.data.tokens.access
      const refresh = response.data.tokens.refresh

      accessToken.value = access
      refreshToken.value = refresh
      currentUser.value = userData

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user_info', JSON.stringify(userData))

      return true
    } catch (error) {
      console.error('Signup error:', error.response?.data)
      throw error
    }
  }

  // [내 정보 수정] 백엔드 경로: /api/accounts/profile/update/
  const updateProfile = async (updateData) => {
    try {
      // FormData 형식을 지원하기 위해 PATCH 요청
      const response = await axios.patch('/accounts/profile/update/', updateData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // 수정된 정보로 스토어 및 로컬스토리지 갱신
      currentUser.value = response.data
      localStorage.setItem('user_info', JSON.stringify(response.data))
      return true
    } catch (error) {
      console.error('Profile update error:', error.response?.data)
      return false
    }
  }

  // [비밀번호 변경] 백엔드 경로: /accounts/password/change/
  const changePassword = async (passwordData) => {
    try {
      await axios.post('/accounts/password/change/', passwordData)
      return true
    } catch (error) {
      console.error('Password change error:', error.response?.data)
      throw error
    }
  }

  // [회원탈퇴] 백엔드 경로: /accounts/withdraw/
  const withdraw = async () => {
    try {
      await axios.delete('/accounts/withdraw/')
      // 탈퇴 성공 시 로컬 정보도 삭제
      accessToken.value = null
      refreshToken.value = null
      currentUser.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      return true
    } catch (error) {
      console.error('Withdraw error:', error.response?.data)
      return false
    }
  }

  // 현재 로그인한 유저 정보 새로고침
  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/accounts/profile/my/')
      currentUser.value = response.data
      localStorage.setItem('user_info', JSON.stringify(response.data))
      return true
    } catch (error) {
      console.error('Fetch current user error:', error)
      return false
    }
  }

  const logout = async () => {
    try {
      // 서버에 로그아웃 요청 (토큰 블랙리스트 등 처리)
      // 실패하더라도 클라이언트 로그아웃은 진행되어야 함
      await axios.post('/accounts/logout/')
    } catch (error) {
      console.warn('Backend logout failed:', error)
    } finally {
      // 클라이언트 상태 초기화
      accessToken.value = null
      refreshToken.value = null
      currentUser.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    }
  }

  // 소셜 로그인
  const socialLogin = async (provider, data) => {
    try {
      const payload = typeof data === 'string' ? { code: data } : data

      const response = await axios.post(`/accounts/${provider}/callback/`, payload)

      const userData = response.data.user
      const access = response.data.tokens.access
      const refresh = response.data.tokens.refresh

      accessToken.value = access
      refreshToken.value = refresh
      currentUser.value = userData

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user_info', JSON.stringify(userData))

      return response.data
    } catch (error) {
      console.error('Social login error:', error.response?.data)
      throw error
    }
  }

  return {
    accessToken, currentUser, isAuthenticated, profileImageUrl,
    login, logout, signup, updateProfile, changePassword, withdraw, fetchCurrentUser,
    socialLogin
  }
})