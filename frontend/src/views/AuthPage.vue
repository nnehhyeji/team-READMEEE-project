<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginSuccessModal from '@/components/LoginSuccessModal.vue'
import { useModalStore } from '@/stores/modal' 
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const userStore = useAuthStore()
const modal = useModalStore() 

const isLoginMode = ref(true)
const isLoading = ref(false)
const showSuccessModal = ref(false)
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const form = ref({
  username: '',
  email: '',
  password: ''
})

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  form.value = { username: '', email: '', password: '' }
}

const handleUsernameInput = (e) => {
  form.value.username = e.target.value.replace(/[^a-zA-Z0-9_]/g, '')
}

const handleSubmit = async () => {
  if (!form.value.email || !form.value.password) {
    modal.alert('이메일과 비밀번호를 입력해주세요.', '알림')
    return
  }

  if (!isLoginMode.value && !form.value.username) {
    modal.alert('사용자 아이디를 입력해주세요.', '알림')
    return
  }

  isLoading.value = true

  try {
    if (isLoginMode.value) {
      const success = await userStore.login({
        email: form.value.email,
        password: form.value.password
      })
      if (success) {
        showSuccessModal.value = true
      }
    } else {
      await userStore.signup({ 
        email: form.value.email,
        username: form.value.username,
        password: form.value.password
      })
      modal.success('회원가입이 완료되었습니다! \n이제 로그인해주세요.', '환영합니다')
      isLoginMode.value = true
    }
  } catch (error) {
    console.error('인증 에러:', error)
    const errorDetail = error.response?.data
    if (errorDetail) {
      const firstKey = Object.keys(errorDetail)[0]
      const firstError = errorDetail[firstKey]
      modal.alert(Array.isArray(firstError) ? firstError[0] : firstError, '오류')
    } else {
      modal.alert('서버와의 통신이 원활하지 않습니다.', '오류')
    }
  } finally {
    isLoading.value = false
  }
}

const handleLoginSuccess = () => {
  router.push('/feed')
}
</script>

<template>
  <!-- [Final Fix] 1. Scroll Container: Fixed to viewport, forces internal scrolling -->
  <div class="fixed inset-0 h-screen w-full bg-[#f1f2f6] font-inter overflow-y-auto">
    
    <!-- [Final Fix] 2. Center Wrapper: At least full height to center, grows to allow scrolling -->
    <div class="min-h-full w-full flex flex-col items-center justify-center p-4 py-12">

      <LoginSuccessModal 
        v-if="showSuccessModal" 
        provider="email" 
        @confirm="handleLoginSuccess" 
      />

      <!-- [Final Fix] 3. Card: shrink-0 ensures it never gets crushed -->
      <div class="bg-white w-full max-w-[1000px] h-auto md:min-h-[600px] rounded-[30px] shadow-2xl flex flex-col md:flex-row overflow-hidden animate-fade-in-up shrink-0">
        
        <!-- 1. Left Side: Gradient Brand Area -->
        <div class="w-full md:w-[45%] bg-gradient-to-br from-[#FFF5F5] via-[#FFE3E3] to-[#FEA2A3] p-10 flex flex-col justify-between text-gray-900 relative overflow-hidden">
          <!-- Abstract Decoration Circles -->
          <div class="absolute -top-20 -right-20 w-60 h-60 bg-[#FEA2A3] opacity-30 rounded-full blur-3xl"></div>
          <div class="absolute bottom-10 -left-10 w-40 h-40 bg-[#FFB5B6] opacity-40 rounded-full blur-2xl"></div>
          
          <div>
             <!-- Brand Logo / Name -->
             <div 
               class="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
               @click="router.push('/')"
             >
                <img src="/logo.png" alt="READMEEE Logo" class="w-10 h-10 object-contain drop-shadow-sm" />
                <h3 class="text-lg font-black tracking-tight text-gray-900 font-sans pt-2">READMEEE</h3>
             </div>
          </div>

          <div class="mt-8 md:mt-0 relative z-10">
             <p class="text-sm font-medium opacity-60 mb-3 tracking-wide text-gray-800 uppercase">Your Daily Archive</p>
             <h1 class="text-3xl md:text-4xl font-medium leading-snug tracking-tight text-gray-900 drop-shadow-sm">
               Where your days<br/>
               <span>become a story</span>
             </h1>
          </div>
          
          <div class="hidden md:block opacity-40 text-xs mt-4 font-medium">
            © 2025 READMEEE Platform
          </div>
        </div>

        <!-- 2. Right Side: Login Form -->
        <div class="w-full md:w-[55%] p-8 md:p-12 flex flex-col justify-center bg-white relative">
          <div class="max-w-md mx-auto w-full">
              
            <!-- Icon Header -->
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              {{ isLoginMode ? 'Welcome back' : 'Create an account' }}
            </h2>
            <p class="text-gray-500 text-sm mb-8">
              {{ isLoginMode ? 'Please enter your details to sign in.' : 'Access your tasks, notes, and projects anytime.' }}
            </p>

            <form @submit.prevent="handleSubmit" class="space-y-5">
              
              <div v-if="!isLoginMode" class="space-y-1">
                <label class="text-xs font-bold text-gray-700 ml-1">Username</label>
                <input 
                  v-model="form.username" 
                  @input="handleUsernameInput"
                  type="text" 
                  placeholder="chlo_simpson" 
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 transition-all text-sm placeholder-gray-300" 
                />
              </div>

              <div class="space-y-1">
                <label class="text-xs font-bold text-gray-700 ml-1">Email</label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  placeholder="name@example.com" 
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 transition-all text-sm placeholder-gray-300" 
                />
              </div>

              <div class="space-y-1">
                <label class="text-xs font-bold text-gray-700 ml-1">Password</label>
                <input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="••••••••" 
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 transition-all text-sm placeholder-gray-300" 
                />
              </div>

              <button 
                type="submit" 
                :disabled="isLoading"
                class="w-full bg-[#0F172A] hover:bg-[#1E293B] text-white font-bold py-3.5 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 mt-4"
              >
                <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
                <span>{{ isLoginMode ? 'Sign In' : 'Create account' }}</span>
              </button>

            </form>

            <!-- Social Login Divider -->
            <div class="relative py-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-100"></div>
              </div>
              <div class="relative flex justify-center text-xs">
                <span class="px-2 bg-white text-gray-400">or continue with</span>
              </div>
            </div>

            <!-- Social Icons Row -->
            <div class="flex gap-4 justify-center">
              <!-- Google -->
              <a :href="`${apiBaseUrl}/api/accounts/google/login/`" class="w-14 h-14 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center hover:bg-gray-100 transition-all">
                 <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" class="w-6 h-6" />
              </a>
              
              <!-- Naver (Green) -->
               <a :href="`${apiBaseUrl}/api/accounts/naver/login/`" class="w-14 h-14 rounded-lg bg-[#03C75A]/10 border border-[#03C75A]/20 flex items-center justify-center hover:bg-[#03C75A]/20 transition-all">
                 <span class="font-black text-[#03C75A] text-lg">N</span>
              </a>

              <!-- Kakao (Yellow) -->
               <a :href="`${apiBaseUrl}/api/accounts/kakao/login/`" class="w-14 h-14 rounded-lg bg-[#FEE500]/20 border border-[#FEE500]/50 flex items-center justify-center hover:bg-[#FEE500]/30 transition-all">
                  <svg class="w-6 h-6 text-[#3B1E1E]" viewBox="0 0 24 24" fill="currentColor">
                     <path d="M12 3C5.373 3 0 6.64 0 11.13c0 2.872 2.21 5.438 5.672 6.82v.006L4.66 21c-.083.33.24.587.52.417l5.222-3.328c.518.062 1.05.097 1.597.097 6.628 0 12-3.64 12-8.13C24 6.64 18.628 3 12 3"/>
                  </svg>
              </a>
            </div>

            <div class="mt-8 text-center text-xs text-gray-500">
               {{ isLoginMode ? "Don't have an account?" : "Already have an account?" }}
               <button @click="toggleMode" class="text-[#FF6B6B] font-bold hover:underline ml-1">
                 {{ isLoginMode ? 'Register' : 'Log in' }}
               </button>
            </div>

          </div>
        </div>

      </div>
    
    </div>
  </div>
</template>

<style scoped>
.font-inter {
  font-family: 'Inter', sans-serif;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>