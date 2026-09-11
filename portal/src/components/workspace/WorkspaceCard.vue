<template>
  <div class="bg-white/90 border border-slate-200 rounded-lg p-4 shadow-sm hover:border-slate-200/60 transition-all flex flex-col">
    <div class="pb-2.5 mb-2 border-b border-slate-200 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-slate-800 uppercase tracking-wider">{{ section.title }}</h3>
      <span class="text-[10px] font-mono text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
        {{ section.items.length }} items
      </span>
    </div>
    
    <div class="space-y-0.5 flex-1">
      <WorkspaceMenuItem
        v-for="item in section.items"
        :key="item.label"
        :item="item"
      />
    </div>
  </div>
</template>

<script setup>
import WorkspaceMenuItem from './WorkspaceMenuItem.vue'

defineProps({
  section: { type: Object, required: true }
})
</script>
