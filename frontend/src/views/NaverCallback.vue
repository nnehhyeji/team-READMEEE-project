<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginSuccessModal from '@/components/LoginSuccessModal.vue'
import { Loader2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const showSuccessModal = ref(false)

onMounted(async () => {
  const code = route.query.code
  const state = route.query.state
  
  if (!code) {
    alert('잘못된 접근입니다.')
    router.replace('/auth')
    return
  }

  try {
    // Naver login logic
    await authStore.socialLogin('naver', { code, state }) 
    
    // Show success modal
    showSuccessModal.value = true
  } catch (error) {
    alert('네이버 로그인 실패: ' + (error.response?.data?.error || '알 수 없는 오류'))
    router.replace('/auth')
  }
})

const handleConfirm = () => {
  router.replace('/feed')
}
</script>

<template>
  <div class="h-screen flex flex-col items-center justify-center bg-gray-50">
    <LoginSuccessModal 
      v-if="showSuccessModal" 
      provider="Naver" 
      @confirm="handleConfirm" 
    />

    <Loader2 class="w-10 h-10 text-green-500 animate-spin mb-4" />
    <p class="text-gray-600 font-medium">네이버 로그인 처리 중입니다...</p>
  </div>
</template>
