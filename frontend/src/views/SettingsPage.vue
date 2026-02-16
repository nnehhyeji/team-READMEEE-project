<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/api/axios' 
import { useAuthStore } from '@/stores/auth'
import { useModalStore } from '@/stores/modal' 
import { storeToRefs } from 'pinia'
import { Lock, Bell, Shield, ChevronRight, LogOut, Download, Camera, Loader2 } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const authStore = useAuthStore()
const { currentUser, profileImageUrl } = storeToRefs(authStore)
const modal = useModalStore() 

// 소셜 로그인 유저 여부 확인
const isSocialUser = computed(() => {
  return currentUser.value?.provider && currentUser.value.provider !== 'email'
})

const activeTab = ref('account')
const fileInput = ref(null)
const isUpdating = ref(false) 

// 알림 설정 (Backend 연동)
const notificationSettings = ref({
  likes: true, comments: true, requests: true, weekly: true, daily: false
})

const profileForm = ref({
  username: '',
  bio: ''
})

// 초기값 설정 및 유저 정보 변경 감지
watch(() => currentUser.value, (newUser) => {
  if (newUser) {
    profileForm.value.username = newUser.username
    profileForm.value.bio = newUser.bio || ''
    
    // 알림 설정 동기화
    notificationSettings.value = {
      likes: newUser.noti_likes ?? true,
      comments: newUser.noti_comments ?? true,
      requests: newUser.noti_follows ?? true, // requests -> noti_follows
      weekly: newUser.noti_weekly ?? true,
      daily: newUser.noti_daily ?? false
    }
  }
}, { immediate: true, deep: true })

/**
 * 알림 설정 자동 저장
 */
const updateNotification = async (key, value) => {
  // 1. 백엔드 필드명 매핑
  const fieldMap = {
    likes: 'noti_likes',
    comments: 'noti_comments',
    requests: 'noti_follows',
    weekly: 'noti_weekly',
    daily: 'noti_daily',
    email: 'noti_email'
  }
  
  const backendField = fieldMap[key]
  if (!backendField) return

  // 2. FormData 생성
  const formData = new FormData()
  formData.append(backendField, value) 

  // 3. 서버 전송 
  try {
    const success = await authStore.updateProfile(formData)
    if (!success) {
      console.error('설정 저장 실패')
    }
  } catch (error) {
    console.error(error)
  }
}

/**
 * 아이디 입력 제한 (영문/숫자/8자)
 */
const handleUsernameInput = (e) => {
  profileForm.value.username = e.target.value.replace(/[^a-zA-Z0-9_]/g, '').slice(0, 8)
}

/**
 * 프로필 사진 변경 및 서버 즉시 전송
 */
const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUpdating.value = true
  try {
    // 1. 백엔드에서 업로드 방식 확인 (Signed URL or Local Storage)
    const { data } = await axios.post('/accounts/upload-url/', { 
      filename: file.name 
    })
    
    // [Fallback] 로컬 저장 모드인 경우
    if (data.storage === 'local') {
      const formData = new FormData()
      formData.append('profile_image', file) 
      const success = await authStore.updateProfile(formData)
      if (success) {
        modal.success('프로필 사진이 로컬에 저장되었습니다.', '성공')
      }
    } else {
      // Supabase 모드
      const { signedUrl, path } = data

      // 2. Supabase 스토리지에 직접 업로드
      const uploadRes = await fetch(signedUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type
        }
      })

      if (!uploadRes.ok) throw new Error('Supabase Upload Failed')

      // 3. 백엔드에 "경로 문자열"만 저장 Request
      const formData = new FormData()
      formData.append('profile_image', path) 

      const success = await authStore.updateProfile(formData)
      if (success) {
        modal.success('프로필 사진이 클라우드에 업데이트되었습니다.', '성공')
      }
    }
  } catch (error) {
    console.error(error)
    modal.alert('이미지 업로드에 실패했습니다.', '오류')
  } finally {
    isUpdating.value = false
  }
}

/**
 * 프로필 사진 삭제 로직
 */
const deleteProfileImage = async () => {
    const ok = await modal.confirm('프로필 사진을 삭제하시겠습니까? \n기본 이미지로 변경됩니다.', '사진 삭제', 'danger')
    if (!ok) return
    
    try {
        const formData = new FormData()
        formData.append('profile_image', '') 
        const success = await authStore.updateProfile(formData)
        if (success) {
            modal.alert('프로필 사진이 삭제되었습니다.', '삭제 완료')
            await authStore.fetchCurrentUser()
        }
    } catch (error) {
        modal.alert('사진 삭제 실패', '오류')
    }
}

/**
 * 이름/소개글 등 텍스트 정보 저장
 */
const saveProfileChanges = async () => {
  if (!profileForm.value.username) {
    modal.alert('아이디를 입력해주세요.', '알림')
    return
  }

  isUpdating.value = true
  try {
    // 텍스트 데이터 전송용 FormData 생성
    const formData = new FormData()
    formData.append('username', profileForm.value.username)
    formData.append('bio', profileForm.value.bio || '')

    const success = await authStore.updateProfile(formData)
    if (success) {
      modal.success('프로필 정보가 저장되었습니다!', '성공')
      await authStore.fetchCurrentUser() 
    }
  } catch (error) {
    const errorMsg = error.response?.data?.username?.[0] || '저장에 실패했습니다.'
    modal.alert(errorMsg, '오류')
  } finally {
    isUpdating.value = false
  }
}

// 비밀번호 변경 폼 상태
const passwordForm = ref({
  old: '',
  new: '',
  confirm: ''
})

/**
 * 비밀번호 변경
 */
const handleChangePassword = async () => {
  if (!passwordForm.value.old || !passwordForm.value.new) {
    modal.alert('현재 비밀번호와 새 비밀번호를 모두 입력해주세요.', '알림')
    return
  }
  
  if (passwordForm.value.new.length < 8) {
    modal.alert('새 비밀번호는 8자 이상이어야 합니다.', '알림')
    return
  }

  if (passwordForm.value.new !== passwordForm.value.confirm) {
    modal.alert('새 비밀번호가 일치하지 않습니다.', '오류')
    return
  }

  isUpdating.value = true
  try {
    const success = await authStore.changePassword({
      old_password: passwordForm.value.old,
      new_password: passwordForm.value.new
    })
    
    if (success) {
      modal.success('비밀번호가 성공적으로 변경되었습니다. \n다시 로그인해주세요.', '성공')
      authStore.logout() // 보안상 로그아웃 처리
      router.push('/auth')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.old_password?.[0] || '비밀번호 변경에 실패했습니다.'
    modal.alert(errorMsg, '오류')
  } finally {
    isUpdating.value = false
    // 폼 초기화
    passwordForm.value = { old: '', new: '', confirm: '' }
  }
}

/**
 * 회원 탈퇴
 */
const handleWithdraw = async () => {
  const confirm1 = await modal.confirm('정말로 탈퇴하시겠습니까? \n이 작업은 되돌릴 수 없습니다.', '회원 탈퇴', 'danger')
  if (confirm1) {
    const confirm2 = await modal.confirm('마지막 확인입니다. \n모든 데이터가 삭제됩니다.', '최종 경고', 'danger')
    if (confirm2) {
      isUpdating.value = true
      try {
        const success = await authStore.withdraw()
        if (success) {
          modal.success('탈퇴가 완료되었습니다. \n이용해주셔서 감사합니다.', '탈퇴 완료')
          router.push('/auth')
        }
      } catch (error) {
        modal.alert('회원 탈퇴 처리 중 오류가 발생했습니다.', '오류')
      } finally {
        isUpdating.value = false
      }
    }
  }
}

/**
 * 로그아웃
 */
const handleLogout = async () => {
  const ok = await modal.confirm('로그아웃 하시겠습니까?', '로그아웃')
  if(ok) {
    await authStore.logout()
    router.push('/auth')
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#FDFBF7] pb-24 font-sans relative overflow-hidden">
    
    <!-- Noise Overlay -->
    <div class="fixed inset-0 w-full h-full pointer-events-none z-[1] opacity-[0.15] mix-blend-overlay">
      <svg class="w-full h-full noise-svg">
        <filter id="noiseFilter">
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noiseFilter)" />
      </svg>
    </div>
    <!-- Sticky Header Replaced by NavBar -->
    <NavBar>
      <template #right>
        <div v-if="isUpdating" class="flex items-center gap-2 text-primary-600 text-sm font-medium">
          <Loader2 class="w-4 h-4 animate-spin" /> 저장 중...
        </div>
      </template>
    </NavBar>

    <div class="max-w-5xl mx-auto p-4 pt-32 md:p-8 md:pt-32 grid md:grid-cols-4 gap-6">
      
      <div class="md:col-span-1 space-y-2">
        <button 
          v-for="item in [
            {id: 'account', icon: Lock, label: '계정 설정'},
            {id: 'notifications', icon: Bell, label: '알림'},
            {id: 'privacy', icon: Shield, label: '보안 및 개인정보'}
          ]" 
          :key="item.id"
          @click="activeTab = item.id"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl transition-all font-bold text-sm"
          :class="activeTab === item.id ? 'bg-primary-600 text-white shadow-lg' : 'bg-white text-gray-600 hover:bg-primary-50'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          {{ item.label }}
        </button>
      </div>

      <div class="md:col-span-3 space-y-6">
        
        <div v-if="activeTab === 'account'" class="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 animate-fade-in">
          <h2 class="text-lg font-bold text-gray-800 mb-6">Profile Information</h2>
          
          <div class="flex flex-col items-center mb-8">
            <div class="relative group cursor-pointer" @click="triggerFileUpload">
              <img 
              :src="profileImageUrl"
                class="w-28 h-28 rounded-full object-cover border-4 border-gray-100 group-hover:border-primary-200 transition-all shadow-md" 
              />
              <div class="absolute inset-0 bg-black/30 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <Camera class="w-8 h-8 text-white" />
              </div>
              <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" class="hidden" />
            </div>
            <p class="text-xs text-gray-400 mt-3">사진을 클릭하여 변경하세요</p>
            <div class="flex flex-col gap-2 mt-4">
              <button type="button" @click="triggerFileUpload" class="px-4 py-2 bg-gray-100 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-200 transition-colors">
                Change Photo
              </button>
              <button type="button" @click="deleteProfileImage" class="px-4 py-2 bg-rose-50 rounded-lg text-sm font-bold text-rose-500 hover:bg-rose-100 transition-colors">
                Delete Photo
              </button>
              <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" class="hidden" />
              <p class="text-xs text-gray-400">JPG, GIF or PNG. 1MB max.</p>
            </div>
          </div>

          <div class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Username</label>
              <div class="relative">
                <span class="absolute left-4 top-3.5 text-gray-400 font-bold">@</span>
                <input 
                  v-model="profileForm.username" 
                  @input="handleUsernameInput"
                  type="text" 
                  maxlength="8"
                  class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-100 focus:outline-none transition-all" 
                />
              </div>
              <p class="text-[10px] text-gray-400 mt-1 ml-1">* 영문, 숫자만 8자 이내로 가능합니다.</p>
            </div>

            <div class="opacity-70">
              <label class="block text-sm font-bold text-gray-400 mb-1">Email (변경 불가)</label>
              <input 
                :value="currentUser.email" 
                disabled 
                type="text" 
                class="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-xl cursor-not-allowed text-gray-500" 
              />
              <p class="text-sm font-bold text-blue-500 mt-2 ml-1">
                {{ 
                  currentUser.provider === 'google' ? 'google로 가입한 계정이에요' : 
                  currentUser.provider === 'naver' ? 'naver로 가입한 계정이에요' : 
                  currentUser.provider === 'kakao' ? 'kakao로 가입한 계정이에요' : 
                  '이메일로 가입한 계정이에요' 
                }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Bio</label>
              <textarea 
                v-model="profileForm.bio" 
                placeholder="나를 한 줄로 표현해보세요."
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none resize-none h-28 text-sm"
              ></textarea>
            </div>

            <button 
              @click="saveProfileChanges"
              :disabled="isUpdating"
              class="w-full bg-primary-500 text-white py-4 rounded-xl font-bold mt-4 shadow-lg shadow-primary-100 hover:scale-[1.01] active:scale-95 transition-all disabled:opacity-50"
            >
              Save Changes
            </button>
          </div>
        </div>

        <div v-if="activeTab === 'notifications'" class="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
          <h2 class="text-lg font-bold text-gray-800 mb-6">Notification Preferences</h2>
          <div class="space-y-1">
            <div v-for="(val, key) in notificationSettings" :key="key" class="flex items-center justify-between py-4 border-b border-gray-50 last:border-0">
              <div>
                <p class="font-bold text-gray-700 capitalize">{{ key.replace(/([A-Z])/g, " $1") }}</p>
                <p class="text-xs text-gray-400">{{ key }} 관련 알림을 받습니다.</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="notificationSettings[key]" @change="updateNotification(key, notificationSettings[key])" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
              </label>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'privacy'" class="space-y-6">
          <!-- Password Change Section -->
          <div class="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 animate-fade-in">
            <h2 class="text-lg font-bold text-gray-800 mb-6">Change Password</h2>
            
            <!-- 소셜 로그인 유저 안내 메시지 -->
            <div v-if="isSocialUser" class="mb-6 p-4 bg-gray-50 rounded-xl border border-gray-200 text-sm text-gray-500 flex items-center gap-2">
              <Shield class="w-4 h-4" />
              <span>소셜 로그인({{ currentUser.provider }}) 계정은 비밀번호를 변경할 수 없습니다.</span>
            </div>

            <div class="space-y-4" :class="{ 'opacity-50 pointer-events-none': isSocialUser }">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Current Password</label>
                <input 
                  v-model="passwordForm.old" 
                  type="password"
                  :disabled="isSocialUser" 
                  class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">New Password</label>
                <input 
                  v-model="passwordForm.new" 
                  type="password" 
                  placeholder="8자 이상 입력해주세요"
                  :disabled="isSocialUser"
                  class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Confirm New Password</label>
                <input 
                  v-model="passwordForm.confirm" 
                  type="password"
                  :disabled="isSocialUser" 
                  class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-all"
                />
              </div>
              <button 
                @click="handleChangePassword"
                :disabled="isUpdating || isSocialUser"
                class="w-full bg-gray-800 text-white py-3 rounded-xl font-bold hover:bg-gray-900 transition-all disabled:opacity-50"
              >
                Update Password
              </button>
            </div>
          </div>

          <!-- Account Actions Section -->
          <div class="bg-white rounded-3xl p-6 shadow-sm border border-rose-100">
            <h2 class="text-lg font-bold text-rose-600 mb-4">Danger Zone</h2>
            <div class="space-y-3">
              <button 
                @click="handleWithdraw"
                class="w-full flex items-center justify-between p-4 bg-rose-50 rounded-xl hover:bg-rose-100 transition-colors text-rose-500 group"
              >
                <div class="flex flex-col items-start">
                  <span class="font-bold group-hover:underline">Delete Account</span>
                  <span class="text-xs opacity-70">모든 데이터가 영구적으로 삭제됩니다.</span>
                </div>
                <ChevronRight class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-8 border-t border-gray-200 text-center">
           <button @click="handleLogout" class="inline-flex items-center gap-2 text-rose-500 font-bold px-8 py-3 rounded-full hover:bg-rose-50 transition-colors">
             <LogOut class="w-5 h-5" /> Log Out
           </button>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* Noise SVG Style */
.noise-svg {
    filter: contrast(170%) brightness(100%);
}
</style>