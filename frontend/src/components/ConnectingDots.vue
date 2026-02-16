<script setup>
import { ref, computed } from 'vue';
import { quarterCoordinates } from '../data/dotCoordinates';

const props = defineProps({
  articles: {
    type: Array,
    default: () => [] 
  },
  isDemo: {
    type: Boolean,
    default: false
  }
});

// --- Dynamic Records Calculation ---
const currentQuarterRecords = computed(() => {
    // 1. 데모 모드일 경우 무조건 전부 true
    const dotsCount = getQuarterDots(currentQuarter.value).length;
    if (props.isDemo) return new Array(dotsCount).fill(true);

    // 2. 현재 쿼터의 날짜 범위 계산
    const currentYear = new Date().getFullYear();
    const quarterStartMonth = { 'Q1': 0, 'Q2': 3, 'Q3': 6, 'Q4': 9 }[currentQuarter.value];
    const startDate = new Date(currentYear, quarterStartMonth, 1);
    
    // 점 개수만큼 배열 생성 (기본 false)
    const records = new Array(dotsCount).fill(false);
    
    // 게시글 날짜 Set 생성 (로컬 시간 기준)
    const articleDates = new Set();
    
    props.articles.forEach(a => {
        if (!a.created_at) return;
        const d = new Date(a.created_at);
        // 브라우저 로컬 타임 기준으로 YYYY-MM-DD 변환
        const localDate = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
        articleDates.add(localDate);
    });
    
    for (let i = 0; i < dotsCount; i++) {
        const d = new Date(startDate);
        d.setDate(startDate.getDate() + i);
        // "YYYY-MM-DD" 포맷팅
        const dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
        
        if (articleDates.has(dateStr)) {
            records[i] = true;
        }
    }
    return records;
});

const quarters = ['Q1', 'Q2', 'Q3', 'Q4'];
const animationStarted = ref(false);
const visibleMaxIndex = ref(-1);
const hoveredIndex = ref(null);

const getInitialQuarter = () => {
    const month = new Date().getMonth() + 1;
    // Standard Calendar Quarters (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec)
    if (month >= 1 && month <= 3) return 'Q1';
    if (month >= 4 && month <= 6) return 'Q2';
    if (month >= 7 && month <= 9) return 'Q3';
    return 'Q4';
};
const currentQuarter = ref(getInitialQuarter());

// --- 3D Carousel Logic ---
const SPACING = 300; 

const getCardStyle = (quarter) => {
    const currentIndex = quarters.indexOf(currentQuarter.value);
    const targetIndex = quarters.indexOf(quarter);
    let diff = targetIndex - currentIndex;
    const zIndex = 10 - Math.abs(diff);
    const opacity = Math.abs(diff) > 2 ? 0 : 1; 
    const translateX = diff * SPACING;
    const scale = 1 - Math.abs(diff) * 0.15;
    const rotateY = diff * -45;
    const filter = Math.abs(diff) > 0 ? `brightness(${100 - Math.abs(diff) * 10}%) blur(${Math.abs(diff) * 2}px)` : 'none';

    return {
        zIndex,
        opacity,
        transform: `translateX(${translateX}px) scale(${scale}) perspective(1000px) rotateY(${rotateY}deg)`,
        filter
    };
};

const getCardClass = (quarter) => {
    return isActive(quarter) ? 'ring-4 ring-blue-100' : 'hover:ring-2 hover:ring-blue-200';
};

const handleCardClick = (quarter) => {
    if (currentQuarter.value !== quarter) {
        currentQuarter.value = quarter;
        resetAnimation();
    }
};

const isActive = (q) => currentQuarter.value === q;

const resetAnimation = () => {
    animationStarted.value = false;
    visibleMaxIndex.value = -1;
    hoveredIndex.value = null;
};

// --- Data Helpers ---
const getQuarterDots = (q) => quarterCoordinates[q]?.points || [];
const quarterImages = computed(() => {
    const imgs = {};
    quarters.forEach(q => imgs[q] = quarterCoordinates[q]?.image);
    return imgs;
});
const quarterImageStyles = computed(() => {
    const styles = {};
    quarters.forEach(q => styles[q] = quarterCoordinates[q]?.imageStyle);
    return styles;
});

const getQuarterLabel = (q) => {
    const labels = { 'Q1': 'Spring', 'Q2': 'Summer', 'Q3': 'Autumn', 'Q4': 'Winter' };
    return labels[q];
};

const getQuarterCompletionMessage = (q) => quarterCoordinates[q]?.message || "Completed!";

// --- Animation Logic ---
const animationLimitIndex = computed(() => {
    const dots = getQuarterDots(currentQuarter.value);
    const total = dots.length;
    
    // 1. 데모 모드면 끝까지
    if (props.isDemo) return total - 1;

    // 2. 현재 분기 및 날짜 계산
    const today = new Date();
    const currentYear = today.getFullYear();
    
    const quarterStartMonth = { 'Q1': 0, 'Q2': 3, 'Q3': 6, 'Q4': 9 }[currentQuarter.value];
    const quarterStartDate = new Date(currentYear, quarterStartMonth, 1);
    
    // 날짜 차이 계산 (일 단위)
    const diffTime = today - quarterStartDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    // 3. 아직 시작 안 한 분기 (미래) -> -1 (애니메이션 안 함)
    if (diffDays < 0) return -1;
    
    // 4. 이미 지난 분기 or 진행 중인 분기
    // - 분기 내라면 today index까지만
    // - 분기 지났으면 total - 1 (끝까지)
    // -> min(diffDays, total - 1) 하면 자동 처리됨
    return Math.min(diffDays, total - 1);
});



const getDotState = (quarter, idx) => {
    const hasToday = currentQuarterRecords.value[idx] === true;
    if (!hasToday) return 'inactive';
    if (idx === 0) return 'single'; 
    const hasYesterday = currentQuarterRecords.value[idx - 1] === true;
    return hasYesterday ? 'streak' : 'single';
};

// ...

// ---  완성 여부 체크 ---
const isFullyRevealed = computed(() => {
    const dots = getQuarterDots(currentQuarter.value);
    if (dots.length === 0) return false;
    const isAnimationDone = visibleMaxIndex.value >= dots.length - 1;
    const isLogicDone = currentQuarterRecords.value.slice(0, dots.length).every(r => r === true);
    return isAnimationDone && isLogicDone;
});



const animatedConnectedCount = computed(() => {
    return currentQuarterRecords.value.slice(0, visibleMaxIndex.value + 1).filter(r => r === true).length;
});

const isScanning = ref(false); // 애니메이션 진행 중 여부

const getDotColor = (quarter, idx) => {
    if (!isActive(quarter)) return '#cbd5e1'; 
    if (!animationStarted.value) return 'transparent';
    
    // 1. 현재 스캔 중인 점 (Cursor) - 스캔 중에만 빨간색
    if (isScanning.value && idx === visibleMaxIndex.value) return '#FF6B6B'; 

    // 2. 스캔 예정인 점
    if (idx > visibleMaxIndex.value) return 'transparent';

    // 3. 스캔 완료된 점 (및 스캔 종료 후의 마지막 점)
    const state = getDotState(quarter, idx);
    if (state === 'inactive') return '#E2E8F0'; // 원래 있던 회색 점 복구
    
    if (state === 'single') return '#CC6F73'; // Pink
    if (state === 'streak') return '#6193B6'; // Blue
    return '#cbd5e1';
};

const visibleLines = computed(() => {
    if (!animationStarted.value) return [];
    const lines = [];
    const dots = getQuarterDots(currentQuarter.value);
    
    dots.forEach((dot, index) => {
        if (index === 0 || index > visibleMaxIndex.value) return;
        if (getDotState(currentQuarter.value, index) === 'streak') {
            const prevDot = dots[index - 1];
            lines.push({ x1: prevDot.x, y1: prevDot.y, x2: dot.x, y2: dot.y });
        }
    });
    
    if (isFullyRevealed.value) {
         const lastDot = dots[dots.length - 1];
         const firstDot = dots[0];
         lines.push({ x1: lastDot.x, y1: lastDot.y, x2: firstDot.x, y2: firstDot.y });
    }
    return lines;
});



const startAnimation = () => {
    if (animationStarted.value) return;
    
    // 오늘 날짜까지만 실행
    const limit = animationLimitIndex.value;
    if (limit < 0) return; 

    animationStarted.value = true;
    isScanning.value = true; // 스캔 시작
    visibleMaxIndex.value = 0;
    
    const interval = setInterval(() => {
        if (visibleMaxIndex.value >= limit) {
            clearInterval(interval);
            isScanning.value = false; // 스캔 종료 -> 마지막 점 원래 색으로 복귀
        } else {
            visibleMaxIndex.value++;
        }
    }, 80);
};



const getProgressMessage = computed(() => {
    const dots = getQuarterDots(currentQuarter.value);
    const p = (animatedConnectedCount.value / dots.length) * 100;
    if (p >= 90) return "거의 다 왔어요! 마지막까지 꾸준히 기록해봐요.";
    if (p >= 50) return "벌써 절반이나 완성되었네요. 대단해요!";
    return "매일매일 기록하며 그림을 완성해보세요!";
});

// --- UI Helpers ---
const onDotHover = (q, idx) => { if (isActive(q)) hoveredIndex.value = idx; };
const getTooltipStyle = (q) => {
    const dots = getQuarterDots(q);
    const dot = dots[hoveredIndex.value];
    if (!dot) return {};
    return { left: `${(dot.x / 600) * 100}%`, top: `${(dot.y / 600) * 100}%`, transform: 'translate(-50%, -150%)' };
};
const getStartPromptStyle = (q) => {
    const dots = getQuarterDots(q);
    if (!dots.length) return {};
    return { left: `${(dots[0].x / 600) * 100}%`, top: `${(dots[0].y / 600) * 100}%`, transform: 'translate(-50%, -160%)' };
};
</script>
<template>
  <div class="relative w-full h-[800px] flex items-center justify-center overflow-hidden bg-[#FDFBF7] select-none perspective-1000">
    
    <div class="relative w-full h-full flex justify-center items-center transform-style-3d">
        <div 
            v-for="(quarter, index) in quarters" 
            :key="quarter"
            class="absolute w-[600px] h-[600px] transition-all duration-700 ease-out flex flex-col items-center justify-center bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden"
            :class="getCardClass(quarter)"
            :style="getCardStyle(quarter)"
            @click="handleCardClick(quarter)"
        >
            <div 
                class="absolute inset-0 z-0 flex items-center justify-center p-12 pointer-events-none"
                :class="isActive(quarter) && isFullyRevealed ? 'animate-image-enter' : 'opacity-0'"
            >
                <img 
                    v-if="quarterImages[quarter]" 
                    :src="quarterImages[quarter]" 
                    class="w-full h-full object-contain" 
                    :style="quarterImageStyles[quarter]" 
                />
            </div>

            <div class="absolute top-6 left-8 z-20">
                <h2 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-700 to-gray-500">
                    {{ quarter }}
                </h2>
                <p class="text-sm text-gray-400 font-medium tracking-wider uppercase mt-1">
                    {{ getQuarterLabel(quarter) }}
                </p>
            </div>

            <svg
              viewBox="0 0 600 600"
              preserveAspectRatio="xMidYMid meet"
              class="w-full h-full z-10 relative"
            >
              <g class="lines-layer" v-if="isActive(quarter)">
                <line
                  v-for="(line, idx) in visibleLines"
                  :key="'line-' + quarter + '-' + idx"
                  :x1="line.x1"
                  :y1="line.y1"
                  :x2="line.x2"
                  :y2="line.y2"
                  stroke="#6193B6"
                  stroke-width="2"
                  stroke-linecap="round"
                  class="streak-line"
                />
              </g>

              <g class="dots-layer">
                <circle
                  v-for="(dot, idx) in getQuarterDots(quarter)"
                  :key="'dot-' + quarter + '-' + idx"
                  :cx="dot.x"
                  :cy="dot.y"
                  r="5"
                  :fill="getDotColor(quarter, idx)"
                  class="transition-all duration-300"
                  :class="[
                      isActive(quarter) && isFullyRevealed ? 'animate-boong-twice' : '',
                      isActive(quarter) ? 'cursor-pointer' : ''
                  ]"
                  :style="{ transitionDelay: isActive(quarter) ? '0s' : (idx * 10) + 'ms' }"
                  @mouseenter="onDotHover(quarter, idx)"
                  @mouseleave="onDotHover(quarter, null)"
                />
              </g>
            </svg>

            <div v-if="isActive(quarter) && !animationStarted && getQuarterDots(quarter).length > 0" 
                 class="absolute z-30 cursor-pointer animate-bounce"
                 :style="getStartPromptStyle(quarter)"
                 @click.stop="startAnimation"
            >
               <div class="bg-[#FF6B6B] text-white px-4 py-2 rounded-full shadow-lg font-bold text-lg relative transform hover:scale-110 transition-transform">
                  Click!
                  <div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-[#FF6B6B] rotate-45"></div>
               </div>
            </div>

            <div v-if="isActive(quarter)" class="absolute bottom-8 left-0 right-0 flex justify-center z-20">
                <div class="bg-white/90 backdrop-blur-md px-6 py-3 rounded-full shadow-lg border border-gray-100 text-center min-w-[300px]">
                    <div v-if="isFullyRevealed">
                        <p class="text-base font-bold text-[#6193B6] animate-pulse">
                            🎉 {{ getQuarterCompletionMessage(quarter) }}
                        </p>
                    </div>
                    <div v-else-if="animationStarted">
                        <p class="text-sm font-semibold text-gray-700 mb-1">
                            {{ getProgressMessage }}
                        </p>
                        <p class="text-xs text-gray-400">
                             {{ animatedConnectedCount }} / {{ getQuarterDots(quarter).length }} dots connected
                        </p>
                    </div>
                    <div v-else>
                        <p class="text-sm font-medium text-gray-500">
                            Click 버튼을 눌러 기록을 확인해보세요!
                        </p>
                    </div>
                </div>
            </div>

            <div v-if="hoveredIndex !== null && isActive(quarter) && animationStarted"
                 class="absolute z-40 pointer-events-none bg-gray-800 text-white text-xs px-2 py-1 rounded shadow-xl"
                 :style="getTooltipStyle(quarter)"
            >
              Day {{ hoveredIndex + 1 }}
            </div>

            <div v-if="!isActive(quarter)" class="absolute inset-0 bg-white/40 z-20 pointer-events-none"></div>
        </div>
    </div>
  </div>
</template>


<style scoped>
.perspective-1000 { perspective: 1000px; }
.transform-style-3d { transform-style: preserve-3d; }

/* 선 애니메이션 */
.streak-line {
  stroke-dasharray: 100;
  stroke-dashoffset: 0;
  animation: drawLine 0.07s ease-out forwards;
}
@keyframes drawLine {
  from { stroke-dashoffset: 100; }
  to { stroke-dashoffset: 0; }
}

/* 점 튕기는 애니메이션 */
.animate-boong-twice {
    animation: boongTwice 2s ease-in-out forwards;
    transform-origin: center;
    transform-box: fill-box;
}
@keyframes boongTwice {
    0% { transform: scale(1) translateY(0); }
    25% { transform: scale(1.3) translateY(-15px); }
    50% { transform: scale(0.9) translateY(0); }
    75% { transform: scale(1.15) translateY(-8px); }
    100% { transform: scale(1) translateY(0); }
}

/* 그림 등장 애니메이션 */
.animate-image-enter {
    animation: imageEnter 1.5s ease-out forwards;
}
@keyframes imageEnter {
    0% { opacity: 0; transform: scale(0.95) translateY(10px); filter: blur(10px); }
    100% { opacity: 0.5; transform: scale(1) translateY(0); filter: blur(0); }
}
</style>