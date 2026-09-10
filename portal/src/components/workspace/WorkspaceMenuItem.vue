<template>
  <router-link
    :to="item.route"
    class="group flex items-center justify-between py-2 px-3 rounded text-xs text-slate-300 hover:text-slate-100 hover:bg-slate-800/60 border border-transparent hover:border-slate-700/40 transition-all cursor-pointer"
  >
    <span class="font-normal truncate tracking-tight group-hover:font-medium">{{ item.label }}</span>
    <ChevronRight class="w-3.5 h-3.5 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all shrink-0 ml-2" />
  </router-link>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'

defineProps({
  item: { type: Object, required: true }
})
</script>
