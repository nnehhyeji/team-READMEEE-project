<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const goHome = () => {
  if (route.path === '/feed') {
    router.push('/')
  } else {
    router.push('/feed')
  }
}
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-white/60 backdrop-blur-md border-b border-gray-200/50 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <h1 
        @click="goHome" 
        class="text-xl font-black tracking-tight text-gray-900 cursor-pointer hover:opacity-70 transition-opacity font-sans"
      >
        READMEEE
      </h1>
      <slot name="right"></slot>
    </div>
  </nav>
</template>


