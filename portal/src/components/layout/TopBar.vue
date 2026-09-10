<template>
  <header class="h-12 bg-slate-900 border-b border-slate-800/80 px-4 flex items-center justify-between text-xs text-slate-300 select-none z-30">
    <div class="flex items-center space-x-3">
      <button 
        @click="navStore.toggleSidebar" 
        class="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
        title="Toggle Sidebar"
      >
        <Menu class="w-4 h-4" />
      </button>
      <div class="flex items-center space-x-2 font-medium tracking-tight">
        <span class="text-slate-400">ERPNext</span>
        <span class="text-slate-600">/</span>
        <span class="text-slate-100 font-semibold">Construction &amp; Projects</span>
      </div>
    </div>

    <div class="flex items-center space-x-4">
      <span class="hidden md:inline-block text-slate-400 font-normal">Proposed workspace navigation</span>
      <div class="h-4 w-px bg-slate-800 hidden md:block"></div>
      
      <div class="relative flex items-center space-x-2">
        <div class="w-6 h-6 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-400 font-semibold text-[10px]">
          {{ userInitials }}
        </div>
        <span class="hidden sm:inline font-medium text-slate-200">{{ authStore.userFullName }}</span>
        <button 
          @click="handleLogout"
          class="p-1 hover:bg-red-950/40 text-slate-400 hover:text-red-400 rounded transition-colors ml-2"
          title="Sign out"
        >
          <LogOut class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { Menu, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'
import { useNavigationStore } from '../../stores/navigation'

const authStore = useAuthStore()
const navStore = useNavigationStore()

const userInitials = computed(() => {
  const name = authStore.userFullName || 'U'
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
})

const handleLogout = () => {
  authStore.logout()
}
</script>
