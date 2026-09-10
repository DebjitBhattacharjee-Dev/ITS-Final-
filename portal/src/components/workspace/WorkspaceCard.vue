<template>
  <div class="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 shadow-sm hover:border-slate-700/60 transition-all flex flex-col">
    <div class="pb-2.5 mb-2 border-b border-slate-800/80 flex items-center justify-between">
      <h3 class="text-xs font-semibold text-slate-200 uppercase tracking-wider">{{ section.title }}</h3>
      <span class="text-[10px] font-mono text-slate-500 bg-slate-800/80 px-1.5 py-0.5 rounded">
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
