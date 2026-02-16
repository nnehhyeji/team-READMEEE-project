<script setup>
import { ref, onMounted, watch } from 'vue' 
import { useRouter, useRoute } from 'vue-router'
import { Home, Trophy, User, Settings, Bell, Menu, X, LogOut } from 'lucide-vue-next'
import NotificationModal from '@/components/NotificationModal.vue'
import { useNotificationStore } from '@/stores/notification'

import { useAuthStore } from '@/stores/auth'
import { useModalStore } from '@/stores/modal' 

const router = useRouter()
const route = useRoute()
const notiStore = useNotificationStore()
const authStore = useAuthStore()
const modal = useModalStore() 

// 메뉴 열림 상태 관리
const isMenuOpen = ref(false)
const showNoti = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}



const handleNavClick = async (item) => {
  if (item.requiresAuth && !authStore.isAuthenticated) {
    const ok = await modal.confirm('로그인이 필요한 서비스입니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) router.push('/auth');
    return;
  }
  router.push(item.path);
  if (window.innerWidth < 1024) isMenuOpen.value = false;
}

const handleNotiClick = async () => {
  if (!authStore.isAuthenticated) {
    const ok = await modal.confirm('알람을 확인하려면 로그인이 필요합니다. \n로그인하시겠습니까?', '로그인 필요', 'danger')
    if (ok) router.push('/auth');
    return;
  }
  notiStore.fetchNotifications();
  showNoti.value = true;
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    notiStore.fetchNotifications()
  }
})


watch(
  () => route.path,
  () => {
    isMenuOpen.value = false
  }
)

const navItems = [
  { path: '/feed', icon: Home, label: 'Home', requiresAuth: false },
  { path: '/best', icon: Trophy, label: 'Weekly Best', requiresAuth: false },
  { path: '/profile', icon: User, label: 'My Profile', requiresAuth: true },
  { path: '/settings', icon: Settings, label: 'Settings', requiresAuth: true },
]
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div v-if="route.path !== '/'">
    <!-- 데스크탑용 햄버거 버튼 (모바일에서는 숨김) -->
    <button 
      @click="toggleMenu"
      class="fixed top-3 right-6 z-[60] p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 hidden md:block"
    >
      <Menu v-if="!isMenuOpen" class="w-6 h-6" />
      <X v-else class="w-6 h-6" />
    </button>

    <!-- 데스크탑용 슬라이딩 사이드바 -->
    <div 
      class="fixed top-0 right-0 h-screen w-64 bg-[#F8F7F4]/80 backdrop-blur-md shadow-2xl z-[50] transition-transform duration-300 ease-in-out border-l border-gray-100 py-20 px-4 hidden md:block"
      :class="isMenuOpen ? 'translate-x-0' : 'translate-x-full'"
    >
      <nav class="flex flex-col gap-2">
        <!-- 로고 / 홈 (ReadMe) -->
        <button 
          @click="goHome" 
          class="text-left px-4 py-4 mb-2 font-black text-2xl tracking-tighter text-[#FEA2A3] transition-all hover:opacity-80"
        >
          READMEEE
        </button>

        


        <TransitionGroup name="list" tag="div" class="flex flex-col gap-2">
            <button 
            v-for="(item, index) in navItems" 
            :key="item.path" 
            v-show="isMenuOpen"
            :style="{ transitionDelay: `${(index + 1) * 100}ms` }"
            @click="handleNavClick(item)"
            class="flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ease-out group w-full"
            :class="route.path === item.path ? 'bg-primary-50 text-[#FEA2A3] font-bold shadow-sm' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'"
            >
            <component :is="item.icon" class="w-5 h-5" />
            <span class="text-[15px] font-medium">{{ item.label }}</span>
            </button>
        </TransitionGroup>

        <Transition name="fade-slide" mode="out-in">
             <button 
                v-if="isMenuOpen" 
                @click="handleNotiClick" 
                class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-500 hover:bg-gray-50 hover:text-gray-900 transition-all duration-300 delay-200 relative w-full mt-2"
            >
                <div class="relative">
                <Bell class="w-5 h-5" />
                <span v-if="notiStore.unreadCount > 0" class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-rose-500 rounded-full border border-white"></span>
                </div>
                <span class="text-[15px] font-medium">Notifications</span>
            </button>
        </Transition>

      <!-- 로그아웃 버튼 추가 (하단 분리) -->
      <div class="mt-8 pt-4 border-t border-gray-100">
        <button 
          v-if="authStore.isAuthenticated"
          @click="authStore.logout(); router.push('/auth');" 
          class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-400 hover:bg-rose-50 hover:text-rose-500 transition-all w-full"
        >
          <LogOut class="w-5 h-5" />
          <span class="text-[15px] font-medium">Log out</span>
        </button>
        
        <button 
          v-else
          @click="router.push('/auth');" 
          class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-500 hover:bg-primary-50 hover:text-primary-600 transition-all w-full"
        >
          <LogOut class="w-5 h-5 rotate-180" />
          <span class="text-[15px] font-medium">Log in</span>
        </button>
      </div>
    </nav>
  </div>

  <!-- 사이드바 백드롭 (데스크탑용) -->
  <div 
    v-if="isMenuOpen" 
    @click="isMenuOpen = false" 
    class="fixed inset-0 z-[40] bg-black/5 backdrop-blur-sm hidden md:block transition-opacity duration-300"
    :class="isMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'"
  ></div>

  <!-- 모바일 하단 네비게이션 바 (Mobile Bottom Nav) -->
  <div class="fixed bottom-0 left-0 w-full bg-white border-t border-gray-100 px-6 py-3 flex justify-between items-center z-[50] md:hidden pb-safe">
    <button 
      v-for="item in navItems" 
      :key="item.path" 
      @click="handleNavClick(item)"
      class="flex flex-col items-center gap-1 p-2 rounded-lg transition-colors"
      :class="route.path === item.path ? 'text-[#FEA2A3]' : 'text-gray-400'"
    >
      <component :is="item.icon" class="w-6 h-6" :stroke-width="route.path === item.path ? 2.5 : 2" />
      <span class="text-[10px] font-medium">{{ item.label }}</span>
    </button>
    
    <!-- 모바일 알림 버튼 -->
    <button 
      @click="handleNotiClick"
      class="flex flex-col items-center gap-1 p-2 rounded-lg transition-colors relative"
      :class="showNoti ? 'text-[#FEA2A3]' : 'text-gray-400'"
    >
      <div class="relative">
        <Bell class="w-6 h-6" :stroke-width="showNoti ? 2.5 : 2" />
        <span v-if="notiStore.unreadCount > 0" class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-rose-500 rounded-full border border-white"></span>
      </div>
      <span class="text-[10px] font-medium">Alerts</span>
    </button>
  </div>

  <NotificationModal v-if="showNoti" @close="showNoti = false" />
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* List Stagger Animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>