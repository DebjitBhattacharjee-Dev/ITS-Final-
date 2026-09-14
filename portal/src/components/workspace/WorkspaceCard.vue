<template>
  <div v-if="visibleItems.length > 0" class="bg-white/90 border border-slate-200 rounded-lg p-4 shadow-sm hover:border-slate-200/60 transition-all flex flex-col">
    <div class="pb-2.5 mb-2 border-b border-slate-200 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-slate-800 uppercase tracking-wider">{{ section.title }}</h3>
      <span class="text-[10px] font-mono text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
        {{ visibleItems.length }} items
      </span>
    </div>
    
    <div class="space-y-0.5 flex-1">
      <WorkspaceMenuItem
        v-for="item in visibleItems"
        :key="item.label"
        :item="item"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import WorkspaceMenuItem from './WorkspaceMenuItem.vue'
import { usePermissionsStore } from '../../stores/permissions'

const props = defineProps({
  section: { type: Object, required: true }
})

const permStore = usePermissionsStore()

const visibleItems = computed(() => {
  if (!props.section?.items) return []
  return props.section.items.filter(item => permStore.isItemPermitted(item))
})
</script>
