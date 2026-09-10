<template>
  <aside 
    :class="[
      'bg-slate-900 border-r border-slate-800/80 flex flex-col transition-all duration-200 z-20 select-none',
      navStore.sidebarCollapsed ? 'w-14' : 'w-64'
    ]"
  >
    <div class="p-3 border-b border-slate-800/60 flex items-center justify-between">
      <span 
        v-if="!navStore.sidebarCollapsed" 
        class="text-[10px] font-bold tracking-wider text-slate-400 uppercase"
      >
        Workspaces
      </span>
      <span v-else class="text-[10px] font-bold text-slate-500 uppercase mx-auto">WS</span>
    </div>

    <nav class="flex-1 overflow-y-auto py-2 px-1.5 space-y-1">
      <router-link
        v-for="ws in visibleWorkspaces"
        :key="ws.id"
        :to="ws.route"
        @click="navStore.setWorkspace(ws.id)"
        :class="[
          'flex items-center space-x-2.5 px-2.5 py-2 rounded text-xs font-medium transition-all group',
          isWorkspaceActive(ws.id)
            ? 'bg-blue-950/60 text-blue-400 border border-blue-600/30 shadow-sm font-semibold'
            : 'text-slate-300 hover:bg-slate-800/60 hover:text-slate-100'
        ]"
      >
        <span 
          :class="[
            'text-[11px] font-mono w-5 text-right font-medium shrink-0',
            isWorkspaceActive(ws.id) ? 'text-blue-400 font-bold' : 'text-slate-500 group-hover:text-slate-400'
          ]"
        >
          {{ ws.number }}
        </span>
        
        <span 
          v-if="!navStore.sidebarCollapsed" 
          class="truncate tracking-tight flex-1"
        >
          {{ ws.label }}
        </span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useNavigationStore } from '../../stores/navigation'
import { usePermissionsStore } from '../../stores/permissions'

const route = useRoute()
const navStore = useNavigationStore()
const permStore = usePermissionsStore()

const visibleWorkspaces = computed(() => {
  return navStore.workspaces.filter(ws => permStore.hasRole(ws.required_roles))
})

const isWorkspaceActive = (wsId) => {
  if (navStore.activeWorkspaceId === wsId) return true
  const ws = navStore.workspaces.find(w => w.id === wsId)
  return ws && route.path.startsWith(ws.route)
}
</script>
