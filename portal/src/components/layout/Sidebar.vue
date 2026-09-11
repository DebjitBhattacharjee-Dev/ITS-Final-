<template>
  <div>
    <!-- Mobile/Tablet & Overlay Backdrop when Sidebar is Open -->
    <div 
      v-if="!navStore.sidebarCollapsed"
      @click="navStore.closeSidebar"
      class="fixed inset-0 bg-white/30 backdrop-blur-xs z-20 transition-opacity"
    ></div>

    <!-- Workspaces Drawer / Sidebar -->
    <aside 
      :class="[
        'fixed top-12 bottom-0 left-0 bg-white border-r border-slate-200 flex flex-col transition-all duration-300 z-30 select-none shadow-xl w-64',
        navStore.sidebarCollapsed ? '-translate-x-full opacity-0 pointer-events-none' : 'translate-x-0 opacity-100 pointer-events-auto'
      ]"
    >
      <div class="p-3.5 border-b border-slate-200 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-sm font-bold tracking-wider text-slate-600 uppercase">
            WORKSPACES
          </span>
          <router-link 
            to="/portal/dashboard"
            @click="navStore.closeSidebar"
            class="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': route.path === '/portal/dashboard' }"
            title="Workflow Dashboard"
          >
            <Home class="w-4 h-4" />
          </router-link>
        </div>
        <button 
          @click="navStore.closeSidebar"
          class="p-1 hover:bg-slate-100 text-slate-600 hover:text-slate-700 rounded transition-colors"
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
            'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group',
            isWorkspaceActive(ws.id)
              ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-xs font-semibold'
              : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
          ]"
        >
          <span 
            :class="[
              'text-[11px] font-mono w-5 text-right font-medium shrink-0',
              isWorkspaceActive(ws.id) ? 'text-blue-600 font-bold' : 'text-slate-600 group-hover:text-slate-600'
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
import { X, Home } from 'lucide-vue-next'
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
