<script setup>
import { computed } from 'vue'

const props = defineProps({
  article: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0
  }
})

const hasImage = computed(() => !!props.article.image)

const isTextOnly = computed(() => !hasImage.value)

// (YYYY.MM.DD)
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}.${month}.${day}`
}

const formattedDate = computed(() => formatDate(props.article.created_at))

// Deterministic tilts (Expanded/Varied)
const tilts = [-5, 3.5, -3, 6, -4, 2.5, -6, 4.5, -2, 5];
const baseTilt = computed(() => tilts[props.index % tilts.length]);
const hoverTilt = computed(() => baseTilt.value + (baseTilt.value > 0 ? 1.5 : -1.5));

// Border Radius: Top corners only
const borderRadius = '12px 12px 0 0';

const cardStyle = computed(() => ({
  '--tilt': `${baseTilt.value}deg`,
  '--tilt-offset': `${hoverTilt.value}deg`,
  // Initial state: Pushed down (translateY) and rotated
  transform: `translateY(8px) rotate(${baseTilt.value}deg)`,
  borderRadius: borderRadius
}));
</script>

<template>
  <div class="flex flex-col items-center group cursor-pointer w-full mb-6 relative">
     <!-- No margin-bottom on the component itself if grid gap handles it, but keeping mb-6 for safety or removing if gap-y-16 is enough -->
    
    <!-- Slot Area: overflow-hidden clips the bottom -->
    <div class="relative w-full px-2 overflow-hidden h-[160px] sm:h-[180px] flex items-end justify-center">
      
      <!-- The Floating Card -->
      <div 
        :style="cardStyle"
        class="w-[85%] aspect-[4/3] overflow-hidden transition-all duration-500 ease-in-out shadow-sm group-hover:shadow-2xl origin-bottom group-hover:-translate-y-4"
        :class="isTextOnly ? 'bg-[#FDFAEF] border border-gray-100' : 'bg-gray-100'"
      >
        <!-- Case A: Text Only -->
        <template v-if="isTextOnly">
          <div class="w-full h-full flex flex-col p-6 text-xs text-gray-600 leading-relaxed overflow-hidden">
            <p class="whitespace-pre-line text-[11px] md:text-[12px] opacity-80 break-keep font-medium">
              {{ article.content }}
            </p>
          </div>
        </template>
        
        <!-- Case B: Image -->
        <template v-else>
          <div class="relative w-full h-full"> 
            <img :src="article.image" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
            <div class="absolute inset-0 bg-black/5 group-hover:bg-black/0 transition-colors"></div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- The Line and Date -->
    <div class="w-full relative z-10 px-2">
      <div class="h-[1.5px] bg-[#222] w-full rounded-full" />
      <div class="pt-3 pb-1">
        <p class="font-mono text-[10px] text-center font-bold text-gray-400 tracking-wider uppercase">
          {{ formattedDate }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
