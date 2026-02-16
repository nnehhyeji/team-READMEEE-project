import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api/axios'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  // 안 읽은 알림 필터
  const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

  // 1. 알림 목록 가져오기
  const fetchNotifications = async () => {
    try {
      const response = await axios.get('/notifications/')
      notifications.value = response.data
    } catch (error) {
      console.error('알림 불러오기 실패:', error)
    }
  }

  // 2. 하나 읽음 처리
  const markAsRead = async (id) => {
    try {
      // 먼저 UI 반영 (Optimistic UI)
      const target = notifications.value.find(n => n.id === id)
      if (target) target.is_read = true

      // 서버 요청
      await axios.patch(`/notifications/${id}/read/`)
    } catch (error) {
      console.error('읽음 처리 실패:', error)
    }
  }

  // 3. 모두 읽음 처리
  const markAllAsRead = async () => {
    try {
      // 먼저 UI 반영
      notifications.value.forEach(n => n.is_read = true)

      // 서버 요청
      await axios.patch('/notifications/read_all/')
    } catch (error) {
      console.error('모두 읽음 처리 실패:', error)
    }
  }

  return {
    notifications,
    unreadCount,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  }
})