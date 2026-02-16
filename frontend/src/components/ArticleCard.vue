<script setup>
import { Heart, MessageCircle, Clock, Lock } from 'lucide-vue-next' 
import { computed } from 'vue'

const props = defineProps({
  article: { type: Object, required: true },
  showQuestion: { type: Boolean, default: false },
  dateFormat: { type: String, default: 'relative' }
})

const emit = defineEmits(['selectArticle', 'clickProfile', 'clickLike'])

const emotionMap = {
  'happy': '😊',
  'proud': '😎',
  'yummy': '😋',
  'tired': '😴',
  'angry': '😤',
}

// 1. 작성자(Author) 정보 연결 [백엔드 UserSummarySerializer 기준]
const displayAuthor = computed(() => {
  const author = props.article.author || {}
  return {
    name: author.username || '익명', //
    photo: author.profile_image || `https://ui-avatars.com/api/?name=${author.username || 'User'}&background=random&color=fff`
  }
})

// 2. 작성 시간 로직 (dateFormat에 따라 분기)
const displayDate = computed(() => {
  if (!props.article.created_at) return ''

  // A. 절대 날짜 형식 (2024. 12. 19.)
  if (props.dateFormat === 'absolute') {
    const date = new Date(props.article.created_at)
    return `${date.getFullYear()}. ${date.getMonth() + 1}. ${date.getDate()}.`
  }

  // B. 상대 날짜 형식 (방금 전, n분 전)
  const created = new Date(props.article.created_at)
  const now = new Date()
  const diff = (now - created) / 1000

  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return `${Math.floor(diff / 86400)}일 전`
})

// 3. 남은 시간 계산 (24시간 카운트다운 - expires_at 기준)
const remainingTime = computed(() => {
  if (!props.article.expires_at) return '24h left'
  
  const expire = new Date(props.article.expires_at)
  const now = new Date()
  const diffMs = expire - now
  
  if (diffMs <= 0) return '만료됨'
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  return hours > 0 ? `${hours}시간 남음` : `${minutes}분 남음`
})

const displayEmotion = computed(() => {
  // 백엔드 Article 모델의 emotion 필드값을 매핑합니다.
  return emotionMap[props.article.emotion] || props.article.emotion || '🤔'
})

const handleProfileClick = () => {
  emit('clickProfile', displayAuthor.value.name)
}
</script>

<template>
  <div 
    @click="$emit('selectArticle', article)"
    class="bg-white rounded-3xl overflow-hidden shadow-sm border border-primary-100 break-inside-avoid hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer group mb-6"
  >
    <div v-if="article.image" class="w-full relative overflow-hidden">
      <img :src="article.image" class="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105" />
      <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors"></div>
    </div>

    <div class="p-6">
      <div class="flex items-start gap-3 mb-4">
        <img 
          :src="displayAuthor.photo" 
          @click.stop="handleProfileClick" 
          class="w-10 h-10 rounded-full object-cover border border-gray-100 cursor-pointer hover:opacity-80 transition-opacity z-10" 
        />
        
        <div class="flex-1">
          <div class="flex items-center justify-between">
             <div class="flex items-center gap-2">
                <span @click.stop="handleProfileClick" class="font-bold text-gray-800 cursor-pointer hover:underline hover:text-primary-600 z-10">
                  {{ displayAuthor.name }}
                </span>
                <span class="text-xl animate-bounce-slow">{{ displayEmotion }}</span>
                
                <!-- 나만 보기 표시 (작성자 본인에게만 보임) -->
                <div v-if="!article.is_public" class="flex items-center gap-1 text-[10px] px-2 py-0.5">
                    <Lock class="w-3 h-3" />
                    <!-- <span>나만 보기</span> -->
                </div>
             </div>
             
             <div v-if="dateFormat === 'relative'" class="flex items-center gap-1 text-xs text-primary-400 bg-primary-50 px-2 py-1 rounded-full font-medium">
                <Clock class="w-3 h-3" />
                <span>{{ remainingTime }}</span> 
             </div>
          </div>
          
          <p class="text-xs text-gray-400 mt-1">{{ displayDate }}</p>
        </div>
      </div>

      <!-- 질문 표시 (옵션) -->
      <div v-if="showQuestion && article.question" class="mb-3 p-3 bg-primary-50/50 rounded-xl border border-primary-100">
        <span class="text-[10px] font-bold text-black uppercase tracking-wider block mb-1">Q. Question</span>
        <p class="text-sm font-bold text-gray-700">{{ article.question.content }}</p>
      </div>

      <p class="text-gray-700 leading-relaxed mb-4 line-clamp-4">{{ article.content }}</p>
      
      <div class="flex gap-4 pt-4 border-t border-gray-100 text-gray-500">
        <button 
          @click.stop="$emit('clickLike', article)" 
          class="flex items-center gap-2 transition-colors group/btn" 
          :class="article.is_liked ? 'text-rose-500' : 'hover:text-rose-500'"
        >
          <Heart class="w-5 h-5 transition-transform active:scale-75" :class="{'fill-current': article.is_liked}" /> 
          <span class="text-sm font-medium">{{ article.like_count || 0 }}</span>
        </button>

        <button class="flex items-center gap-2 hover:text-primary-500 transition-colors">
          <MessageCircle class="w-5 h-5" /> 
          <span class="text-sm font-medium">{{ article.comment_count || 0 }}</span>
        </button>
      </div>
    </div>
  </div>
</template>