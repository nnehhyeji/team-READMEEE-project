<script setup>
import { Check, ArrowRight } from 'lucide-vue-next'

defineProps({
  provider: {
    type: String,
    default: 'Email'
  },
  message: {
    type: String,
    default: ''
  }
})

defineEmits(['confirm'])
</script>

<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
    <div class="bg-white rounded-3xl w-full max-w-sm p-8 shadow-2xl flex flex-col items-center text-center animate-scale-up">
      
      <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
        <Check class="w-8 h-8 text-primary-600 stroke-[3]" />
      </div>

      <h2 class="text-2xl font-bold text-gray-800 mb-2">로그인 성공!</h2>
      <p class="text-gray-500 mb-8">
        {{ message || (provider === 'email' ? '이메일 로그인이 완료되었습니다.' : `${provider} 로그인이 완료되었습니다.`) }}<br>
      </p>

      <button 
        @click="$emit('confirm')" 
        class="w-full bg-primary-500 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-primary-600 hover:scale-[1.02] transition-all flex items-center justify-center gap-2 active:scale-95"
      >
        <span>시작하기</span>
        <ArrowRight class="w-5 h-5" />
      </button>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

.animate-scale-up {
  animation: scaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { 
    opacity: 0;
    transform: scale(0.9);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}
</style>
