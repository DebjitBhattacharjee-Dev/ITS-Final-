<template>
  <span 
    :class="[
      'inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium tracking-tight border',
      variantClasses
    ]"
  >
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'default' }
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'success': return 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'
    case 'warning': return 'bg-amber-950/60 text-amber-400 border-amber-800/60'
    case 'danger': return 'bg-red-950/60 text-red-400 border-red-800/60'
    case 'info': return 'bg-blue-950/60 text-blue-400 border-blue-800/60'
    default: return 'bg-slate-800/80 text-slate-300 border-slate-700/60'
  }
})
</script>
