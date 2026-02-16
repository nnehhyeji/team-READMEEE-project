<script setup>
import { ref, computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import DetailModal from '@/components/DetailModal.vue'
import { useArticleStore } from '@/stores/articles'
import { useRouter } from 'vue-router'

const props = defineProps({
  articles: {
    type: Array,
    required: true,
    default: () => []
  },
  username: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['open-detail'])
const router = useRouter()
const articleStore = useArticleStore()

// --- Calendar State ---
const currentDate = ref(new Date())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth() + 1)

// --- Daily Timeline Logic ---
const dailyDays = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate()
  return Array.from({ length: daysInMonth }, (_, i) => i + 1)
})

const getDayStyle = (day) => {
  // Wave logic from ProfileCalendarArchive
  const amplitude = 40 
  const frequency = 0.4 
  // Start from Right (Max Amplitude) using Cosine
  const xOffset = Math.cos((day - 1) * frequency) * amplitude
  
  return {
    transform: `translateX(${xOffset}px)`
  }
}

const getDayColor = (day) => {
  const group = Math.floor((day - 1) / 7)
  return group % 2 === 0 ? '#CC6F73' : '#6193B6' 
}

const isToday = (day) => {
  const today = new Date()
  return today.getDate() === day && 
         today.getMonth() + 1 === currentMonth.value && 
         today.getFullYear() === currentYear.value
}

// Find article for specific day within the provided props.articles
// Filter logic: Match Year, Month, Day
const getArticleForDay = (day) => {
  return props.articles.find(article => {
    const d = new Date(article.created_at)
    return d.getDate() === day && 
           d.getMonth() + 1 === currentMonth.value && 
           d.getFullYear() === currentYear.value
  })
}

const changeMonth = (delta) => {
  currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + delta))
}

// Handler
const openDetail = (article) => {
  emit('open-detail', article)
}

</script>

<template>
    <div class="animate-fade-in relative min-h-[600px] bg-[#FEFBF0] rounded-3xl p-6 overflow-hidden border border-gray-100 shadow-sm">
        
        <!-- Background Decoration (Top User Info) -->
        <div class="absolute top-6 left-6 z-10">
            <h3 class="text-[#6193B6] font-light text-lg">{{ username }} (Archive)</h3>
        </div>

        <!-- Middle Left Year/Month -->
        <div class="absolute top-1/2 left-6 -translate-y-1/2 z-10 pointer-events-none">
             <div class="text-[#6193B6] text-xl font-light">{{ currentYear }}</div>
             <div class="text-[#6193B6] text-4xl font-light mt-1">{{ String(currentMonth).padStart(2, '0') }}</div>
        </div>
        
         <!-- Nav Controls (Floating) -->
         <div class="absolute bottom-6 left-6 z-20 flex gap-2">
            <button @click="changeMonth(-1)" class="p-2 bg-white/50 hover:bg-white rounded-full shadow-sm text-[#6193B6] transition"><ChevronLeft /></button>
            <button @click="changeMonth(1)" class="p-2 bg-white/50 hover:bg-white rounded-full shadow-sm text-[#6193B6] transition"><ChevronRight /></button>
         </div>

        <!-- Timeline Container -->
        <div class="relative w-full h-full flex justify-center py-10 overflow-y-auto max-h-[600px] scrollbar-hide">
            
            <div class="flex flex-col items-center gap-[16px] w-[300px] relative z-10 pb-20"> <!-- Gap approx 40px height per item -->
                <div v-for="day in dailyDays" :key="day" 
                     class="relative flex items-center justify-center transition-transform duration-500 ease-in-out"
                     :style="getDayStyle(day)">
                    
                    <!-- Day Number Action -->
                    <button 
                         @click="getArticleForDay(day) ? openDetail(getArticleForDay(day)) : null"
                         class="text-xl font-light tracking-widest relative group transition-all"
                         :class="{ 
                             'cursor-pointer hover:scale-125': getArticleForDay(day),
                             'cursor-default opacity-80': !getArticleForDay(day) 
                         }"
                         :style="{ color: getDayColor(day) }"
                    >
                         {{ String(day).padStart(2, '0') }}

                         <!-- Today Indicator -->
                         <div v-if="isToday(day)" class="absolute inset-0 -m-3 border-2 border-[#436889] rounded-full opacity-50"></div>
                         
                         <!-- Content Indicator (Dot) -->
                         <div v-if="getArticleForDay(day)" 
                              class="absolute -right-3 top-0 w-2 h-2 rounded-full animate-pulse"
                              :style="{ backgroundColor: getDayColor(day) }">
                         </div>

                        <!-- Hover Tooltip -->
                        <div v-if="getArticleForDay(day)" 
                             class="opacity-0 group-hover:opacity-100 absolute left-8 top-1/2 -translate-y-1/2 bg-white shadow-lg p-2 rounded-lg text-xs w-32 pointer-events-none z-50 transition-opacity">
                             {{ getArticleForDay(day).content?.slice(0, 15) }}...
                             <div v-if="getArticleForDay(day).image" class="mt-1 w-full h-20 rounded bg-gray-100 overflow-hidden">
                                 <img :src="getArticleForDay(day).image" class="w-full h-full object-cover">
                             </div>
                        </div>
                    </button>
                    
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* Hide scrollbar */
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>