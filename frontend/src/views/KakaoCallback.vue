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
const modalMessage = ref('')

onMounted(async () => {
  const code = route.query.code
  if (!code) {
    alert('잘못된 접근입니다.')
    router.replace('/auth')
    return
  }

  try {
    const res = await authStore.socialLogin('kakao', code)
  
    
    showSuccessModal.value = true
  } catch (error) {
    alert('카카오 로그인 실패: ' + (error.response?.data?.error || '알 수 없는 오류'))
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
      provider="Kakao"
      :message="modalMessage" 
      @confirm="handleConfirm" 
    />

    <Loader2 class="w-10 h-10 text-yellow-500 animate-spin mb-4" />
    <p class="text-gray-600 font-medium">카카오 로그인 처리 중입니다...</p>
  </div>
</template>
