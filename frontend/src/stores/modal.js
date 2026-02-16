import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
    const isOpen = ref(false)
    const type = ref('alert')
    const title = ref('')
    const message = ref('')

    let resolvePromise = null

    const open = (msg, ttl = '', mode = 'alert') => {
        message.value = msg
        title.value = ttl
        type.value = mode
        isOpen.value = true

        return new Promise((resolve) => {
            resolvePromise = resolve
        })
    }

    const alert = (msg, ttl = '', subType = 'alert') => {
        return open(msg, ttl, subType)
    }

    const success = (msg, ttl = '') => {
        return open(msg, ttl, 'success')
    }

    const confirm = (msg, ttl = '', subType = 'confirm') => {
        return open(msg, ttl, subType)
    }

    const close = (result = false) => {
        isOpen.value = false
        if (resolvePromise) {
            resolvePromise(result)
            resolvePromise = null
        }
    }

    return {
        isOpen,
        type,
        title,
        message,
        alert,
        success,
        confirm,
        close
    }
})
