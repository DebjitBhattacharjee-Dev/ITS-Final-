<template>
  <div class="py-12 flex flex-col items-center justify-center text-slate-400">
    <div class="w-7 h-7 border-2 border-slate-700 border-t-blue-500 rounded-full animate-spin mb-3"></div>
    <span class="text-xs font-medium text-slate-400">{{ message }}</span>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Loading data...' }
})
</script>
