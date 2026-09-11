<template>
  <div class="py-8 bg-red-950/20 border border-red-900/40 rounded-lg text-center p-6 my-4">
    <AlertCircle class="w-7 h-7 text-red-400 mx-auto mb-2" />
    <h4 class="text-sm font-semibold text-red-200">{{ title }}</h4>
    <p class="text-sm text-red-300/80 mt-1">{{ message }}</p>
    <button 
      v-if="retryable"
      @click="$emit('retry')"
      class="mt-3 px-3 py-1.5 bg-red-900/40 hover:bg-red-900/60 text-red-200 border border-red-700/50 rounded text-sm transition-colors"
    >
      Retry
    </button>
  </div>
</template>

<script setup>
import { AlertCircle } from 'lucide-vue-next'

defineProps({
  title: { type: String, default: 'Error loading data' },
  message: { type: String, default: 'An unexpected error occurred while communicating with the server.' },
  retryable: { type: Boolean, default: true }
})

defineEmits(['retry'])
</script>
