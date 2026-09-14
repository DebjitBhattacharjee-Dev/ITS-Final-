<template>
  <div>
    <!-- Mobile/Tablet Overlay Backdrop -->
    <div 
      v-if="!navStore.sidebarCollapsed"
      @click="navStore.closeSidebar"
      class="fixed inset-0 bg-slate-900/20 backdrop-blur-xs z-20 transition-opacity md:hidden"
    ></div>

    <!-- Workspaces Drawer / Sidebar -->
    <aside 
      :class="[
        'fixed top-12 bottom-0 left-0 bg-white border-r border-slate-200 flex flex-col transition-all duration-300 z-30 select-none shadow-sm w-64',
        navStore.sidebarCollapsed ? '-translate-x-full md:translate-x-0 opacity-0 md:opacity-100 pointer-events-none md:pointer-events-auto' : 'translate-x-0 opacity-100 pointer-events-auto'
      ]"
    >
      <div class="p-3.5 border-b border-slate-200 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <img src="/images/its_logo.png" alt="ITS" class="h-5 w-auto object-contain" />
          <span class="text-xs font-bold tracking-wider text-slate-700 uppercase">
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
          class="p-1 hover:bg-blue-50 text-slate-400 hover:text-blue-600 rounded transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto py-3 px-2 space-y-1.5">
        <router-link
          v-for="ws in visibleWorkspaces"
          :key="ws.id"
          :to="ws.route"
          @click="handleWorkspaceClick(ws.id)"
          :class="[
            'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-[17px] font-semibold transition-all group border',
            isWorkspaceActive(ws.id)
              ? 'bg-blue-50 text-blue-700 border-blue-200 shadow-xs'
              : 'text-slate-700 border-transparent hover:bg-blue-50 hover:text-blue-700 hover:border-blue-100'
          ]"
        >
          <span 
            :class="[
              'w-2 h-2 rounded-full shrink-0 transition-colors',
              isWorkspaceActive(ws.id) ? 'bg-blue-600' : 'bg-slate-400 group-hover:bg-blue-600'
            ]"
          ></span>
          
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
  return navStore.workspaces.filter(ws => permStore.isWorkspacePermitted(ws))
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
