<script setup>
import { X, Heart, MessageCircle, Send, MoreHorizontal, Trash2 } from 'lucide-vue-next'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useArticleStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { useModalStore } from '@/stores/modal' 

const props = defineProps({
  article: { type: Object, required: true }
})

const emit = defineEmits(['close', 'clickProfile', 'clickLike'])

const articleStore = useArticleStore()
const authStore = useAuthStore()
const modal = useModalStore() 

// --- 상태 관리 ---
const isMenuOpen = ref(false)
const commentInput = ref('')

// --- 로직 ---

/**
 * 1. 내가 쓴 게시글인지 확인 (삭제 버튼 노출용)
 */
const isMyPost = computed(() => {
  const authorUsername = props.article.author?.username
  return authStore.currentUser?.username === authorUsername
})

/**
 * 2. 게시글 삭제 가능 여부 (내 글 && 24시간 이내 작성)
 */
const isDeletable = computed(() => {
  if (!isMyPost.value) return false
  if (!props.article.created_at) return false 

  const created = new Date(props.article.created_at)
  const now = new Date()
  
  // 차이값(ms) 계산
  const diff = now - created
  const oneDayInMs = 24 * 60 * 60 * 1000

  return diff < oneDayInMs
})

/**
 * 3. 게시글 삭제 로직
 */
const handleDelete = async () => {
  const ok = await modal.confirm('정말 이 게시글을 삭제하시겠습니까?', '삭제 확인', 'danger') 
  if (ok) {
    const success = await articleStore.deleteArticle(props.article.id)
    if (success) {
      modal.success('게시글이 삭제되었습니다.', '삭제 완료') 
      emit('close') 
    }
  }
}


/**
 * 3. 댓글 작성 로직
 */
const submitComment = async () => {
  // 1. 비회원 차단 알림창
  if (!authStore.isAuthenticated) {
    const ok = await modal.confirm('댓글을 남기려면 로그인이 필요합니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) {
      router.push('/auth')
    }
    return
  }

  if (!commentInput.value.trim()) return
  
  // 2. 스토어 함수 호출 (이제 스토어가 댓글 수도 올려줌)
  const newComment = await articleStore.addComment(props.article.id, commentInput.value)
  if (newComment) {
    if (!props.article.comment_list) props.article.comment_list = []
    props.article.comment_list.push(newComment)
    commentInput.value = ''
    // props.article.comment_count++ 는 이제 안 해도 됨 (스토어에서 처리)
  }
}

/**
 * 4. 댓글 삭제 로직
 */
const removeComment = async (commentId, index) => {
  const ok = await modal.confirm('댓글을 삭제하시겠습니까?', '삭제 확인', 'danger')
  if (ok) {
    const success = await articleStore.deleteComment(commentId)
    if (success) {
      // 화면에서 해당 댓글 즉시 제거
      props.article.comment_list.splice(index, 1)
      props.article.comment_count--
      modal.success('댓글이 삭제되었습니다.', '삭제 완료')
    }
  }
}

/**
 * 5. 메뉴 닫기 처리 (외부 클릭 시)
 */
const closeMenu = () => { isMenuOpen.value = false }

onMounted(async () => {
  window.addEventListener('click', closeMenu)
  // 모달 열릴 때 최신 댓글 목록 가져오기
  const data = await articleStore.fetchComments(props.article.id)
  if (data) {
    props.article.comment_list = data
  }
})

onUnmounted(() => {
  window.removeEventListener('click', closeMenu)
})

// --- 데이터 가공 ---

const emotionMap = {
  'happy': '😊', 'proud': '😎', 'yummy': '😋', 'tired': '😴', 'angry': '😤'
}

const displayUser = computed(() => {
  const user = props.article.author || {}
  return {
    name: user.username || '익명',
    photo: user.profile_image || `https://ui-avatars.com/api/?name=${user.username || 'User'}`
  }
})

const timeAgo = computed(() => {
  if (!props.article?.created_at) return '방금 전'
  const created = new Date(props.article.created_at)
  const now = new Date()
  const diff = (now - created) / 1000 
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 84600) return `${Math.floor(diff / 3600)}시간 전`
  return `${Math.floor(diff / 86400)}일 전`
})

const displayEmotion = computed(() => emotionMap[props.article.emotion] || '😶')
</script>

<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in" @click="$emit('close')">
    
    <div class="bg-white rounded-3xl w-full max-w-5xl h-[85vh] overflow-hidden flex flex-col md:flex-row shadow-2xl" @click.stop>
      
      <!-- 왼쪽: 이미지 영역 (비율 강제 제거, 원본 비율 유지, 배경색 검정) -->
      <div v-if="article.image" class="w-full md:w-[60%] bg-black md:border-r border-gray-100 relative h-[40vh] md:h-full">
        <img :src="article.image" class="w-full h-full object-contain mx-auto" />
      </div>

      <!-- 오른쪽: 컨텐츠 영역 (flex-col로 상단헤더 - 본문 - 댓글 - 입력창 분리) -->
      <div class="flex-1 flex flex-col bg-white h-full relative" :class="{'w-full': !article.image}">
        
        <!-- 1. 헤더 (고정) -->
        <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-white z-20 shrink-0">
          <div class="flex items-center gap-3">
            <img :src="displayUser.photo" @click="$emit('clickProfile', displayUser.name)" 
                 class="w-10 h-10 rounded-full border cursor-pointer hover:opacity-80" />
            <div>
              <div class="flex items-center gap-2">
                <p @click="$emit('clickProfile', displayUser.name)" class="font-bold text-gray-800 cursor-pointer hover:underline">{{ displayUser.name }}</p>
                <span class="text-xl">{{ displayEmotion }}</span>
              </div>
              <p class="text-[10px] text-gray-400">{{ timeAgo }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <!-- 오늘 쓴 글만 삭제 가능 (isDeletable) -->
            <div v-if="isDeletable" class="relative">
              <button @click.stop="isMenuOpen = !isMenuOpen" class="p-2 hover:bg-gray-100 rounded-full text-gray-500">
                <MoreHorizontal class="w-5 h-5" />
              </button>
              <div v-if="isMenuOpen" class="absolute right-0 mt-2 w-32 bg-white rounded-xl shadow-xl border py-1 z-30">
                <button @click="handleDelete" class="w-full flex items-center gap-2 px-4 py-2 text-sm text-rose-500 hover:bg-rose-50">
                  <Trash2 class="w-4 h-4" /> 삭제하기
                </button>
              </div>
            </div>
            <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-full text-gray-500"><X class="w-6 h-6" /></button>
          </div>
        </div>

        <div class="p-6 border-b border-gray-50 bg-white min-h-0 flex-[3] overflow-y-auto" 
             :class="article.image ? '' : 'shrink-0 max-h-[60vh]'">
          <div class="prose prose-sm max-w-none">
            <!-- 🎵 BGM Text Info (Top Left, No Box) -->
            <div v-if="article.music_title" class="flex items-center gap-1.5 mb-2 text-xs">
               <span>🎵</span>
               <span class="font-bold text-gray-700">{{ article.music_title }}</span>
               <span class="text-gray-400">-</span>
               <span class="text-gray-500">{{ article.music_artist }}</span>
            </div>

            <!-- 질문 표시 추가 (간격 늘림 mb-4 -> mb-10) -->
            <h3 v-if="article.question" class="text-xl font-bold text-gray-900 mb-6 leading-snug mt-0">
              Q. {{ article.question.content }}
            </h3>
            <p class="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">{{ article.content }}</p>
          </div>
        </div>

        <!-- 3. 댓글 목록 (스크롤) - 별도 영역 할당 (비율 축소) -->
        <div class="flex-1 flex flex-col min-h-[150px] max-h-[30%] bg-gray-50/50">
            <!-- 고정된 헤더 영역 -->
            <div class="p-6 pb-2 shrink-0 bg-gray-50/50 z-10 backdrop-blur-sm">
               <h3 class="font-bold text-gray-800 text-sm">
                  Comments ({{ article.comment_count || 0 }})
                </h3>
            </div>
            
            <!-- 스크롤 가능한 댓글 목록 영역 -->
            <div class="overflow-y-auto px-6 pb-6 flex-1 space-y-4">
                <div v-if="article.comment_list && article.comment_list.length > 0" class="space-y-4">
                  <div v-for="(comment, index) in article.comment_list" :key="comment.id" class="flex gap-3 group">
                    <img :src="comment.author?.profile_image || `https://ui-avatars.com/api/?name=${comment.author?.username}`" 
                         class="w-8 h-8 rounded-full object-cover shrink-0" />
                    <div class="flex-1 bg-white p-3 rounded-2xl relative shadow-sm border border-gray-100">
                      <div class="flex justify-between">
                        <span class="text-xs font-bold text-gray-800">{{ comment.author?.username }}</span>
                        <button v-if="comment.author?.username === authStore.currentUser?.username" 
                                @click="removeComment(comment.id, index)"
                                class="text-gray-300 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Trash2 class="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <p class="text-sm text-gray-700 mt-1 break-words">{{ comment.content }}</p>
                    </div>
                  </div>
                </div>
                
                <div v-else class="flex flex-col items-center justify-center text-gray-400 py-4 h-full">
                  <MessageCircle class="w-8 h-8 opacity-20 mb-2" />
                  <p class="text-xs">첫 댓글을 남겨주세요!</p>
                </div>
            </div>
        </div>

        <!-- 4. 하단 액션바 (고정) -->
        <div class="p-4 border-t border-gray-100 bg-white shrink-0">
          <div class="flex gap-4 mb-3">
            <button @click="$emit('clickLike', article)" class="flex items-center gap-2 group">
              <Heart class="w-7 h-7" :class="article.is_liked ? 'text-rose-500 fill-current' : 'text-gray-800 group-hover:text-rose-500'" />
              <span class="font-bold text-gray-800">{{ article.like_count || 0 }}</span>
            </button>
          </div>
          
          <div class="flex gap-2 items-center bg-gray-50 rounded-2xl px-4 py-2 border border-gray-100 focus-within:ring-2 focus-within:ring-primary-200 transition-all">
            <input v-model="commentInput" @keyup.enter="submitComment" type="text" placeholder="따뜻한 댓글을 남겨주세요..." 
                   class="flex-1 bg-transparent py-2 focus:outline-none text-sm" />
            <button @click="submitComment" class="text-primary-600 font-bold text-sm px-2 hover:bg-primary-50 rounded-lg py-1 transition-colors">게시</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>