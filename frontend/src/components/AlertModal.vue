<script setup>
import { useModalStore } from '@/stores/modal'
import { storeToRefs } from 'pinia'
import { AlertCircle, HelpCircle, CheckCircle } from 'lucide-vue-next'

const modalStore = useModalStore()
const { isOpen, type, title, message } = storeToRefs(modalStore)

const handleConfirm = () => {
  modalStore.close(true)
}

const handleCancel = () => {
  modalStore.close(false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4 animate-fade-in" @click.self="handleCancel">
      <div class="bg-white rounded-3xl w-full max-w-sm p-6 shadow-2xl flex flex-col items-center text-center animate-scale-up" role="dialog" aria-modal="true">
        
        <!-- Icon -->
        <div class="w-14 h-14 rounded-full flex items-center justify-center mb-5" 
             :class="{
               'bg-rose-100': type === 'alert' || type === 'danger',
               'bg-primary-100': type === 'confirm' || type === 'info' || type === 'success'
             }">
          <AlertCircle v-if="type === 'alert' || type === 'danger'" class="w-7 h-7 text-rose-500" />
          <CheckCircle v-else-if="type === 'success'" class="w-7 h-7 text-primary-500" />
          <HelpCircle v-else class="w-7 h-7 text-primary-500" />
        </div>

        <!-- Content -->
        <h2 v-if="title" class="text-xl font-bold text-gray-800 mb-2">{{ title }}</h2>
        <p class="text-gray-600 mb-8 whitespace-pre-wrap leading-relaxed">{{ message }}</p>

        <!-- Buttons -->
        <div class="flex gap-3 w-full">
          <button 
            v-if="type === 'confirm' || type === 'danger'"
            @click="handleCancel"
            class="flex-1 bg-gray-100 text-gray-600 font-bold py-3.5 rounded-xl hover:bg-gray-200 transition-colors"
          >
            취소
          </button>
          
          <button 
            @click="handleConfirm"
            class="flex-1 font-bold py-3.5 rounded-xl shadow-md transition-all active:scale-95 flex items-center justify-center"
            :class="{
              'bg-gray-900 text-white hover:bg-gray-800': type === 'alert',
              'bg-rose-500 text-white hover:bg-rose-600': type === 'danger',
              'bg-primary-500 text-white hover:scale-[1.01] active:scale-95 shadow-lg shadow-primary-100': type === 'confirm' || type === 'info' || type === 'success'
            }"
          >
            확인
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-out;
}

.animate-scale-up {
  animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { 
    opacity: 0;
    transform: scale(0.95);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}
</style>
