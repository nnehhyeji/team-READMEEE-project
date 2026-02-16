<script setup>
import { useRouter } from 'vue-router'
import { Heart, User, MessageCircle, X, CheckCheck } from 'lucide-vue-next'
import { useNotificationStore } from '@/stores/notification' 

const emit = defineEmits(['close'])
const router = useRouter()
const notiStore = useNotificationStore()

// 아이콘 매핑
const getIcon = (type) => (type === 'like' ? Heart : type === 'follow' ? User : MessageCircle)
const getIconColor = (type) => 'bg-[#507B9B]/10 text-[#507B9B]'

// 알림 텍스트 생성
const getNotificationText = (noti) => {
  if (noti.notification_type === 'like') return 'liked your post.'
  if (noti.notification_type === 'comment') return 'commented on your post.'
  if (noti.notification_type === 'follow') return 'started following you.'
  return 'sent a notification.'
}

// 클릭 핸들러
const handleNotificationClick = (noti) => {
  notiStore.markAsRead(noti.id)
  emit('close')
  
  // 타입별 이동 경로
  if (noti.notification_type === 'follow') {
    router.push(`/profile/${noti.sender.username}`) // 팔로우 -> 프로필
  } else if (noti.article) {
    router.push(`/profile/${noti.sender.username}`)
  }
}

// 시간 포맷팅 (YYYY-MM-DDT... -> YYYY-MM-DD HH:MM)
const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
</script>

<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in" @click="$emit('close')">
    <div class="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl flex flex-col max-h-[70vh]" @click.stop>
      
      <div class="flex items-center justify-between p-6 border-b border-gray-100">
        <div>
          <h2 class="text-xl font-bold text-gray-800">Notifications</h2>
          <p class="text-xs mt-1 transition-colors" :class="notiStore.unreadCount > 0 ? 'text-[#507B9B] font-bold' : 'text-gray-400'">
            {{ notiStore.unreadCount > 0 ? `You have ${notiStore.unreadCount} unread messages` : 'All caught up! 🎉' }}
          </p>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-full cursor-pointer">
          <X class="w-6 h-6 text-gray-400" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-2">
        <div 
          v-for="noti in notiStore.notifications" 
          :key="noti.id" 
          @click="handleNotificationClick(noti)" 
          class="flex items-start gap-4 p-4 rounded-2xl transition-all cursor-pointer relative mb-1" 
          :class="{'bg-[#507B9B]/5': !noti.is_read, 'hover:bg-gray-50': noti.is_read}"
        >
          <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" :class="getIconColor(noti.notification_type)">
            <component :is="getIcon(noti.notification_type)" class="w-5 h-5 fill-current" />
          </div>
          <div class="flex-1">
            <p class="text-sm text-gray-800">
              <span class="font-bold">{{ noti.sender.username }}</span> 
              {{ getNotificationText(noti) }}
            </p>
            <p class="text-xs text-gray-400 mt-1">{{ formatTime(noti.created_at) }}</p>
          </div>
          <div v-if="!noti.is_read" class="w-2 h-2 rounded-full bg-[#507B9B] mt-2 flex-shrink-0"></div>
        </div>

        <div v-if="notiStore.notifications.length === 0" class="text-center py-10 text-gray-400">
          No notifications yet.
        </div>
      </div>

      <div class="p-4 border-t border-gray-100 text-center">
        <button 
          @click="notiStore.markAllAsRead" 
          :disabled="notiStore.unreadCount === 0"
          class="flex items-center justify-center gap-2 w-full text-[#507B9B] font-bold text-sm hover:underline disabled:text-gray-300 disabled:no-underline cursor-pointer disabled:cursor-not-allowed"
        >
          <CheckCheck class="w-4 h-4" />
          Mark all as read
        </button>
      </div>

    </div>
  </div>
</template>