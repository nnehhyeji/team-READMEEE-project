import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/api/axios'

export const useQuestionStore = defineStore('question', () => {
  // 1. 상태 (State)
  const todayQuestion = ref(null)

  // 2. 액션 (Actions)
  const fetchTodayQuestion = async () => {
    if (todayQuestion.value) return

    try {
      const response = await axios.get('/questions/today/')

      // console.log('오늘의 질문 로딩 성공:', response.data)

      todayQuestion.value = response.data
    } catch (error) {
      console.error('질문 로딩 실패:', error.response?.data || error.message)
    }
  }

  // 외부에서 사용할 수 있도록 리턴
  return { todayQuestion, fetchTodayQuestion }
})