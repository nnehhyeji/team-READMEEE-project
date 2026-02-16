<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, UserPlus, Loader2 } from 'lucide-vue-next'
import { useSocialStore } from '@/stores/social'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router' 
import { useModalStore } from '@/stores/modal' 

const props = defineProps({
  username: { type: String, required: true }, 
  initialTab: { type: String, default: 'followers' }
})

const emit = defineEmits(['close', 'refresh'])

const socialStore = useSocialStore()

const authStore = useAuthStore()
const router = useRouter() 
const modal = useModalStore() 
const { isLoading } = storeToRefs(socialStore)

const activeTab = ref(props.initialTab)
const searchQuery = ref('')
const userList = ref([]) 

/**
 * 💡 1. 데이터 로드 로직 (팔로워/팔로잉/검색 통합)
 */
const loadData = async () => {
  socialStore.isLoading = true 
  userList.value = [] 
  try {
    if (activeTab.value === 'discover') {
      if (!searchQuery.value) {
        userList.value = await socialStore.searchUsers('')
      } else {
        userList.value = await socialStore.searchUsers(searchQuery.value)
      }
    } else {
      userList.value = await socialStore.fetchFollowList(props.username, activeTab.value)
    }
  } catch(e) {
    console.error(e)
  } finally {
    socialStore.isLoading = false 
  }
}

/**
 * 2. 팔로우 토글 핸들러 (실제 API 연동)
 */
const handleFollowClick = async (user) => {
  if (!authStore.isAuthenticated) {
    const ok = await modal.confirm('로그인이 필요한 기능입니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) router.push('/auth')
    return
  }

  // user.username으로 서버에 요청
  const success = await socialStore.toggleFollow(user.username, user.is_following)
  
  if (success) {
    // 내 로컬 데이터 상태 즉시 업데이트
    user.is_following = !user.is_following
    emit('refresh')
  }
}

// 탭 전환이나 검색어 입력 시 데이터 다시 불러오기
watch([activeTab, searchQuery], loadData)
onMounted(loadData)

/**
 * 3. 데이터 정규화 (백엔드마다 다른 데이터 구조 통일)
 * 팔로워 목록은 follow.follower_info에, 검색 결과는 user 자체에 정보가 있음
 */
const normalizedUsers = computed(() => {
  return userList.value.map(item => {
    if (activeTab.value === 'followers') return item.follower_info
    if (activeTab.value === 'following') return item.following_info
    return item 
  })
})
</script>

<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in" @click="$emit('close')">
    <div class="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl flex flex-col max-h-[75vh]" @click.stop>
      
      <div class="flex border-b border-gray-100 bg-white">
        <button 
          v-for="tab in ['followers', 'following', 'discover']" 
          :key="tab"
          @click="activeTab = tab; searchQuery = ''" 
          class="flex-1 py-4 font-bold text-sm transition-colors capitalize" 
          :class="activeTab === tab ? 'text-[#507B9B] border-b-2 border-[#507B9B]' : 'text-gray-400 hover:text-gray-600'"
        >
          {{ tab === 'followers' ? '팔로워' : tab === 'following' ? '팔로잉' : '검색' }}
        </button>
      </div>

      <div class="p-4 bg-gray-50 border-b border-gray-100">
        <div class="relative bg-white rounded-xl shadow-sm">
          <Search class="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <input 
            v-model="searchQuery" 
            type="text" 
            :placeholder="activeTab === 'discover' ? '유저 아이디 검색...' : '목록에서 필터링...'" 
            class="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#507B9B]/20" 
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-4 space-y-2">
         <div v-if="isLoading" class="text-center py-10">
           <Loader2 class="w-8 h-8 animate-spin mx-auto text-[#507B9B]" />
         </div>

         <template v-else>
           <!-- 추천 목록일 때 헤더 표시 -->
           <div v-if="activeTab === 'discover' && !searchQuery && normalizedUsers.length > 0" class="mb-4 px-2">
             <h3 class="text-sm font-bold text-gray-800">👋 Recommended for You</h3>
             <p class="text-xs text-gray-400">새로운 친구들을 만나보세요!</p>
           </div>

           <div v-if="normalizedUsers.length === 0" class="text-center py-12 text-gray-400 text-sm">
             <!-- 검색어 없을 때는 추천 목록이 뜨므로, 검색 결과 없음 메시지는 검색어가 있을 때만 표출 -->
             <p v-if="activeTab === 'discover' && searchQuery">검색 결과가 없습니다.</p>
             <p v-else-if="activeTab !== 'discover'">표시할 사용자가 없습니다.</p>
           </div>
           
           <div v-for="user in normalizedUsers" :key="user.username" 
                class="flex items-center justify-between p-2 rounded-2xl hover:bg-gray-50 transition-colors group">
              <div class="flex items-center gap-3 cursor-pointer" @click="$emit('close'); $router.push(`/profile/${user.username}`)">
                  <img :src="user.profile_image || `https://ui-avatars.com/api/?name=${user.username}`" 
                       class="w-11 h-11 rounded-full object-cover border border-gray-100" />
                  <div>
                    <p class="font-bold text-gray-800 text-sm">{{ user.username }}</p>
                    <p class="text-[10px] text-gray-400">@{{ user.username }}</p>
                  </div>
              </div>
              
              <button 
                v-if="user.username !== authStore.currentUser?.username"
                @click="handleFollowClick(user)" 
                class="px-5 py-1.5 rounded-full text-xs font-bold transition-all border shadow-sm" 
                :class="user.is_following 
                  ? 'bg-white border-gray-200 text-gray-500 hover:border-rose-200 hover:text-rose-500' 
                  : 'bg-[#507B9B] border-transparent text-white hover:opacity-90'"
              >
                {{ user.is_following ? '팔로잉' : '팔로우' }}
              </button>
           </div>
         </template>
      </div>

      <div class="p-4 border-t border-gray-100 text-center bg-gray-50/50">
          <button @click="$emit('close')" class="text-gray-400 font-bold text-xs hover:text-gray-600 transition-colors uppercase tracking-widest">Close</button>
      </div>
    </div>
  </div>
</template>