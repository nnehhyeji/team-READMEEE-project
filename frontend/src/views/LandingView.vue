<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'
import { useQuestionStore } from '@/stores/question'
import { storeToRefs } from 'pinia'

const router = useRouter()
const questionStore = useQuestionStore()
const { todayQuestion } = storeToRefs(questionStore)

const questionColor = ref('#F4C0D6')
const displayedText = ref('')
const isTyping = ref(false)
const isTypingFinished = ref(false)

const typeText = async (text) => {
  if (!text) return
  isTyping.value = true
  isTypingFinished.value = false
  displayedText.value = ''
  
  // Start with a small pause
  await new Promise(r => setTimeout(r, 500))
  
  for (let i = 0; i < text.length; i++) {
    displayedText.value += text[i]
    // Randomize typing speed slightly for realism
    await new Promise(r => setTimeout(r, Math.random() * 50 + 50))
  }
  isTyping.value = false
  isTypingFinished.value = true
}

onMounted(async () => {
  await questionStore.fetchTodayQuestion()
  if (todayQuestion.value?.content) {
    typeText(todayQuestion.value.content)
  }
  
  // 색상 로테이션 로직 (MainFeed와 동일하게 유지 or Landing 전용으로 분리)
  const colors = ['#F4C0D6', '#F9F18F', '#D3FFC3']
  const savedIndex = sessionStorage.getItem('headerColorIndex')
  let nextIndex = 0
  if (savedIndex !== null) {
    nextIndex = (parseInt(savedIndex) + 1) % colors.length
  }
  questionColor.value = colors[nextIndex]
  sessionStorage.setItem('headerColorIndex', nextIndex.toString())
})

const goFeed = () => {
    router.push('/feed')
}
</script>

<template>
  <div class="h-screen w-full bg-black flex flex-col items-center justify-center relative overflow-hidden">
    <!-- 배경 장식 (심심하지 않게) -->
    <div class="absolute inset-0 bg-gradient-to-b from-transparent to-black/20 pointer-events-none"></div>

    <div class="z-10 text-center px-4 max-w-5xl flex flex-col items-center gap-12">
        <!-- 질문 -->
        <h1 
            class="font-bold leading-tight break-keep keep-all text-5xl md:text-7xl lg:text-8xl transition-colors duration-500 tracking-[0.05em] max-w-6xl mx-auto min-h-[1.2em]"
            :class="{ 'animate-float': isTypingFinished }"
            :style="{ color: questionColor }"
        >
            {{ displayedText }}<span v-if="!isTypingFinished" class="animate-cursor-blink ml-1 opacity-70">|</span>
        </h1>

        <!-- 버튼 -->
        <button 
            @click="goFeed"
            class="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-white/10 font-lg rounded-full hover:bg-white/20 hover:scale-105 active:scale-95 ring-1 ring-white/30 animate-fade-in-delay"
        >
            <Search class="w-5 h-5 mr-2 text-gray-300 group-hover:text-white" />
            <span class="text-gray-200 group-hover:text-white">답변하러 가기</span>
        </button>
    </div>
  </div>
</template>

<style scoped>
/* 깜빡이는 커서 */
@keyframes cursorBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

.animate-cursor-blink {
    animation: cursorBlink 1s infinite;
}

/* 둥둥 떠있는 효과 (타이핑 끝난 후) */
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.animate-float {
    animation: float 3s ease-in-out infinite;
}

/* 버튼 등장 딜레이 (기존 유지) */
.animate-fade-in-delay {
    opacity: 0; 
    animation: fadeIn 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    animation-delay: 2.5s; /* 타이핑 끝난 후 등장하도록 넉넉히 */
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
