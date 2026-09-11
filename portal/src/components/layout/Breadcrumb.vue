<template>
  <nav v-if="!isGlobalDashboard" class="flex items-center space-x-1.5 text-sm text-slate-600 mb-3 select-none">
    <router-link to="/portal" class="hover:text-slate-900 transition-colors flex items-center gap-1 font-medium">
      <span>Workspaces</span>
    </router-link>
    <span class="text-slate-700">/</span>
    <span class="text-slate-900 font-medium">{{ activeWorkspaceLabel }}</span>
    <template v-if="subPage">
      <span class="text-slate-700">/</span>
      <span class="text-slate-600">{{ subPage }}</span>
    </template>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useNavigationStore } from '../../stores/navigation'

const props = defineProps({
  subPage: { type: String, default: '' }
})

const route = useRoute()
const navStore = useNavigationStore()

const isGlobalDashboard = computed(() => {
  const p = route.path.replace(/\/+$/, '')
  return p === '/portal' || p === '/portal/dashboard'
})

const activeWorkspaceLabel = computed(() => navStore.activeWorkspace?.label || 'Workspace')
</script>
