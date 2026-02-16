import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/api/axios'

export const useSocialStore = defineStore('social', () => {
    const followers = ref([])
    const followings = ref([])
    const searchResults = ref([])
    const isLoading = ref(false)

    // 1. 팔로우/언팔로우 액션
    const toggleFollow = async (username, isFollowing) => {
        const url = `/accounts/users/${username}/${isFollowing ? 'unfollow' : 'follow'}/`
        try {
            await axios({ method: isFollowing ? 'delete' : 'post', url })
            return true
        } catch (error) {
            console.error('Follow Error:', error)
            return false
        }
    }

    // 2. 목록 가져오기
    const fetchFollowList = async (username, type) => {
        isLoading.value = true
        try {
            const response = await axios.get(`/accounts/users/${username}/${type}/`)
            if (type === 'followers') followers.value = response.data
            else followings.value = response.data
            return response.data
        } catch (error) {
            return []
        } finally {
            isLoading.value = false
        }
    }

    // 3. 사용자 검색
    const searchUsers = async (query) => {
        isLoading.value = true
        try {
            const response = await axios.get(`/accounts/search/?q=${query}`)
            searchResults.value = response.data
            return response.data
        } catch (error) {
            console.error('검색 에러:', error)
            return []
        } finally {
            isLoading.value = false
        }
    }

    return {
        followers, followings, searchResults, isLoading,
        toggleFollow, fetchFollowList, searchUsers
    }
})