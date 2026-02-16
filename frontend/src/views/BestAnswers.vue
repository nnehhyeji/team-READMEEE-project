<script setup>
import axios from '@/api/axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loader2 } from 'lucide-vue-next' 

import ArticleCard from '@/components/ArticleCard.vue'
import DetailModal from '@/components/DetailModal.vue'
import NavBar from '@/components/NavBar.vue'
import { useArticleStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const articleStore = useArticleStore()

const authStore = useAuthStore()
const modal = useModalStore() 

// --- 상태 ---
const selectedPost = ref(null)
const isLoading = ref(true) 

// --- 데이터 (베스트 글) ---
const bestAnswers = ref([])

// --- API 호출 ---
const fetchBestAnswers = async () => {
  try {
    isLoading.value = true 
    const response = await axios.get('/articles/weekly_best/')
    bestAnswers.value = response.data
  } catch (error) {
    console.error('베스트 게시글 로딩 실패:', error)
  } finally {
    isLoading.value = false 
  }
}

onMounted(() => {
  fetchBestAnswers()
})

// --- 함수 ---
const getRankBadge = (rank) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return '⭐'
}

const goToProfile = (userName) => router.push(`/profile/${userName}`)

const openDetail = (answer) => {
  selectedPost.value = answer
}

const closeDetail = () => {
  selectedPost.value = null
}

const toggleLike = async (post) => {
  const success = await articleStore.toggleLike(post.id)
  if (!success) {
    modal.alert('집계 기간(24시간)이 지난 글에는 \n좋아요를 누를 수 없습니다.', '알림', 'danger')
  }
}
</script>

<template>
  <div class="min-h-screen pb-24 relative overflow-hidden font-pretendard">
    
    <div class="fixed inset-0 bg-gradient-to-br from-orange-300 via-teal-200 to-blue-300 -z-10"></div>
    
    <div class="fixed inset-0 backdrop-blur-[100px] bg-white/30 -z-5"></div>

    <NavBar />

    <div class="pt-32 pb-0 relative">
      <div class="max-w-7xl mx-auto px-6 pb-20 relative min-h-[400px] md:min-h-[500px]">  
        
        <div class="absolute top-12 left-6 md:left-12">
          <div class="absolute top-0 left-0 w-[90px] h-[180px] md:w-[140px] md:h-[280px] border-r-2 border-t-2 border-b-2 border-gray-800 rounded-r-full overflow-hidden"></div>
          
          
          <div class="absolute top-8 left-[70px] md:top-16 md:left-[110px] w-[140px] h-[140px] md:w-[200px] md:h-[200px] border-2 border-gray-800 rounded-full bg-white/40 backdrop-blur-md flex items-center justify-center shadow-sm animate-elastic-pop delay-150">
          </div>
          
          <div class="absolute top-[-10px] left-[200px] md:top-[-20px] md:left-[300px] w-[120px] h-[120px] md:w-[180px] md:h-[180px] border-2 border-gray-800 rounded-full bg-white/30 backdrop-blur-md flex items-center justify-center shadow-sm animate-elastic-pop delay-300">
          </div>
          
          
          <div class="absolute top-16 left-[310px] md:top-24 md:left-[460px] w-[100px] h-[100px] md:w-[140px] md:h-[140px] border-2 border-gray-800 rounded-full bg-white/20 backdrop-blur-md shadow-sm animate-elastic-pop delay-500"></div>
        </div>

        <div class="hidden lg:block absolute top-12 right-12">
          <div class="absolute top-8 right-0 w-[130px] h-[130px] border-2 border-gray-800 rounded-full bg-white/30 backdrop-blur-md flex items-center justify-center shadow-sm animate-roll-in delay-700">
          </div>
        </div>

        <div class="relative z-10 pt-32 md:pt-40 px-4 max-w-4xl">
          <h1 class="text-6xl md:text-8xl lg:text-9xl font-bold text-gray-900 tracking-tight mb-6 leading-none">
            Weekly Best
          </h1>
          <div class="mt-10 md:mt-16">
            <h2 class="text-3xl md:text-5xl font-light text-gray-800 mb-3">
              A Moment's Gaze
            </h2>
            <p class="text-lg md:text-xl text-gray-700 font-light leading-relaxed">
              타인의 시선을 멈추게 한 저번 주의 게시물
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-6 relative z-10">
      
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-32">
        <Loader2 class="w-10 h-10 text-gray-400 animate-spin mb-4" />
        <p class="text-gray-500 font-medium">이번 주의 베스트 글을 불러오고 있습니다</p>
      </div>

      <div v-else-if="bestAnswers.length === 0" class="text-center py-20">
        <div class="inline-block bg-white/80 backdrop-blur-sm px-12 py-8 rounded-3xl shadow-lg border border-gray-200">
          <p class="text-xl text-gray-600">아직 집계된 베스트 글이 없습니다 🐢</p>
        </div>
      </div>
      
      <div v-else class="bg-white/60 backdrop-blur-xl rounded-[40px] p-8 md:p-12 shadow-2xl border border-white/50">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <div 
            v-for="(answer, index) in bestAnswers" 
            :key="answer.id"
            class="relative group"
          >
            <div class="absolute -top-4 -left-4 z-20 bg-gray-900 text-white w-12 h-12 rounded-full shadow-xl flex items-center justify-center text-2xl font-bold border-4 border-white">
              {{ getRankBadge(index + 1) }}
            </div>

            <div class="bg-white rounded-[24px] shadow-lg border border-gray-200 overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 cursor-pointer h-full">
              <div @click="openDetail(answer)" class="p-6">
                
                <div class="flex items-center gap-3 mb-4">
                  <img 
                    :src="answer.author?.profile_image || `https://ui-avatars.com/api/?name=${answer.author?.username || 'User'}&background=random&color=fff`"
                    class="w-12 h-12 rounded-full object-cover border-2 border-gray-100"
                    @click.stop="goToProfile(answer.author?.username)"
                  />
                  <div class="flex-1">
                    <p class="font-bold text-gray-900 cursor-pointer hover:underline text-base" @click.stop="goToProfile(answer.author?.username)">
                      {{ answer.author?.username || '익명' }}
                    </p>
                    <p class="text-xs text-gray-400">
                      {{ new Date(answer.created_at).getFullYear() }}. {{ new Date(answer.created_at).getMonth() + 1 }}. {{ new Date(answer.created_at).getDate() }}.
                    </p>
                  </div>
                </div>

                <div v-if="answer.question" class="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <span class="text-[10px] font-black text-gray-900 uppercase tracking-wider block mb-1.5">Q.</span>
                  <p class="text-sm font-semibold text-gray-800 leading-snug">{{ answer.question.content }}</p>
                </div>

                <div v-if="answer.image" class="mb-4 -mx-6">
                  <img :src="answer.image" class="w-full aspect-square object-cover" />
                </div>

                <p class="text-gray-700 leading-relaxed mb-6 line-clamp-4 text-base">
                  {{ answer.content }}
                </p>
                
                <div class="flex gap-6 pt-4 border-t border-gray-100">
                  <button @click.stop="toggleLike(answer)" class="flex items-center gap-2 text-gray-600 hover:text-rose-500 transition-colors text-sm" :class="{ 'text-rose-500': answer.is_liked }">
                    <svg class="w-5 h-5" :class="{ 'fill-current': answer.is_liked }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <span class="font-medium">{{ answer.like_count || 0 }}</span>
                  </button>
                  <button class="flex items-center gap-2 text-gray-600 hover:text-blue-500 transition-colors text-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span class="font-medium">{{ answer.comment_count || 0 }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <DetailModal 
      v-if="selectedPost" 
      :article="selectedPost" 
      @close="closeDetail"
      @click-profile="goToProfile"
      @click-like="toggleLike"
    />

  </div>
</template>

<style scoped>
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

@keyframes elastic-pop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1.1);
    opacity: 1;
  }
  65% {
    transform: scale(0.95);
  }
  82% {
    transform: scale(1.02);
  }
  92% {
    transform: scale(0.98);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes roll-in {
  0% {
    transform: translateX(-600%) rotate(-1080deg); /* 직전 도형 위치 부근에서 시작 */
    opacity: 0;
  }
  100% {
    transform: translateX(0) rotate(0deg);
    opacity: 1;
  }
}

.animate-elastic-pop {
  animation: elastic-pop 1.2s cubic-bezier(0.28, 0.84, 0.42, 1) forwards;
  opacity: 0;
}

.animate-roll-in {
  animation: roll-in 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 0;
}

.delay-150 { animation-delay: 150ms; }
.delay-300 { animation-delay: 300ms; }
.delay-500 { animation-delay: 500ms; }
.delay-700 { animation-delay: 700ms; }

</style>