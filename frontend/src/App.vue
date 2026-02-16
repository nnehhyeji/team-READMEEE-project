<script setup>
import { RouterView } from 'vue-router'
import RightNav from '@/components/RightNav.vue'
import AlertModal from '@/components/AlertModal.vue' 
</script>

<template>
  <RightNav />
  <AlertModal /> 
  <RouterView />
</template>