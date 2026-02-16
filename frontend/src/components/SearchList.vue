<script setup>
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'

const props = defineProps({
  articles: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['open-detail'])

const searchQuery = ref('')

// Client-side filtering
const searchResults = computed(() => {
    if (!searchQuery.value.trim()) return props.articles
    
    const query = searchQuery.value.toLowerCase()
    return props.articles.filter(article => {
        const contentMatch = article.content?.toLowerCase().includes(query)
        const emotionMatch = article.emotion?.toLowerCase().includes(query)
        const questionMatch = article.question?.content?.toLowerCase().includes(query)
        return contentMatch || emotionMatch || questionMatch
    })
})

const getEmotionEmoji = (emotion) => {
  const map = { 'happy': '😊', 'proud': '😎', 'yummy': '😋', 'tired': '😴', 'angry': '😤' }
  return map[emotion] || '😶'
}

const openDetail = (article) => {
  emit('open-detail', article)
}
</script>

<template>
    <div class="animate-fade-in">
      <div class="flex items-center gap-2 mb-6 bg-gray-100 px-4 py-3 rounded-2xl">
        <Search class="text-gray-400 w-5 h-5"/>
        <input 
          v-model="searchQuery" 
          placeholder="내 질문이나 답변을 검색해보세요..." 
          class="bg-transparent w-full outline-none text-gray-800 placeholder-gray-400"
        />
      </div>

      <div v-if="searchResults.length > 0" class="space-y-4">
        <div 
          v-for="article in searchResults" 
          :key="article.id" 
          @click="openDetail(article)"
          class="flex gap-4 p-4 border border-gray-100 rounded-2xl hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200">
            <img v-if="article.image" :src="article.image" class="w-full h-full object-cover"/>
            <div v-else class="w-full h-full flex items-center justify-center text-2xl bg-yellow-50">
               {{ getEmotionEmoji(article.emotion) }}
            </div>
          </div>
          <div class="overflow-hidden">
            <p class="text-xs text-blue-500 font-bold mb-1">{{ article.question ? article.question.content : '자유 기록' }}</p>
            <p class="text-sm text-gray-800 line-clamp-2">{{ article.content }}</p>
            <p class="text-xs text-gray-400 mt-2">{{ new Date(article.created_at).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-20 text-gray-400">
        <p v-if="searchQuery">검색 결과가 없습니다.</p>
        <p v-else>기록이 없습니다.</p>
      </div>
    </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
