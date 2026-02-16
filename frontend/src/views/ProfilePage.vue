<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Flame, UserPlus, UserCheck, ChevronLeft, ChevronRight, Camera, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useSocialStore } from '@/stores/social' 
import { useArticleStore } from '@/stores/articles'
import { useModalStore } from '@/stores/modal' 
import { storeToRefs } from 'pinia'
import axios from '@/api/axios'

// 자식 컴포넌트 임포트
import StatsSection from '@/components/StatsSection.vue'
import DetailModal from '@/components/DetailModal.vue'
import UserListModal from '@/components/UserListModal.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import ArchiveItem from '@/components/ArchiveItem.vue'
import ProfileCalendarArchive from '@/components/ProfileCalendarArchive.vue'
import DailyTimeline from '@/components/DailyTimeline.vue'
import SearchList from '@/components/SearchList.vue'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const socialStore = useSocialStore()
const articleStore = useArticleStore()
const modal = useModalStore() 

const { currentUser, isAuthenticated } = storeToRefs(authStore)

// --- 상태 (State) ---
const displayUser = ref(null) 
const isFollowing = ref(false)
const activeTab = ref('archive')
const feedViewMode = ref('grid') // 'grid' | 'timeline' | 'list'
const scrollY = ref(0) // 스크롤 위치 저장
const fileInput = ref(null) // 파일 입력 참조
const isLoadingFeed = ref(false) 


const handleScroll = () => {
  scrollY.value = window.scrollY
}

onMounted(() => {
  initProfile()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 동적 스타일 계산
const profileImageStyle = computed(() => {
  const maxScroll = 300 // 스크롤 거리 약간 늘림 (자연스럽게)
  const startSize = 320 // 2배 확대 (160 * 2)
  const endSize = 80    // 최소 크기 유지
  
  const progress = Math.min(scrollY.value / maxScroll, 1)
  const currentSize = startSize - (progress * (startSize - endSize))
  
  return {
    width: `${currentSize}px`,
    height: `${currentSize}px`
  }
})

// 모달 제어
const selectedArticle = ref(null)
const showUserModal = ref(false)
const activeModalTab = ref('followers')

const userArticles = ref([]) 
const monthlyStats = ref(null) 
const wordStats = ref([]) 

const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(new Date().getMonth() + 1)

// --- 헬퍼 함수 ---
const getEmotionEmoji = (emotion) => {
  const map = { 'happy': '😊', 'proud': '😎', 'yummy': '😋', 'tired': '😴', 'angry': '😤' }
  return map[emotion] || '😶'
}
const getEmotionColor = (emotion) => {
  const map = { 'happy': '#FCD34D', 'proud': '#93C5FD', 'yummy': '#FCA5A5', 'tired': '#C4B5FD', 'angry': '#E5E7EB' }
  return map[emotion] || '#CBD5E1'
}

// --- 핵심 로직 (Logic) ---

/**
 * 현재 페이지가 '나'의 프로필인지 확인
 */
const isMe = computed(() => {
  const routeUsername = route.params.username
  // URL에 이름이 없거나(내 주소), URL의 이름이 로그인한 내 이름과 같을 때
  return !routeUsername || (isAuthenticated.value && routeUsername === currentUser.value?.username)
})

/**
 * 프로필 정보 초기화 (가장 중요!)
 */
const initProfile = async () => {
  // 1. URL에서 이름을 가져오고, 없으면 내 이름을 타겟으로 설정
  const targetUsername = route.params.username || currentUser.value?.username

  // 로그인도 안 했고 URL에 이름도 없다면 로그인 페이지로 보냄
  if (!targetUsername && !isAuthenticated.value) {
    router.push('/auth')
    return
  }

  try {
    // A. 타인 프로필을 보고 있거나, 로그인 안 한 상태로 특정 유저를 볼 때
    if (targetUsername && targetUsername !== currentUser.value?.username) {
      const userRes = await axios.get(`/accounts/users/${targetUsername}/`)
      displayUser.value = userRes.data
      
      // 로그인 상태라면 팔로우 여부 체크
      if (isAuthenticated.value) {
        isFollowing.value = userRes.data.is_following || false
      }
    } 
    // B. 내 프로필을 보고 있을 때
    else if (isAuthenticated.value) {
      try {
        const myRes = await axios.get('/accounts/profile/my/')
        const freshUserData = myRes.data
        
        displayUser.value = {
          ...freshUserData,
          streak: freshUserData.consecutive_days || 0,
          follower_count: freshUserData.follower_count || 0,
          following_count: freshUserData.following_count || 0,
        }

        // 스토어 정보도 최신화 (다른 컴포넌트를 위해)
        authStore.currentUser = freshUserData
        localStorage.setItem('user_info', JSON.stringify(freshUserData))

      } catch (err) {
        console.error('내 정보 로딩 실패:', err)
        // 실패 시 기존 스토어 데이터라도 보여줌 (fallback)
        displayUser.value = {
          ...currentUser.value,
          streak: currentUser.value.consecutive_days || 0,
          follower_count: currentUser.value.follower_count || 0,
          following_count: currentUser.value.following_count || 0,
        }
      }
    }

    // 공통: 해당 유저의 게시글 가져오기
    isLoadingFeed.value = true 
    try {
      const articles = await articleStore.fetchUserArticles(targetUsername)
      userArticles.value = articles
      if (displayUser.value) displayUser.value.article_count = articles.length
    } finally {
      isLoadingFeed.value = false 
    }
    
    // 통계 탭이면 데이터 로드
    if (activeTab.value === 'emotions') loadStatsData()

  } catch (error) {
    console.error('프로필 로딩 실패:', error)
    modal.alert('사용자를 찾을 수 없습니다.', '오류')
    router.push('/')
  }
}

/**
 *  통계 데이터 로드
 */
const loadStatsData = async () => {
  if (!isMe.value) return 
  try {
    const stats = await articleStore.fetchMonthlyStats(selectedYear.value, selectedMonth.value)
    monthlyStats.value = stats
    const words = await articleStore.fetchWordFrequency(selectedYear.value, selectedMonth.value)
    wordStats.value = words
  } catch (error) {
    console.error('통계 로드 실패:', error)
  }
}

// 달 이동 로직
const changeMonth = (delta) => {
  selectedMonth.value += delta
  if (selectedMonth.value > 12) { selectedMonth.value = 1; selectedYear.value++ } 
  else if (selectedMonth.value < 1) { selectedMonth.value = 12; selectedYear.value-- }
  loadStatsData()
}

// 팔로우 처리 (비회원 차단 추가, 서버 연동, 숫자 실시간 반영)
const handleMainFollow = async () => { 
  if (!isAuthenticated.value) {
    const ok = await modal.confirm('로그인이 필요한 기능입니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) router.push('/auth')
    return
  }

  // 1. 소셜 스토어를 통해 서버에 요청 (DB 반영)
  const success = await socialStore.toggleFollow(targetUsername, isFollowing.value)
  
  if (success) {
    // 2. 현재 팔로우 상태 반전
    isFollowing.value = !isFollowing.value 


    // 3. 화면에 보이는 숫자를 즉시 업데이트 (UI 반영)
    if (isFollowing.value) {
      // 팔로우를 한 경우 -> 상대방의 팔로워 수 +1
      displayUser.value.follower_count++
    } else {
      // 팔로우를 취소한 경우 -> 상대방의 팔로워 수 -1
      displayUser.value.follower_count--
    }
  } else {
    console.error('팔로우 요청 실패')
  }
}

// 2. 좋아요 처리
const handleLike = async (article) => {
  if (!isAuthenticated.value) {
    const ok = await modal.confirm('로그인 후 마음을 표현할 수 있습니다! \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) router.push('/auth')
    return
  }
  
  const success = await articleStore.toggleLike(article.id)
  
  if (success) {
    article.is_liked = !article.is_liked
    article.is_liked ? article.like_count++ : article.like_count--
  }
}

// 프로필 이미지 URL 처리 헬퍼
const getProfileImageUrl = (user) => {
  if (!user || !user.profile_image) {
    return `https://ui-avatars.com/api/?name=${user?.username || 'User'}`
  }
  const path = user.profile_image
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  return path.startsWith('http') ? path : `${apiUrl}${path}`
}

const openUserModal = (tab) => {
  activeModalTab.value = tab
  showUserModal.value = true
}

const openDetail = (article) => {
  selectedArticle.value = article
}

const goToProfile = (username) => {
  if (route.params.username === username) return
  router.push(`/profile/${username}`)
}

// URL 파라미터가 바뀔 때마다 프로필 재설정
watch(() => route.params.username, () => {
  activeTab.value = 'archive'
  initProfile()
})

watch(activeTab, (newTab) => {
  if (newTab === 'emotions') loadStatsData()
})


</script>

<template>
  <div class="min-h-screen pb-24 font-sans bg-[#FDFBF7] paper-texture">
    <NavBar />
    <template v-if="displayUser">
      
      <!-- 미니멀 디자인 -->
      <div class="pt-32 pb-10 px-6 text-center"> 
        
          <!-- 프로필 이미지 -->
          <div 
            class="relative inline-block mb-6 transition-all duration-300 ease-out group"
          >
            <img :src="getProfileImageUrl(displayUser)" 
                 :style="profileImageStyle"
                 class="rounded-full object-cover shadow-sm bg-white transition-all duration-100" />
                 
            <div v-if="displayUser.streak > 0" class="absolute bottom-2 right-2 bg-orange-500 text-white p-2 rounded-full shadow-md animate-bounce-slow"
                 :class="{ 'scale-75': scrollY > 50 }">
              <Flame class="w-5 h-5" />
            </div>
          </div>
          
          <!-- 유저네임 & 소개글 -->
          <h1 class="text-4xl font-bold text-gray-900 mb-3 tracking-tight font-sans">{{ displayUser.username }}</h1>
          <p class="text-gray-500 text-sm max-w-sm mx-auto mb-10 leading-relaxed font-medium">
            {{ displayUser.bio || '기록이 일상이 되는 공간 🌙' }}
          </p>
          
          <!-- 스탯 섹션 (카드 제거 -> 텍스트 중심) -->
          <div class="flex justify-center items-center gap-8 mb-10">
            <div class="text-center min-w-[3rem]">
              <p class="font-bold text-xl text-gray-900 mb-1">{{ displayUser.article_count || 0 }}</p>
              <p class="text-xs text-gray-500 font-bold">게시물</p>
            </div>
            <div class="text-center min-w-[3rem]">
              <p class="font-bold text-xl text-gray-900 mb-1">{{ displayUser.streak || 0 }}</p>
              <p class="text-xs text-gray-500 font-bold">연속기록</p>
            </div>
            <button @click="openUserModal('followers')" class="text-center min-w-[3rem] hover:opacity-70 transition-opacity">
              <p class="font-bold text-xl text-gray-900 mb-1">{{ displayUser.follower_count || 0 }}</p>
              <p class="text-xs text-gray-500 font-bold">팔로워</p>
            </button>
            <button @click="openUserModal('following')" class="text-center min-w-[3rem] hover:opacity-70 transition-opacity">
              <p class="font-bold text-xl text-gray-900 mb-1">{{ displayUser.following_count || 0 }}</p>
              <p class="text-xs text-gray-500 font-bold">팔로잉</p>
            </button>
          </div>
  
          <!-- 버튼 영역 -->
          <div class="flex justify-center gap-3">
              <button v-if="isMe" @click="router.push('/settings')" class="bg-gray-100 text-gray-900 px-8 py-3 rounded-xl font-bold text-sm hover:bg-gray-200 transition-all">
               프로필 편집
             </button>
             <button v-else @click="handleMainFollow" class="px-12 py-3 rounded-xl font-bold text-sm transition-all shadow-sm flex items-center gap-2" 
               :class="isFollowing ? 'bg-gray-100 text-gray-900' : 'bg-black text-white hover:bg-gray-800'">
               {{ isFollowing ? '팔로잉' : '팔로우' }}
             </button>
          </div>

      </div>

      <div class="max-w-4xl mx-auto px-6 mt-8 pb-24">
        <div class="flex border-b border-gray-200 mb-8">
          <button v-for="tab in ['archive', 'calendar_list', 'emotions']" :key="tab" @click="activeTab = tab" 
                  class="flex-1 py-4 text-sm font-bold capitalize border-b-2 transition-colors duration-200" 
                  :class="activeTab === tab ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-400 hover:text-gray-600'">
            {{ tab === 'archive' ? 'Feed' : (tab === 'calendar_list' ? 'Easter Egg' : 'Statistics') }}
          </button>
        </div>

        <!-- 1. Feed View (Original Archive) -->
        <div v-if="activeTab === 'archive'" class="space-y-4 animate-fade-in transition-all">
           
           <!-- Feed View Toggle (Grid vs Daily) -->
           <div class="flex justify-end mb-4">
             <div class="bg-gray-100 p-1 rounded-lg flex text-xs font-bold">
               <button 
                 @click="feedViewMode = 'grid'" 
                 class="px-3 py-1.5 rounded-md transition-all"
                 :class="feedViewMode === 'grid' ? 'bg-white text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
               >
                 그리드
               </button>
               <button 
                 @click="feedViewMode = 'timeline'" 
                 class="px-3 py-1.5 rounded-md transition-all"
                 :class="feedViewMode === 'timeline' ? 'bg-white text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
               >
                 타임라인
               </button>
               <button 
                 @click="feedViewMode = 'list'" 
                 class="px-3 py-1.5 rounded-md transition-all"
                 :class="feedViewMode === 'list' ? 'bg-white text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
               >
                 검색/목록
               </button>
             </div>
           </div>

           <!-- 로딩 중일 때 스피너 표시 -->
           <div v-if="isLoadingFeed" class="flex flex-col items-center justify-center py-20">
             <Loader2 class="w-8 h-8 text-primary-500 animate-spin mb-3" />
             <p class="text-gray-400 font-medium text-sm">기록을 불러오는 중...</p>
           </div>

           <!-- 로딩 끝난 후 데이터 표시 -->
           <div v-else>
               <!-- Grid View -->
               <div v-if="feedViewMode === 'grid'">
                  <div v-if="userArticles.length > 0">
                      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-6">
                        <ArchiveItem 
                          v-for="(article, index) in userArticles" 
                          :key="article.id" 
                          :article="article"
                          :index="index"
                          @click="openDetail(article)"
                        />
                      </div>
                    </div>
                    <div v-else class="text-center py-24 bg-white rounded-3xl border border-dashed border-gray-200 text-gray-400 font-medium">
                      아직 기록된 마음이 없습니다. 📭
                    </div>
               </div>
               
               <!-- Daily Timeline View -->
               <div v-else-if="feedViewMode === 'timeline'">
                  <DailyTimeline 
                    :articles="userArticles" 
                    :username="displayUser.username"
                    @open-detail="openDetail"
                  />
               </div>

               <!-- Search/List View -->
               <div v-else-if="feedViewMode === 'list'">
                  <SearchList 
                    :articles="userArticles"
                    @open-detail="openDetail"
                  />
               </div>
           </div>

        </div>

        <!-- 2. [NEW] Calendar & Search View -->
        <div v-else-if="activeTab === 'calendar_list'" class="space-y-6 animate-fade-in">
          <div v-if="isMe">
            <ProfileCalendarArchive 
              :user-id="displayUser.id" 
              :username="displayUser.username" 
              :is-me="isMe" 
            />
          </div>
          <div v-else class="text-center py-20 bg-white rounded-3xl border border-dashed text-gray-400">
             캘린더와 검색은 본인만 이용할 수 있습니다. 🔒
          </div>
        </div>

        <!-- 3. Statistics View -->
        <div v-else-if="activeTab === 'emotions'" class="space-y-6 animate-fade-in">
          <template v-if="isMe">
            <div class="flex items-center justify-between bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
              <button @click="changeMonth(-1)" class="p-2 hover:bg-gray-100 rounded-full"><ChevronLeft /></button>
              <h2 class="text-lg font-bold text-gray-800">{{ selectedYear }}년 {{ selectedMonth }}월</h2>
              <button @click="changeMonth(1)" class="p-2 hover:bg-gray-100 rounded-full"><ChevronRight /></button>
            </div>
            <StatsSection v-if="monthlyStats" :emotion-data="monthlyStats.emotion_distribution" :word-data="wordStats" :articles="userArticles" />
          </template>
          <div v-else class="text-center py-24 text-gray-400 font-medium bg-white rounded-3xl shadow-sm border border-dashed">
            통계는 본인만 확인할 수 있습니다. 🤫
          </div>
        </div>


      </div>
    </template>

    <div v-else class="min-h-[80vh] flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
        <p class="text-gray-500 font-medium">프로필을 불러오고 있어요...</p>
      </div>
    </div>

    <UserListModal 
      v-if="showUserModal" 
      :initialTab="activeModalTab" 
      :username="displayUser?.username" 
      @close="showUserModal = false" 
      @refresh="initProfile"
      />
    <DetailModal 
      v-if="selectedArticle" 
      :article="selectedArticle" 
      @close="selectedArticle = null" 
      @click-like="handleLike" 
      @click-profile="goToProfile" 
    />
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
.animate-bounce-slow { animation: bounce 2s infinite; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

.paper-texture {
  background-color: #FDFBF7; /* Base paper color */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.2' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.08'/%3E%3C/svg%3E");
  background-blend-mode: multiply;
}
</style>