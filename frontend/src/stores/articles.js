import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

export const useArticleStore = defineStore('articles', () => {
  const articles = ref([])
  const hasAnswered = ref(false)
  const authStore = useAuthStore()

  // 1. [READ] 게시글 목록 가져오기(피드)
  const getArticles = async () => {
    try {
      // 인스턴스 설정에 따라 '/articles/'로 요청
      const response = await axios.get('/articles/')
      articles.value = response.data
      const today = new Date().toLocaleDateString('en-CA')   // 오늘 날짜(KST 기준) 구하기

      // 내가 오늘 이 질문에 대해 작성한 글이 있는지 확인
      const myTodayArticle = articles.value.find(article => {
        const authorName = article.author?.username
        const isMine = authorName === authStore.currentUser?.username
        const isToday = article.created_at?.startsWith(today)
        return isMine && isToday
      })
      hasAnswered.value = !!myTodayArticle
    } catch (error) {
      console.error('데이터 가져오기 실패:', error)
    }
  }

  // 2. [CREATE] 게시글 작성하기 (매개변수 이름 통일)
  const createArticle = async ({ content, emotion, image, question_id, music_title, music_artist, is_public = true }) => {
    try {
      const formData = new FormData()
      formData.append('content', content)
      formData.append('emotion', emotion || 'happy')
      formData.append('question_id', question_id)
      formData.append('is_public', is_public)

      // BGM 정보 추가 (있을 경우에만)
      if (music_title) formData.append('music_title', music_title)
      if (music_artist) formData.append('music_artist', music_artist)

      if (image) formData.append('image', image)

      const response = await axios.post('/articles/', formData)

      // 작성 성공 시 목록 최상단에 추가 (백엔드 응답 데이터 구조 반영)
      articles.value.unshift(response.data)
      hasAnswered.value = true
      return true
    } catch (error) {
      console.error('글 작성 실패:', error.response?.data)
      return false
    }
  }

  // 3. [DELETE] 게시글 삭제
  const deleteArticle = async (articleId) => {
    try {
      await axios.delete(`/articles/${articleId}/`)
      articles.value = articles.value.filter(a => a.id !== articleId)
      hasAnswered.value = false
      return true
    } catch (error) {
      console.error('삭제 실패:', error)
      return false
    }
  }

  // 4. [CREATE] 댓글 작성 (content 사용)
  const addComment = async (articleId, content) => {
    if (!authStore.isAuthenticated) {
      alert('로그인 후 댓글을 남길 수 있습니다. 💬')
      return null
    }

    try {
      const response = await axios.post(`/articles/${articleId}/comment_create/`, {
        content: content
      })

      // 댓글 작성 성공 시 해당 게시글의 댓글 수도 1 증가시킴
      const target = articles.value.find(a => a.id === articleId)
      if (target) {
        target.comment_count++
      }
      return response.data
    } catch (error) {
      console.error('댓글 작성 실패:', error)
      return null
    }
  }

  // 5. [READ] 댓글 목록 가져오기
  const fetchComments = async (articleId) => {
    try {
      const response = await axios.get(`/articles/${articleId}/comment_list/`)
      return response.data
    } catch (error) {
      console.error('댓글 로딩 실패:', error)
      return []
    }
  }

  // 6. [DELETE] 댓글 삭제
  const deleteComment = async (commentId) => {
    try {
      await axios.delete(`/comments/${commentId}/`)
      return true
    } catch (error) {
      console.error('댓글 삭제 실패:', error)
      return false
    }
  }

  // 7. [UPDATE] 좋아요 토글
  const toggleLike = async (articleId) => {
    // [비회원 차단]
    if (!authStore.isAuthenticated) {
      alert('로그인이 필요한 기능입니다.')
      return false
    }

    try {
      await axios.post(`/articles/${articleId}/like/`)

      // 스토어가 관리하는 전체 게시글 목록에서 해당 게시글을 찾습니다.
      const target = articles.value.find(a => a.id === articleId)
      if (target) {
        // 내 로컬 데이터를 즉시 수정 (피드와 모달에 동시 반영됨)
        target.is_liked = !target.is_liked
        target.is_liked ? target.like_count++ : target.like_count--
      }
      return true
    } catch (error) {
      console.error('좋아요 실패:', error)
      return false
    }
  }

  // 8. [CREATE] 체류 시간 기록 (매개변수 이름 통일)
  const recordDwellTime = async (articleId, dwell_seconds) => {
    try {
      await axios.post(`/articles/${articleId}/record_dwell_time/`, {
        dwell_seconds: dwell_seconds
      })
      return true
    } catch (error) {
      console.error('체류 시간 전송 실패:', error)
      return false
    }
  }

  // 9. [READ] 특정 유저의 게시글만 가져오기(프로필 페이지)
  const fetchUserArticles = async (username) => {
    try {
      // 백엔드에서 필터링 기능을 제공한다고 가정 (예: /articles/?username=...)
      const response = await axios.get(`/articles/?username=${username}`)
      return response.data
    } catch (error) {
      console.error('유저 게시글 로딩 실패:', error)
      return []
    }
  }

  // 10. [READ] 내 아카이브 조회 (필터링 지원)
  const fetchMyArchive = async (params = {}) => {
    try {
      // params: { year, month, search, limit, etc. }
      const response = await axios.get('/articles/my_archive/', { params })

      // 페이지네이션 응답인 경우 results 반환, 아니면 데이터 그대로 반환
      if (response.data.results) {
        return response.data.results
      }
      return response.data
    } catch (error) {
      console.error('내 아카이브 로딩 실패:', error)
      return [] // 실패시 빈 배열 반환
    }
  }

  // [READ] 감정 통계 가져오기
  const fetchMonthlyStats = async (year, month) => {
    try {
      const response = await axios.get('/statistics/my/', {
        params: { year, month }
      })
      return response.data
    } catch (error) {
      console.error('감정 통계 로딩 실패:', error)
      return null
    }
  }

  // [READ] 단어 빈도 가져오기
  const fetchWordFrequency = async (year, month) => {
    try {
      const response = await axios.get('/statistics/word_frequency/', {
        params: { year, month }
      })
      return response.data.word_frequency
    } catch (error) {
      console.error('단어 빈도 로딩 실패:', error)
      return []
    }
  }
  return {
    articles,
    hasAnswered,
    getArticles,
    createArticle,
    deleteArticle,
    addComment,
    fetchComments,
    deleteComment,
    toggleLike,
    recordDwellTime,
    fetchUserArticles,
    fetchMyArchive,
    fetchMonthlyStats,
    fetchWordFrequency,
  }
})