<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue' 
import { useRouter } from 'vue-router'
import { Search, ChevronDown, Loader2, Plus, Play, Pause, X } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'

// 컴포넌트들
import ArticleCard from '@/components/ArticleCard.vue'
import DetailModal from '@/components/DetailModal.vue'
import WriteModal from '@/components/WriteModal.vue'
import NavBar from '@/components/NavBar.vue'
import MasonryGrid from '@/components/MasonryGrid.vue'

// 스토어들
import { useArticleStore } from '@/stores/articles'
import { useQuestionStore } from '@/stores/question'
import { useAuthStore } from '@/stores/auth'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const articleStore = useArticleStore()
const questionStore = useQuestionStore()
const authStore = useAuthStore()
const modal = useModalStore() 

// --- 상태 (State) ---
const { articles, hasAnswered } = storeToRefs(articleStore)
const { todayQuestion } = storeToRefs(questionStore) 

// 로컬 상태
const isWriteModalOpen = ref(false) 
const selectedArticle = ref(null)   
const startTime = ref(0)
const showRecommendations = ref(false)
const isLoading = ref(true)

// 스크롤 상태 관리 (배경 전환 효과)
const scrollY = ref(0)
const handleScroll = () => {
  scrollY.value = window.scrollY
}

// 음악 팝업 상태
const showMusicPopup = ref(false)
const isMusicPlaying = ref(false)

// 질문별로 게시글 그룹화
const groupedFeed = computed(() => {
  const groups = {}

  articles.value.forEach(article => {
    if (!article.question) return

    const qId = article.question.id
    if (!groups[qId]) {
      groups[qId] = {
        question: article.question,
        articles: []
      }
    }
    groups[qId].articles.push(article)
  })

  return Object.values(groups).sort((a, b) => {
    return new Date(b.question.release_date) - new Date(a.question.release_date)
  })
})

// 음악 정보
const musicInfo = computed(() => {
  const q = todayQuestion.value
  if (q && q.rec_video_id) {
    return {
      title: q.rec_title,
      artist: q.rec_artist,
      reason: q.rec_reason,
      videoId: q.rec_video_id
    }
  }
  return null
})

onMounted(async () => {
  window.addEventListener('scroll', handleScroll) // 스크롤 리스너 등록
  try {
    isLoading.value = true
    await Promise.all([
      articleStore.getArticles(),
      questionStore.fetchTodayQuestion()
    ])
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll) // 리스너 제거
})

const goToProfile = (userName) => router.push(`/profile/${userName}`)

const handleOpenWriteModal = async () => {
  if (isLoading.value) return 

  if (hasAnswered.value) {
    modal.alert('오늘의 질문에 이미 답변하셨습니다', '알림')
    return
  }

  if (!authStore.isAuthenticated) {
    const ok = await modal.confirm('로그인이 필요한 기능입니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) {
      router.push('/auth')
    }
    return
  }
  isWriteModalOpen.value = true
}

const handleLike = async (article) => {
  if (!authStore.isAuthenticated) {
    const ok = await modal.confirm('좋아요를 누르려면 로그인이 필요합니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) {
      router.push('/auth')
    }
    return
  }
  await articleStore.toggleLike(article.id)
}

const openDetail = (article) => {
  selectedArticle.value = article
  startTime.value = Date.now()
}

const closeDetail = async () => {
  if (selectedArticle.value) {
    const duration = Math.round((Date.now() - startTime.value) / 1000)
    await articleStore.recordDwellTime(selectedArticle.value.id, duration)
  }
  selectedArticle.value = null
}

const handleCreateArticle = async ({ content, emotion, image, question_id, music_title, music_artist, is_public }) => {
  try {
    const success = await articleStore.createArticle({ 
      content, emotion, image, question_id, music_title, music_artist, is_public 
    })
    
    if (success) {
      isWriteModalOpen.value = false
      modal.success('오늘의 기록이 저장되었습니다!', '성공')
    }
  } catch (error) {
    console.error('글 작성 실패:', error)
    modal.alert("저장에 실패했습니다.", '오류')
  }
}

// 재생 버튼 클릭 핸들러
const handlePlayClick = () => {
  if (!musicInfo.value) {
    modal.alert('오늘의 추천 음악이 없습니다.', '음악 없음')
    return
  }
  
  // Toggle Logic
  if (isMusicPlaying.value) {
    isMusicPlaying.value = false
    showMusicPopup.value = false
  } else {
    showMusicPopup.value = true
    isMusicPlaying.value = true
  }
}

// 음악 팝업 내 재생/일시정지
const toggleMusicPlayback = () => {
  isMusicPlaying.value = !isMusicPlaying.value
}

// 음악 팝업 닫기
const closeMusicPopup = () => {
  showMusicPopup.value = false
  isMusicPlaying.value = false
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen pb-24 font-pretendard relative overflow-hidden bg-[#DDB6B8]">
    
    <!-- 1. Background Layer 1: The "Snake" Design (Fixed Base) -->
    <div class="fixed inset-0 w-full h-full pointer-events-none z-0">
      <div class="absolute inset-0 w-full h-full bg-[#DDB6B8]">
        <!-- Snake Body -->
        <div class="absolute -top-[15%] -left-[15%] w-[130vh] h-[130vh] rounded-[48%] bg-gradient-to-br from-white/80 via-white/20 to-transparent rotate-[20deg] mix-blend-overlay opacity-90 blur-[50px] transform-gpu"></div>
        <div class="absolute -bottom-[25%] -right-[25%] w-[140vh] h-[140vh] rounded-[45%] bg-[#E5B0B4] rotate-[20deg] mix-blend-normal opacity-100 blur-[50px] transform-gpu"></div>
        
        <!-- 3. Water Ripple Effect (Concentric Expanding Circles) -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full pointer-events-none z-0 overflow-hidden">
           <!-- Ripple 1 -->
           <div class="absolute top-1/2 left-1/2 w-[50vh] h-[50vh] border-[1px] border-white/70 rounded-full -translate-x-1/2 -translate-y-1/2 opacity-0 animate-ripple"></div>
           <!-- Ripple 2 (Delayed) -->
           <div class="absolute top-1/2 left-1/2 w-[50vh] h-[50vh] border-[1px] border-white/50 rounded-full -translate-x-1/2 -translate-y-1/2 opacity-0 animate-ripple" style="animation-delay: 2.5s;"></div>
           <!-- Ripple 3 (Delayed) -->
           <div class="absolute top-1/2 left-1/2 w-[50vh] h-[50vh] border-[1px] border-white/30 rounded-full -translate-x-1/2 -translate-y-1/2 opacity-0 animate-ripple" style="animation-delay: 5s;"></div>
        </div>
      </div>
    </div>

    <!-- 2. Background Layer 2: The "Pink -> White -> Green" Gradient Overlay -->
    <!-- Opacity changes based on scrollY -->
    <div 
      class="fixed inset-0 w-full h-full pointer-events-none z-0 transition-opacity duration-500 ease-out"
      :style="{ opacity: Math.min(scrollY / 600, 1) }"
    >
      <!-- Custom Gradient based on user image -->
      <div class="absolute inset-0 bg-[#F9F8F5]"></div>
      
      <!-- Blue Orb (Left Bottom) -->
      <!-- Wrapper: Scroll Movement -->
      <div 
        class="absolute bottom-[-10%] left-[-20%] w-[90vh] h-[90vh] transition-transform duration-75 ease-linear will-change-transform"
        :style="{ transform: `translate(${scrollY * 0.3}px, -${scrollY * 0.3}px)` }"
      >
        <!-- Inner: Visual & Pulse Animation -->
        <div class="w-full h-full rounded-full bg-[#D0E6F5] blur-[120px] opacity-90 mix-blend-multiply animate-pulse-slow"></div>
      </div>

      <!-- Lime Orb 1 (Right Top) -->
      <div 
        class="absolute top-[-10%] right-[-10%] w-[100vh] h-[100vh] transition-transform duration-75 ease-linear will-change-transform" 
        :style="{ transform: `translate(-${scrollY * 0.3}px, ${scrollY * 0.3}px)` }"
      >
        <div class="w-full h-full rounded-full bg-[#E9F7C6] blur-[100px] opacity-90 mix-blend-multiply animate-pulse-slow" style="animation-delay: 1.5s;"></div>
      </div>

      <!-- Lime Orb 2 (Right Center) -->
      <div 
        class="absolute top-[30%] right-[-20%] w-[80vh] h-[80vh] transition-transform duration-75 ease-linear will-change-transform" 
        :style="{ transform: `translate(-${scrollY * 0.4}px, ${scrollY * 0.2}px)` }"
      >
        <div class="w-full h-full rounded-full bg-[#DDF988] blur-[130px] opacity-70 mix-blend-multiply animate-pulse-slow" style="animation-delay: 3s;"></div>
      </div>
    </div>

    <!-- 3. Noise Overlay (Fixed on top of backgrounds) -->
    <div class="fixed inset-0 w-full h-full pointer-events-none z-[1] opacity-[0.45] mix-blend-overlay">
      <svg class="w-full h-full noise-svg">
        <filter id="noiseFilter">
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noiseFilter)" />
      </svg>
    </div>
    
    <!-- Main Content Wrapper (Z-Index Adjusted) -->
    <div class="relative z-10">
      
      <!-- 상단 네비게이션 바 -->
      <!-- 상단 네비게이션 바 -->
      <NavBar />
      
      <!-- Hero Section -->
      <div class="relative w-full h-[85vh] overflow-hidden">
        
        <div class="relative z-10 max-w-7xl mx-auto px-6 md:px-20 pt-40 md:pt-52">
          <h1 class="text-4xl md:text-[56px] font-black text-[#1A1A1A] leading-[1.15] mb-12 tracking-tight max-w-3xl break-keep drop-shadow-sm">
            {{ todayQuestion ? todayQuestion.content : '오늘의 질문을 불러오는 중...' }}
          </h1>

          <div class="flex items-center gap-5">

            <!-- Modified Write Button Logic -->
            <div 
               class="w-full md:w-[450px] h-[68px] backdrop-blur-md rounded-full px-8 flex items-center justify-between shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/50 transition-all group z-20"
               :class="(hasAnswered || isLoading) ? 'bg-gray-100 cursor-default' : 'bg-white/90 cursor-pointer hover:bg-white'"
               @click="handleOpenWriteModal"
            >
              <span 
                class="font-medium text-lg transition-colors"
                :class="(hasAnswered || isLoading) ? 'text-gray-400' : 'text-gray-400 group-hover:text-gray-600'"
              >
                {{ isLoading ? '기록 확인 중...' : (hasAnswered ? '오늘의 기록 완료!' : '오늘의 질문에 답변을 남겨보세요') }}
              </span>
              
              <div v-if="!hasAnswered && !isLoading">
                <Search class="w-6 h-6 text-gray-400 group-hover:text-pink-400 transition-colors" />
              </div>
              <div v-else-if="isLoading">
                 <Loader2 class="w-5 h-5 text-gray-400 animate-spin" />
              </div>
              <div v-else>
                 <span class="text-xl"></span>
              </div>
            </div>

            <button 
              @click="handlePlayClick"
              class="w-[68px] h-[68px] rounded-full bg-white/80 backdrop-blur-md shadow-lg flex items-center justify-center hover:bg-white transition-all active:scale-95 z-20 group"
            >
              <component :is="isMusicPlaying ? Pause : Play" class="w-6 h-6 text-black fill-black group-hover:scale-110 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-6 md:px-20 py-20 relative z-10">
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
          <Loader2 class="w-10 h-10 text-pink-400 animate-spin mb-4" />
          <p class="text-gray-600 font-medium">기록을 불러오고 있어요</p>
        </div>

        <div v-else>
          <div v-for="group in groupedFeed" :key="group.question.id" class="mb-20">
            <div v-if="group.question.id !== todayQuestion?.id" class="mb-10 pl-6 border-l-4 border-pink-200">
              <p class="text-[12px] text-pink-400 font-bold uppercase tracking-[0.2em] mb-2">Previous Log</p>
              <h2 class="text-xl font-bold text-gray-800">{{ group.question.content }}</h2>
            </div>

            <MasonryGrid :items="group.articles">
              <template #default="{ item: article }">
                <ArticleCard 
                  :key="article.id" 
                  :article="article"
                  class="transform hover:-translate-y-1 transition-transform duration-300"
                  @select-article="openDetail"
                  @click-profile="goToProfile"
                  @click-like="handleLike"
                />
              </template>
            </MasonryGrid>
          </div>
          
          <div v-if="groupedFeed.length === 0" class="text-center py-20 text-gray-400">
            <p class="text-sm">아직 작성된 글이 없습니다. 첫 기록을 남겨보세요! ✨</p>
          </div>
        </div>
      </div>
      
      <!-- 음악 팝업 카드 (Restored + Fixed) -->
      <Transition
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="transform translate-y-full opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-full opacity-0"
      >
        <div 
          v-if="showMusicPopup && musicInfo" 
          class="fixed bottom-24 right-6 md:bottom-8 md:right-8 w-72 bg-gradient-to-b from-white to-pink-100 rounded-3xl shadow-2xl overflow-hidden border border-white/50 z-50"
        >
          <!-- 앨범 커버 -->
          <div class="relative h-48 bg-gray-100 flex items-center justify-center">
            <iframe 
              v-if="isMusicPlaying"
              :src="`https://www.youtube.com/embed/${musicInfo.videoId}?autoplay=1&controls=0&modestbranding=1&rel=0`" 
              class="w-full h-full object-cover" 
              frameborder="0" 
              allow="autoplay; encrypted-media" 
            ></iframe>
            <div v-else class="flex items-center justify-center">
              <span class="text-6xl opacity-30">🎵</span>
            </div>

            <!-- 닫기 -->
            <button 
              @click="closeMusicPopup"
              class="absolute top-3 right-3 w-8 h-8 bg-white/80 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-md"
            >
              <X class="w-4 h-4 text-gray-600" />
            </button>
          </div>

          <!-- 정보 -->
          <div class="p-5">
            <p class="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1">Today's BGM</p>
            <h3 class="font-bold text-gray-900 text-base mb-1 leading-tight">{{ musicInfo.title }}</h3>
            <p class="text-sm text-gray-600 mb-1">{{ musicInfo.artist }}</p>
            <div class="w-full h-px bg-black opacity-40 my-2"></div>
            <p class="text-xs text-gray-500 leading-relaxed mb-4 line-clamp-2">{{ musicInfo.reason }}</p>
            
            <div class="flex items-center gap-5">
              <button @click="toggleMusicPlayback" class="w-10 h-10 bg-black rounded-full flex items-center justify-center hover:bg-gray-900 transition-all shadow-md active:scale-95 group">
                <component :is="isMusicPlaying ? Pause : Play" class="w-4 h-4 text-white fill-white group-hover:scale-110 transition-transform" />
              </button>
              
              <!-- Decorative Dots -->
              <div class="flex gap-1.5">
                <div 
                  class="w-1.5 h-1.5 bg-black rounded-full transition-all"
                  :class="{ 'animate-dot-bounce': isMusicPlaying }"
                ></div>
                <div 
                  class="w-1.5 h-1.5 bg-black rounded-full transition-all"
                  :class="{ 'animate-dot-bounce': isMusicPlaying }"
                  style="animation-delay: 0.15s"
                ></div>
                <div 
                  class="w-1.5 h-1.5 bg-black rounded-full transition-all"
                  :class="{ 'animate-dot-bounce': isMusicPlaying }"
                  style="animation-delay: 0.3s"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <DetailModal 
        v-if="selectedArticle" 
        :article="selectedArticle" 
        @close="closeDetail"
        @click-profile="goToProfile"
        @click-like="handleLike"
      />

      <WriteModal 
        v-if="isWriteModalOpen"
        @close="isWriteModalOpen = false"
        @create-article="handleCreateArticle"
      />

    </div>
  </div>
</template>

<style scoped>
/* Ripple Animation (Water Effect) */
@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0;
  }
  20% {
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.8);
    opacity: 0;
  }
}
.animate-ripple {
  animation: ripple 8s cubic-bezier(0, 0, 0.2, 1) infinite;
}

/* Music Dot Animation */
@keyframes dot-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.animate-dot-bounce {
  animation: dot-bounce 1s ease-in-out infinite;
}

/* 부드러운 애니메이션 효과 */
@keyframes pulse-slow {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.05); opacity: 0.5; }
}
.animate-pulse-slow {
  animation: pulse-slow 8s ease-in-out infinite;
}

/* 가독성을 위한 텍스트 스타일 */
h1 {
  word-break: keep-all;
}

/* Noise SVG Style */
.noise-svg {
  filter: contrast(170%) brightness(100%);
}
</style>
```