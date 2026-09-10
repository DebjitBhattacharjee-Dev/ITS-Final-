<template>
  <div class="py-12 border border-dashed border-slate-800/80 rounded-lg text-center p-6 bg-slate-900/30">
    <FolderOpen class="w-8 h-8 text-slate-600 mx-auto mb-2" />
    <h4 class="text-xs font-semibold text-slate-300">{{ title }}</h4>
    <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">{{ description }}</p>
  </div>
</template>

<script setup>
import { FolderOpen } from 'lucide-vue-next'

defineProps({
  title: { type: String, default: 'No records found' },
  description: { type: String, default: 'There are no records matching your current filter criteria.' }
})
</script>
