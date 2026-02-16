<script setup>
import { ref, computed, onMounted } from 'vue'
import { X, Image as ImageIcon, Music, Play, Pause } from 'lucide-vue-next'
import { useQuestionStore } from '@/stores/question'
import { useModalStore } from '@/stores/modal' 

const emit = defineEmits(['close', 'createArticle'])
const questionStore = useQuestionStore()
const modal = useModalStore() 

const content = ref('')
const emotion = ref(null)
const image = ref(null)
const previewUrl = ref(null)
const fileInput = ref(null)
const isBgmOn = ref(false)
const isPublic = ref(true)

const musicInfo = computed(() => {
  const q = questionStore.todayQuestion
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

const emotions = [
  { id: 'happy', emoji: '😊', label: 'Happy' },
  { id: 'proud', emoji: '😎', label: 'Proud' },
  { id: 'yummy', emoji: '😋', label: 'Yummy' },
  { id: 'tired', emoji: '😴', label: 'Tired' },
  { id: 'angry', emoji: '😤', label: 'Angry' }, 
]

onMounted(async () => {
  await questionStore.fetchTodayQuestion()
})

const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0]
  if (selectedFile) {
    image.value = selectedFile
    previewUrl.value = URL.createObjectURL(selectedFile)
  }
}

import { supabase } from '@/lib/supabase'
import axios from '@/api/axios'

const handlePost = async () => {
  if (!emotion.value) {
    modal.alert('오늘의 기분을 선택해주세요!', '알림', 'danger')
    return
  }
  if (!content.value.trim()) {
    modal.alert('내용을 입력해주세요!', '알림', 'danger')
    return
  }

  let uploadedImageUrl = null
  let imageFile = null

  if (image.value) {
    try {
      const fileExt = image.value.name.split('.').pop()
      const fileName = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}.${fileExt}`

      const { data: signData } = await axios.post('/articles/upload-url/', {
        filename: fileName
      })

      // [Fallback] 로컬 저장소 모드인 경우
      if (signData.storage === 'local') {
        imageFile = image.value
      } else {
        // Supabase 모드
        if (!supabase) {
          throw new Error('Supabase client is not initialized. Please check your environment variables or use local storage mode.')
        }

        await fetch(signData.signedUrl, {
            method: 'PUT',
            body: image.value,
            headers: {
                'Content-Type': image.value.type
            }
        })

        const { data: publicUrlData } = supabase.storage
          .from('ReadMe-images')
          .getPublicUrl(signData.path)
        
        uploadedImageUrl = publicUrlData.publicUrl
      }

    } catch (error) {
      console.error('Image Upload Error:', error)
      modal.alert('이미지 업로드에 실패했습니다.', '오류', 'danger')
      return
    }
  }

  emit('createArticle', { 
    content: content.value, 
    emotion: emotion.value,
    image: imageFile || uploadedImageUrl, // File 객체 또는 URL 문자열
    question_id: questionStore.todayQuestion?.id,
    is_public: isPublic.value,
    music_title: isBgmOn.value ? musicInfo.value?.title : null,
    music_artist: isBgmOn.value ? musicInfo.value?.artist : null,
  })
  
  content.value = ''
  emotion.value = null
  image.value = null
  previewUrl.value = null
  isPublic.value = true
}
</script>

<template>
  <div class="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fade-in">
    <div class="bg-white rounded-3xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-primary-50/30 to-purple-50/30">
        <div class="flex-1 pr-4">
          <p class="text-xs font-bold text-primary-500 uppercase tracking-wider mb-1">Today's Question</p>
          <h2 class="text-lg font-bold text-gray-800 leading-tight">
            {{ questionStore.todayQuestion?.content || '오늘의 질문을 불러오는 중...' }}
          </h2>
        </div>
        <button 
          @click="$emit('close')" 
          class="p-2 hover:bg-gray-200 rounded-full transition-colors flex-shrink-0"
        >
          <X class="w-6 h-6 text-gray-500" />
        </button>
      </div>

      <div class="p-6 overflow-y-auto scrollbar-hide">
        
        <!-- Music Section -->
        <div v-if="musicInfo" class="mb-8 bg-gradient-to-br from-[#69A9C5] to-[#B6CDDD] p-5 rounded-3xl border border-indigo-100 relative overflow-hidden">
            <div class="flex items-stretch gap-4 relative z-10">
               
               <div class="w-32 rounded-xl overflow-hidden shadow-lg bg-black flex-shrink-0 group relative min-h-full">
                  <iframe 
                    v-if="isBgmOn"
                    :src="`https://www.youtube.com/embed/${musicInfo.videoId}?autoplay=1&controls=0&modestbranding=1&rel=0`" 
                    class="w-full h-full object-cover pointer-events-none" 
                    frameborder="0" 
                    allow="autoplay; encrypted-media" 
                  ></iframe>
                  <div v-else class="w-full h-full flex items-center justify-center bg-indigo-200/50">
                    <Music class="w-8 h-8 text-indigo-400 animate-pulse" />
                  </div>
               </div>

               <div class="flex-1 min-w-0 flex flex-col justify-between">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                       <span class="px-2 py-0.5 bg-white/60 text-[10px] font-bold text-[#69A9C5] rounded-md backdrop-blur-sm border border-indigo-100">
                         Today's BGM
                       </span>
                       
                       <button 
                        @click="isBgmOn = !isBgmOn"
                        class="flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold transition-all"
                        :class="isBgmOn ? 'bg-[#69A9C5] text-white' : 'bg-white text-[#69A9C5] border border-indigo-100 shadow-sm'"
                       >
                         <component :is="isBgmOn ? Pause : Play" class="w-3 h-3" />
                         {{ isBgmOn ? 'BGM OFF' : 'BGM ON' }}
                       </button>
                    </div>
                    <h4 class="font-bold text-gray-900 leading-tight truncate">{{ musicInfo.title }}</h4>
                    <p class="text-xs text-gray-900 truncate mb-3">{{ musicInfo.artist }}</p>
                  </div>
                  
                  <div class="flex items-start gap-1.5 bg-white/50 p-2.5 rounded-xl border border-indigo-50">
                    <span class="text-xs select-none">💡</span>
                    <p class="text-[11px] text-gray-900 leading-snug line-clamp-2 italic">
                       {{ musicInfo.reason }}
                    </p>
                  </div>
               </div>
            </div>
        </div>

        <p class="text-sm font-bold text-gray-700 mb-3">How are you feeling?</p>
        <div class="flex gap-3 mb-6 overflow-x-auto py-4 scrollbar-hide px-1">
          <button 
            v-for="emo in emotions" 
            :key="emo.id" 
            @click="emotion = emo.id" 
            class="flex flex-col items-center justify-center w-20 h-24 rounded-2xl border-2 transition-all flex-shrink-0" 
            :class="emotion === emo.id ? 'border-primary-500 bg-primary-50 scale-110 shadow-md' : 'border-gray-100 hover:border-primary-200'"
          >
            <span class="text-3xl mb-2">{{ emo.emoji }}</span>
            <span class="text-xs font-medium text-gray-600">{{ emo.label }}</span>
          </button>
        </div>

        <p class="text-sm font-bold text-gray-700 mb-3">Your thoughts</p>
        <textarea 
          v-model="content" 
          class="w-full h-40 p-4 border-2 border-gray-100 rounded-2xl mb-6 focus:border-primary-300 focus:outline-none resize-none text-gray-700 placeholder:text-gray-300" 
          placeholder="오늘의 질문에 대한 당신의 생각을 자유롭게 적어주세요..."
        ></textarea>
        
        <p class="text-sm font-bold text-gray-700 mb-3">Add a photo (optional)</p>
        <div v-if="previewUrl" class="mb-3 relative group">
          <img :src="previewUrl" class="w-full h-64 object-cover rounded-2xl border border-gray-100" />
          <button 
            @click="triggerFileUpload" 
            class="absolute inset-0 bg-black/40 text-white opacity-0 group-hover:opacity-100 flex items-center justify-center rounded-2xl transition-opacity font-medium backdrop-blur-[2px]"
          >
            사진 변경하기
          </button>
        </div>
        <button 
          v-else 
          @click="triggerFileUpload"
          class="w-full border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center gap-2 text-gray-400 hover:border-primary-300 hover:bg-primary-50 transition-all group"
        >
          <ImageIcon class="w-8 h-8 group-hover:text-primary-400" />
          <span class="text-sm">Upload an image</span>
        </button>
        <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" class="hidden" />
      </div>

      <!-- Action Bar -->
      <div class="p-6 border-t border-gray-100 flex gap-3 bg-white items-center">
        <label class="flex items-center gap-2 cursor-pointer p-2 hover:bg-gray-50 rounded-lg transition-colors">
            <div class="relative inline-flex items-center">
                <input type="checkbox" v-model="isPublic" class="sr-only peer">
                <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary-500"></div>
            </div>
            <span class="text-sm font-medium text-gray-600 select-none min-w-[60px]">
                {{ isPublic ? '전체 공개' : '나만 보기' }}
            </span>
        </label>

        <div class="flex-1 flex gap-3 justify-end">
            <button 
              @click="$emit('close')" 
              class="px-6 py-3 rounded-full border border-gray-200 font-bold text-gray-500 hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
            <button 
              @click="handlePost" 
              class="px-8 py-3 rounded-full bg-gray-400 text-white font-bold shadow-lg shadow-primay-200 hover:shadow-gray-500 transition-all active:scale-95"
            >
              답변 완료
            </button>
        </div>
      </div>
    </div>
  </div>
</template>