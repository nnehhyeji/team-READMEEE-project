<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  }
})

// 화면 너비 감지
const windowWidth = ref(window.innerWidth)

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

// 반응형 컬럼 개수 계산
const columnCount = computed(() => {
  if (windowWidth.value >= 1024) return 3 // lg
  if (windowWidth.value >= 768) return 2  // md
  return 1                                // base
})

// 아이템 분배 로직 (Shortest Column First)
// 각 컬럼의 예상 높이를 추적하여, 가장 짧은 컬럼에 다음 아이템을 배치합니다.
const columns = computed(() => {
  const cols = Array.from({ length: columnCount.value }, () => [])
  const colHeights = new Array(columnCount.value).fill(0) // 각 컬럼의 누적 높이(가중치)

  props.items.forEach((item) => {
    // 1. 높이 가중치 계산 (Heuristic)
    // - 이미지가 있으면: 높음 (약 +300)
    // - 텍스트 길이: 글자당 약간의 높이 추가
    const hasImage = !!item.image
    const contentLength = item.content ? item.content.length : 0
    
    let weight = 100 // 기본 카드 헤더/패딩
    if (hasImage) {
      weight += 300 // 이미지 가중치
    }
    // 텍스트 가중치 (최대 150으로 제한)
    weight += Math.min(contentLength * 0.5, 150)

    // 2. 가장 짧은 컬럼 찾기
    let minIndex = 0
    let minHeight = colHeights[0]

    for (let i = 1; i < columnCount.value; i++) {
      if (colHeights[i] < minHeight) {
        minHeight = colHeights[i]
        minIndex = i
      }
    }

    // 3. 해당 컬럼에 추가 및 높이 갱신
    cols[minIndex].push(item)
    colHeights[minIndex] += weight
  })
  
  return cols
})
</script>

<template>
  <div class="flex gap-6 items-start w-full">
    <div 
      v-for="(colItems, colIndex) in columns" 
      :key="colIndex" 
      class="flex-1 flex flex-col gap-6 w-full min-w-0"
    >
      <div v-for="item in colItems" :key="item.id || item._id || JSON.stringify(item)">
        <!-- 부모에서 디자인을 정할 수 있도록 슬롯 제공 -->
        <slot :item="item"></slot>
      </div>
    </div>
  </div>
</template>
