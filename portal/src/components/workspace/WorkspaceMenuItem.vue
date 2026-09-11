<template>
  <router-link
    :to="item.route"
    class="group flex items-center justify-between py-2 px-3 rounded text-sm text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-transparent hover:border-slate-200/40 transition-all cursor-pointer"
  >
    <span class="font-medium truncate tracking-tight group-hover:font-medium">{{ item.label }}</span>
    <ChevronRight class="w-3.5 h-3.5 text-slate-600 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all shrink-0 ml-2" />
  </router-link>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'

defineProps({
  item: { type: Object, required: true }
})
</script>
