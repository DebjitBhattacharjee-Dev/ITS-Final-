<template>
  <div>
    <!-- Mobile/Tablet & Overlay Backdrop when Sidebar is Open -->
    <div 
      v-if="!navStore.sidebarCollapsed"
      @click="navStore.closeSidebar"
      class="fixed inset-0 bg-slate-950/60 backdrop-blur-xs z-20 transition-opacity"
    ></div>

    <!-- Workspaces Drawer / Sidebar -->
    <aside 
      :class="[
        'fixed top-12 bottom-0 left-0 bg-slate-900 border-r border-slate-800/80 flex flex-col transition-all duration-300 z-30 select-none shadow-2xl w-64',
        navStore.sidebarCollapsed ? '-translate-x-full opacity-0 pointer-events-none' : 'translate-x-0 opacity-100 pointer-events-auto'
      ]"
    >
      <div class="p-3.5 border-b border-slate-800/60 flex items-center justify-between">
        <span class="text-xs font-bold tracking-wider text-slate-300 uppercase">
          WORKSPACES
        </span>
        <button 
          @click="navStore.closeSidebar"
          class="p-1 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto py-2 px-2 space-y-1">
        <router-link
          v-for="ws in visibleWorkspaces"
          :key="ws.id"
          :to="ws.route"
          @click="handleWorkspaceClick(ws.id)"
          :class="[
            'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all group',
            isWorkspaceActive(ws.id)
              ? 'bg-blue-950/70 text-blue-400 border border-blue-600/40 shadow-sm font-semibold'
              : 'text-slate-300 hover:bg-slate-800/80 hover:text-slate-100'
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
          
          <span class="truncate tracking-tight flex-1">
            {{ ws.label }}
          </span>
        </router-link>
      </nav>
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { X } from 'lucide-vue-next'
import { useNavigationStore } from '../../stores/navigation'
import { usePermissionsStore } from '../../stores/permissions'

const route = useRoute()
const navStore = useNavigationStore()
const permStore = usePermissionsStore()

const visibleWorkspaces = computed(() => {
  return navStore.workspaces.filter(ws => permStore.hasRole(ws.required_roles))
})

const isWorkspaceActive = (wsId) => {
  const ws = navStore.workspaces.find(w => w.id === wsId)
  return ws && route.path.startsWith(ws.route)
}

const handleWorkspaceClick = (wsId) => {
  navStore.setWorkspace(wsId)
  navStore.closeSidebar()
}
</script>
