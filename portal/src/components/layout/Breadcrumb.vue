<template>
  <nav class="flex items-center space-x-1.5 text-xs text-slate-400 mb-2">
    <router-link to="/portal" class="hover:text-slate-200 transition-colors">Workspaces</router-link>
    <span class="text-slate-600">/</span>
    <span class="text-slate-200 font-medium">{{ activeWorkspaceLabel }}</span>
    <template v-if="subPage">
      <span class="text-slate-600">/</span>
      <span class="text-slate-400">{{ subPage }}</span>
    </template>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useNavigationStore } from '../../stores/navigation'

const props = defineProps({
  subPage: { type: String, default: '' }
})

const navStore = useNavigationStore()
const activeWorkspaceLabel = computed(() => navStore.activeWorkspace?.label || 'Workspace')
</script>
