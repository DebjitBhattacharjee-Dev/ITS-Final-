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
    case 'success': return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    case 'warning': return 'bg-amber-50 text-amber-700 border-amber-200'
    case 'danger': return 'bg-red-50 text-red-700 border-red-200'
    case 'info': return 'bg-blue-50 text-blue-700 border-blue-200'
    default: return 'bg-slate-100 text-slate-700 border-slate-200'
  }
})
</script>
