<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useArticleStore } from '@/stores/articles'
import DetailModal from '@/components/DetailModal.vue'
import { useRouter } from 'vue-router'
import { useModalStore } from '@/stores/modal' 
const props = defineProps({
  userId: { type: Number, required: true },
  username: { type: String, required: true },
  isMe: { type: Boolean, default: false }
})

const articleStore = useArticleStore()
const router = useRouter()
const modal = useModalStore() 

// --- Data & Constants ---
const CUSTOM_EMOJIS = [
  { id: 'c1', hex: '#2967EB', emoji: '☀️' },
  { id: 'c2', hex: '#FF6200', emoji: '☁️' },
  { id: 'c3', hex: '#FFBB00', emoji: '😊' },
  { id: 'c4', hex: '#767676', emoji: '😎' },
  { id: 'c5', hex: '#FF1888', emoji: '😋' },
  { id: 'c6', hex: '#A000CB', emoji: '😴' },
  { id: 'c7', hex: '#117B45', emoji: '😤' },
  { id: 'c8', hex: '#B6B6B6', emoji: '🌧️' },
]

const GRID_COLORS = {
  v: ['#FFBB00', '#2967EB', '#FF1888', '#117B45', '#FF6200', '#A000CB'],
  h: ['#B6B6B6', '#FF6200', '#A000CB', '#B6B6B6', '#117B45']
}

// Calendar Logic
const currentDate = ref(new Date())
const monthlyArticles = ref([])
const isLoading = ref(false)

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth() + 1)
const currentMonthName = computed(() => {
  return currentDate.value.toLocaleString('en-US', { month: 'long' })
})

// Stickers Logic
const isEditMode = ref(false)
const stickers = ref({}) 
const scatteredEmojis = ref([]) 

// Dragging State
const draggingItem = ref(null) // The item object being dragged
const dragOffset = ref({ x: 0, y: 0 }) // Mouse offset relative to item
const originalPos = ref({ x: 0, y: 0 })

// --- Calendar Computation ---
const monthDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value - 1
  const firstDay = new Date(year, month, 1).getDay()
  const lastDate = new Date(year, month + 1, 0).getDate()
  
  const days = []
  // Prev month filler
  for (let i = firstDay - 1; i >= 0; i--) {
     const d = new Date(year, month, -i)
     days.push({ date: d, current: false, dateKey: formatKey(d) })
  }
  // Current month
  for (let i = 1; i <= lastDate; i++) {
    const d = new Date(year, month, i)
    days.push({ date: d, current: true, dateKey: formatKey(d) })
  }
  // Next month filler
  const remain = 42 - days.length
  for (let i = 1; i <= remain; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ date: d, current: false, dateKey: formatKey(d) })
  }
  return days
})

function formatKey(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const changeMonth = (delta) => {
  currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + delta))
  fetchMonthlyArticles()
}

// --- Sticker Pool Initialization ---
const initScatteredEmojis = () => {
  // Double the emojis
  const doublePool = [...CUSTOM_EMOJIS, ...CUSTOM_EMOJIS]
  
  // Generate random positions within the LEFT container area
  scatteredEmojis.value = doublePool.map(item => ({
    ...item,
    uid: Math.random().toString(36).substr(2, 9),
    // Constrain random range to fit nicely in the left panel
    x: 20 + Math.random() * 200, 
    y: 50 + Math.random() * 400, // More vertical space
    rotate: (Math.random() - 0.5) * 45,
    scale: 1,
    zIndex: 10,
    isDragging: false
  }))
}

// --- Drag & Drop Logic (Custom Physics) ---

const startDrag = (event, item) => {
  if (!isEditMode.value) return
  event.preventDefault()
  
  draggingItem.value = item
  item.isDragging = true
  item.zIndex = 50 
  item.scale = 1.2
  item.rotate = 0 

  const clientX = event.clientX || event.touches?.[0].clientX
  const clientY = event.clientY || event.touches?.[0].clientY

  dragOffset.value = {
    x: clientX - item.x,
    y: clientY - item.y
  }
  originalPos.value = { x: item.x, y: item.y }

  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', onDragEnd)
  window.addEventListener('touchmove', onDragMove, { passive: false })
  window.addEventListener('touchend', onDragEnd)
}

const onDragMove = (event) => {
  if (!draggingItem.value) return
  const clientX = event.clientX || event.touches?.[0].clientX
  const clientY = event.clientY || event.touches?.[0].clientY

  draggingItem.value.x = clientX - dragOffset.value.x
  draggingItem.value.y = clientY - dragOffset.value.y
}

const onDragEnd = (event) => {
  if (!draggingItem.value) return

  const item = draggingItem.value
  const clientX = event.clientX || event.changedTouches?.[0].clientX
  const clientY = event.clientY || event.changedTouches?.[0].clientY

  const elements = document.elementsFromPoint(clientX, clientY)
  const cell = elements.find(el => el.hasAttribute('data-date-key'))
  
  if (cell) {
    const key = cell.getAttribute('data-date-key')
    placeSticker(key, item)
    // Remove from pool
    scatteredEmojis.value = scatteredEmojis.value.filter(i => i.uid !== item.uid)
  } else {
    // Drop outside: FREE MOVEMENT
    item.rotate = (Math.random() - 0.5) * 45
  }

  // Cleanup
  item.isDragging = false
  item.scale = 1
  item.zIndex = 10
  draggingItem.value = null
  
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
  window.removeEventListener('touchmove', onDragMove)
  window.removeEventListener('touchend', onDragEnd)
}

const placeSticker = (dateKey, item) => {
  stickers.value[dateKey] = {
    emoji: item.emoji,
    hex: item.hex,
    id: item.id
  }
}

const removeSticker = (dateKey) => {
  const sticker = stickers.value[dateKey]
  if (sticker) {
     scatteredEmojis.value.push({
       ...sticker,
       uid: Math.random().toString(),
       x: 20 + Math.random() * 200,
       y: 50 + Math.random() * 350,
       rotate: (Math.random() - 0.5) * 45,
       scale: 1,
       zIndex: 10,
       isDragging: false
     })
     delete stickers.value[dateKey]
  }
}

// --- API & Persistence ---
const fetchMonthlyArticles = async () => {
  if (!props.isMe) return
  isLoading.value = true
  try {
    const res = await articleStore.fetchMyArchive({
      year: currentYear.value,
      month: currentMonth.value,
      limit: 100
    })
    monthlyArticles.value = res
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const loadStickers = () => {
  const saved = localStorage.getItem(`calendar_stickers_${props.username}`)
  if (saved) {
    try { stickers.value = JSON.parse(saved) } catch (e) {}
  }
}

const saveStickers = () => {
  localStorage.setItem(`calendar_stickers_${props.username}`, JSON.stringify(stickers.value))
  isEditMode.value = false
  modal.success('저장되었습니다!', '성공')
}

const toggleEditMode = () => {
  if (isEditMode.value) {
    isEditMode.value = false
    loadStickers() // Revert
  } else {
    isEditMode.value = true
    if (scatteredEmojis.value.length === 0) {
      initScatteredEmojis()
    }
  }
}

onMounted(() => {
  fetchMonthlyArticles()
  loadStickers()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
})

// Modal
const selectedArticle = ref(null)
const openDetail = (article) => { selectedArticle.value = article }
</script>

<template>
  <div class="w-full min-h-[800px] p-4 flex flex-col items-center">
    
    <!-- Controls Header -->
    <div class="w-full max-w-6xl flex items-center justify-between mb-4 px-4">
      <div class="flex items-center gap-4">
        <h2 class="text-3xl font-sans tracking-tighter text-gray-800">
          <span class="font-light mr-2">{{ currentMonthName }}</span>
          <span class="font-bold text-gray-200">{{ currentYear }}</span>
        </h2>
        <div class="flex gap-1">
           <button @click="changeMonth(-1)" class="p-1.5 hover:bg-white hover:shadow-sm rounded-full transition-all text-slate-400"><ChevronLeft :size="20" /></button>
           <button @click="changeMonth(1)" class="p-1.5 hover:bg-white hover:shadow-sm rounded-full transition-all text-slate-400"><ChevronRight :size="20" /></button>
        </div>
      </div>
      
      <div v-if="isMe" class="flex gap-2">
         <button v-if="!isEditMode" @click="toggleEditMode" class="btn-primary">
            Edit Moods
         </button>
         <template v-else>
            <button @click="toggleEditMode" class="btn-secondary">Cancel</button>
            <button @click="saveStickers" class="btn-primary">Save Changes</button>
         </template>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex w-full max-w-7xl gap-8 relative items-start">
      
      <!-- LEFT: Sticker Pool (Edit Mode Only) -->
      <transition name="fade-slide">
        <div v-if="isEditMode" class="hidden lg:block w-[320px] h-[600px] relative shrink-0">
          
          <!-- The Draggable Stickers -->
          <div 
             v-for="chip in scatteredEmojis" 
             :key="chip.uid"
             class="absolute flex items-center justify-center cursor-grab active:cursor-grabbing shadow-lg rounded-full select-none transition-transform duration-100"
             :style="{
                width: '48px',
                height: '48px',
                backgroundColor: chip.hex,
                left: chip.x + 'px',
                top: chip.y + 'px',
                transform: `rotate(${chip.rotate}deg) scale(${chip.scale})`,
                zIndex: chip.zIndex
             }"
             @mousedown="startDrag($event, chip)"
             @touchstart.passive="startDrag($event, chip)"
          >
             <span class="text-3xl filter drop-shadow-sm pointer-events-none">{{ chip.emoji }}</span>
          </div>
          
          <!-- Instruction Text at Bottom -->
          <div class="absolute bottom-0 left-0 w-full text-left text-[11px] leading-relaxed text-gray-800 font-bold opacity-80 pointer-events-none px-4">
             Drag and drop the circles matching your mood or today’s weather. Play at your own risk! May cause tears and laughter!
          </div>
        </div>
      </transition>

      <!-- RIGHT: Calendar Grid -->
      <div class="flex-1 select-none w-full">
        
        <!-- Days Header -->
        <div class="grid grid-cols-7 mb-2 text-center">
          <div v-for="day in ['sun','mon','tue','wed','thu','fri','sat']" :key="day" 
               class="text-xs font-bold text-gray-400 tracking-wider">
            {{ day }}
          </div>
        </div>

        <!-- The Grid -->
        <!-- Fixed height removed to allow aspect-square responsive resizing -->
        <div class="relative w-full border-l border-slate-100">
           <!-- Grid Background Lines -->
           <div class="absolute inset-0 pointer-events-none z-0">
              <!-- Vertical Lines -->
              <div v-for="i in 6" :key="'v'+i" class="absolute top-0 bottom-0" 
                :style="{ 
                   left: (i * (100/7)) + '%',
                   width: '2px',
                   backgroundColor: GRID_COLORS.v[i-1] || '#ccc'
                }">
              </div>
              
              <!-- Horizontal Lines -->
              <div v-for="i in 5" :key="'h'+i" class="absolute left-0 right-0 h-[1.5px]" 
                 :style="{ 
                   top: (i * (100/6)) + '%',
                   backgroundColor: GRID_COLORS.h[i-1] || '#eee'
                 }">
              </div>
           </div>

           <!-- Cells -->
           <div class="grid grid-cols-7 relative z-10 text-sm">
              <div v-for="d in monthDays" :key="d.dateKey"
                   :data-date-key="d.dateKey"
                   class="aspect-square relative group hover:bg-white/30 border-b border-slate-100/50"
                   :class="{'border-b-0': false}" 
              >
                 <!-- Date Number -->
                 <div class="absolute top-2 left-2 z-20 text-[9px] font-medium text-gray-300" 
                      :class="d.current ? 'text-gray-400' : 'text-gray-200 opacity-50'">
                    {{ d.date.getDate() }}
                 </div>

                 <!-- Sticker Layer -->
                 <div v-if="stickers[d.dateKey]" 
                      class="absolute inset-0 flex items-center justify-center animate-pop-in"
                 >
                    <div class="w-12 h-12 rounded-full shadow-md flex items-center justify-center text-3xl relative group/sticker"
                         :style="{ backgroundColor: stickers[d.dateKey].hex, transform: 'rotate(-5deg)' }"
                    >
                       {{ stickers[d.dateKey].emoji }}
                       
                       <button v-if="isEditMode" @click="removeSticker(d.dateKey)" class="absolute -top-1 -right-1 bg-white rounded-full p-1 shadow-sm opacity-0 group-hover/sticker:opacity-100 transition-opacity hover:text-rose-500">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M18 6L6 18M6 6l12 12"/></svg>
                       </button>
                    </div>
                 </div>

              </div>
           </div>
        </div>

      </div>

    </div>

    <DetailModal v-if="selectedArticle" :article="selectedArticle" @close="selectedArticle = null" />

  </div>
</template>

<style scoped>
.btn-primary {
  @apply px-4 py-1.5 bg-slate-900 text-white font-bold rounded-full text-xs hover:bg-slate-800 transition-all shadow-md active:scale-95;
}
.btn-secondary {
  @apply px-4 py-1.5 bg-white text-slate-600 font-bold rounded-full text-xs border border-slate-200 hover:bg-slate-50 transition-all active:scale-95;
}

.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@keyframes popIn {
  0% { transform: scale(0) rotate(-45deg); opacity: 0; }
  60% { transform: scale(1.2) rotate(10deg); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
.animate-pop-in {
  animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
</style>
