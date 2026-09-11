<template>
  <div class="py-12 border border-dashed border-slate-200 rounded-lg text-center p-6 bg-white/30">
    <FolderOpen class="w-8 h-8 text-slate-600 mx-auto mb-2" />
    <h4 class="text-sm font-semibold text-slate-700">{{ title }}</h4>
    <p class="text-sm text-slate-600 mt-1 max-w-sm mx-auto">{{ description }}</p>
  </div>
</template>

<script setup>
import { FolderOpen } from 'lucide-vue-next'

defineProps({
  title: { type: String, default: 'No records found' },
  description: { type: String, default: 'There are no records matching your current filter criteria.' }
})
</script>
