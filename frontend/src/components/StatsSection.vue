<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router' 
import ConnectingDots from '@/components/ConnectingDots.vue'

/**
 * [PROPS] 부모로부터 실시간 통계 데이터를 받습니다.
 */
const props = defineProps({
  // { 'happy': { count: 5, percentage: 35 }, ... }
  emotionData: { type: Object, default: () => ({}) },
  // [ { word: '커피', count: 12 }, ... ]
  wordData: { type: Array, default: () => [] },
  // Linked articles for context
  articles: { type: Array, default: () => [] }
})

// --- 탭 상태 관리 ---
const currentView = ref('stats') // 'stats' | 'dots'

const route = useRoute()

/**
 * [디자인 설정] 감정 ID에 따른 이름, 이모지, 색상 매핑 (유저 요청 5컬러 적용)
 * F4C0D6 (핑크/Yummy), F9F18F (옐로/Happy), D3FFC3 (그린/Proud), F68C47 (오렌지/Angry), D0EAF4 (블루/Tired)
 */
const emotionConfig = {
  happy: { label: '행복해', emoji: '😊', color: '#FFA06E' }, // Orange
  proud: { label: '뿌듯해', emoji: '😎', color: '#25D0FB' }, // Blue
  yummy: { label: '맛있어', emoji: '😋', color: '#DDF988' }, // Lime
  tired: { label: '피곤해', emoji: '😴', color: '#68A993' }, // Green
  angry: { label: '화가나', emoji: '😤', color: '#FEB3C7' }, // Pink
  default: { label: '기타', emoji: '😶', color: '#CBD5E1' }
}

const colorPalette = Object.values(emotionConfig).map(c => c.color).filter(c => c !== '#CBD5E1')

/**
 * [감정 데이터 가공] 백엔드 객체 데이터를 차트용 배열로 변환
 */
const emotionStats = computed(() => {
  if (!props.emotionData) return []
  return Object.entries(props.emotionData).map(([key, value]) => {
    const config = emotionConfig[key] || emotionConfig.default
    return {
      id: key,
      label: config.label, emoji: config.emoji, color: config.color,
      percent: value.percentage, 
      count: value.count
    }
  })
})

/**
 * [단어 데이터 가공] Text Cloud용 데이터
 * 1. 빈도수 내림차순 정렬 -> 상위 30개 추출
 * 2. 그 중 상위 5개는 'isTop' 플래그 (밑줄 및 팝업용)
 * 3. 팝업에 띄울 관련 게시글(matchedArticle) 찾기
 * 4. 전체 배열을 랜덤 섞기 (비정렬 배치)
 */
const processedWords = computed(() => {
  if (!props.wordData || props.wordData.length === 0) return []
  
  // 1. Sort by count desc & Take Top 30
  let sorted = [...props.wordData].sort((a, b) => b.count - a.count).slice(0, 30)
  
  const maxCount = sorted[0]?.count || 1
  const minCount = sorted[sorted.length - 1]?.count || 1

  // 2. Map data (Assign size, top flag, matched article)
  // 랜덤 회전값을 고정하기 위해 시드 기반 혹은 인덱스 기반으로 변경하지 않고,
  // computed가 재호출되지 않도록 주의. (props가 바뀌지 않으면 유지됨)
  const mapped = sorted.map((w, index) => {
    // 폰트 크기 고정 (1.5rem)
    const size = 1.5

    // 상위 5개 플래그
    const isTop = index < 5
    
    // 관련 게시글 찾기
    let matchedArticle = null
    if (isTop && props.articles) {
       matchedArticle = props.articles.find(a => a.content && a.content.includes(w.word))
    }

    // 회전값 제거 (가독성 및 떨림 방지) - 0deg로 고정
    // 유저가 "떨린다"고 하는 것이 텍스트 구름의 랜덤 회전 때문일 수도 있음.
    const rotate = 0

    return {
      ...w,
      fontSize: `${size}rem`,
      rotation: `rotate(${rotate}deg)`,
      isTop,
      matchedArticle
    }
  })

  // 3. Shuffle (Fisher-Yates)
  for (let i = mapped.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [mapped[i], mapped[j]] = [mapped[j], mapped[i]];
  }

  return mapped
})

/**
 * [SVG 수학] 도넛 차트 Paths
 */
const hoveredStat = ref(null)
const chartPaths = computed(() => {
  let cumulativePercent = 0
  return emotionStats.value.map(stat => {
    const startX = Math.cos(2 * Math.PI * cumulativePercent)
    const startY = Math.sin(2 * Math.PI * cumulativePercent)
    cumulativePercent += stat.percent / 100
    const endX = Math.cos(2 * Math.PI * cumulativePercent)
    const endY = Math.sin(2 * Math.PI * cumulativePercent)
    const largeArcFlag = stat.percent / 100 > 0.5 ? 1 : 0
    // 도넛 홀을 위해 path 수정 없이 viewBox로 조정 (기존 유지)
    const pathData = [`M ${startX} ${startY}`, `A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}`, `L 0 0`].join(' ')
    return { ...stat, path: pathData }
  })
})
</script>

<template>
  <div class="animate-fade-in font-sans">
    
    <!-- 서브 탭 (Stats vs Connecting Dots) -->
    <div class="flex justify-center mb-6">
      <div class="bg-gray-100 p-1 rounded-xl inline-flex">
        <button 
          @click="currentView = 'stats'"
          class="px-4 py-2 rounded-lg text-sm font-bold transition-all"
          :class="currentView === 'stats' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-400 hover:text-gray-600'"
        >
          감정 & 단어
        </button>
        <button 
          @click="currentView = 'dots'"
          class="px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2"
          :class="currentView === 'dots' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-400 hover:text-gray-600'"
        >
          Connecting Dots
        </button>
      </div>
    </div>

    <!-- 1. 기존 통계 뷰 -->
    <div v-if="currentView === 'stats'" class="grid md:grid-cols-2 gap-6">
       <!-- 감정 도넛 차트 -->
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center justify-between min-h-[400px]">
        <h3 class="font-bold text-gray-900 text-xl w-full text-center mb-4">감정통계</h3>
        
        <div v-if="emotionStats.length > 0" class="relative w-56 h-56">
            <!-- SVG Chart -->
            <svg viewBox="-1 -1 2 2" class="w-full h-full transform -rotate-90 overflow-visible">
            <defs>
              <linearGradient v-for="stat in emotionStats" :key="`grad-${stat.id}`" :id="`grad-${stat.id}`" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" :stop-color="stat.color" stop-opacity="0.9" />
                <stop offset="100%" :stop-color="stat.color" stop-opacity="0.1" />
              </linearGradient>
            </defs>
            <template v-for="stat in chartPaths" :key="stat.id">
                <!-- L 0 0 로 파이차트를 그리고, 중앙에 흰 원을 덮어서 얇은 도넛으로 만듦 -->
                <path :d="stat.path" :fill="`url(#grad-${stat.id})`"
                class="transition-opacity duration-300 cursor-pointer hover:opacity-100"
                :class="hoveredStat && hoveredStat.id !== stat.id ? 'opacity-30' : 'opacity-100'"
                @mouseenter="hoveredStat = stat" @mouseleave="hoveredStat = null" />
            </template>
            </svg>
            
            <!-- Center Hole Overlay (This makes the Pie a Donut) -->
            <!-- inset-8 (크게 잡아서 얇게 만듦) -->
            <div class="absolute inset-8 bg-white rounded-full flex flex-col items-center justify-center pointer-events-none shadow-inner">
            <!-- Center Label -->
            <div class="text-center">
                <span class="text-3xl block mb-1">
                {{ hoveredStat ? hoveredStat.emoji : (emotionStats[0]?.emoji || '😊') }}
                </span>
                <span class="text-sm font-bold text-gray-800">
                {{ hoveredStat ? hoveredStat.label : (emotionStats[0]?.label || '감정') }}
                </span>
            </div>
            </div>
        </div>
        <div v-else class="text-center py-10 text-gray-400 font-medium">기록된 감정이 없습니다. 💭</div>
        
        <!-- Legend (하단 리스트 형태) -->
        <div class="w-full space-y-2 mt-4 max-w-[200px]">
            <div v-for="stat in emotionStats" :key="stat.id" class="flex items-center justify-between text-sm">
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: stat.color }"></span>
                <span class="text-gray-500 font-medium">{{ stat.emoji }} {{ stat.label }}</span>
            </div>
            <span class="font-bold text-gray-700">{{ stat.count }}회</span>
            </div>
        </div>
        </div>

        <!-- 단어 텍스트 구름 -->
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col min-h-[400px]">
        <h3 class="font-bold text-gray-900 text-xl w-full text-center mb-8">가장 많이 사용한 단어</h3>
        
        <div v-if="processedWords.length > 0" class="flex-1 flex flex-wrap content-center justify-center items-center gap-x-2 gap-y-3 p-6 max-w-lg mx-auto">
            
            <!-- Text Item -->
            <div v-for="item in processedWords" :key="item.word" 
                class="group relative"
                :style="{ transform: item.rotation }">
                
            <div class="relative inline-block">
                <!-- Custom Highlighter Background (Top 5 only) -->
                <!-- Square corners, slightly narrower than text (left-1 right-1) -->
                <div v-if="item.isTop" class="absolute bottom-0.5 left-1 right-1 h-5 bg-gray-200/50 z-0"></div>

                <!-- Word Text -->
                <span class="relative z-10 text-2xl transition-all duration-200 selection:bg-transparent"
                    :class="item.isTop 
                        ? 'font-semibold text-gray-900 cursor-pointer' 
                        : 'font-light text-gray-300 cursor-default'">
                {{ item.word }}
                </span>

                <!-- Popup (Only for top items with a matched article) -->
                <div v-if="item.isTop && item.matchedArticle" 
                    class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 hidden group-hover:block z-50 pointer-events-none">
                <div class="bg-white rounded-lg shadow-xl overflow-hidden border border-gray-200 p-2 animate-fade-in pointer-events-auto">
                    <img v-if="item.matchedArticle.image" :src="item.matchedArticle.image" class="w-full h-32 object-cover rounded-md mb-2" />
                    <p class="text-xs text-gray-600 line-clamp-3 font-medium">{{ item.matchedArticle.content }}</p>
                    <p class="text-[10px] text-gray-400 mt-1 text-right">{{ item.matchedArticle.created_at?.slice(0, 10) }}</p>
                </div>
                <!-- Tip arrow -->
                <div class="w-3 h-3 bg-white transform rotate-45 border-r border-b border-gray-200 absolute -bottom-1.5 left-1/2 -translate-x-1/2"></div>
                </div>
            </div>

            </div>

        </div>
        <div v-else class="text-center py-24 text-gray-400 font-medium">분석할 단어가 부족합니다. ✍️</div>
        </div>
    </div>
    
    <!-- 2. Connecting Dots 뷰 -->
    <div v-if="currentView === 'dots'">
        <ConnectingDots :articles="props.articles" :is-demo="route.query.demo === 'true'" />
    </div>

  </div>
</template>

<style scoped>
/* Pretendard 적용을 위해 tailwind config 설정을 따름 */
</style>