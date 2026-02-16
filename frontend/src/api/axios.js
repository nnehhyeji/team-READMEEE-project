import axios from 'axios'

const instance = axios.create({
  // 1. 백엔드 서버의 기본 주소 
  baseURL: `${import.meta.env.VITE_API_BASE_URL}/api`,
})

// 1. 요청 인터셉터
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')

    // 토큰이 실제로 존재할 때만 Bearer 헤더를 붙이기
    if (token && token !== 'null' && token !== 'undefined') {
      config.headers.Authorization = `Bearer ${token}`
    } else {

      delete config.headers.Authorization
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 2. 응답 인터셉터: 서버의 대답을 가로채서 에러 처리
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    // 서버가 401(권한 없음)을 던지면 = 신분증 만료 혹은 부정확
    if (error.response && error.response.status === 401) {
      console.warn('인증 정보가 만료되어 모든 로컬 데이터를 초기화합니다.')

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    }
    return Promise.reject(error)
  }
)

export default instance