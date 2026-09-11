<template>
  <header class="h-12 bg-white border-b border-slate-200 px-4 flex items-center justify-between text-sm text-slate-700 select-none z-30 shadow-2xs">
    <div class="flex items-center space-x-3 shrink-0">
      <button 
        @click="navStore.toggleSidebar" 
        class="p-1 hover:bg-slate-100 rounded text-slate-600 hover:text-slate-800 transition-colors"
        title="Toggle Sidebar"
      >
        <Menu class="w-4 h-4" />
      </button>
      <div class="flex items-center space-x-2 font-medium tracking-tight">
        <span class="text-slate-600">ERPNext</span>
        <span class="text-slate-700">/</span>
        <span class="text-slate-900 font-semibold">Construction &amp; Projects</span>
      </div>
    </div>

    <!-- ERPNext Awesomebar Search -->
    <Awesomebar />

    <div class="flex items-center space-x-4 shrink-0">
      <span class="hidden md:inline-block text-slate-600 font-medium">ITS Project Operations</span>
      <div class="h-4 w-px bg-slate-200 hidden md:block"></div>
      
      <div class="relative flex items-center space-x-2">
        <div class="w-6 h-6 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-700 font-semibold text-xs">
          {{ userInitials }}
        </div>
        <span class="hidden sm:inline font-medium text-slate-800">{{ authStore.userFullName }}</span>
        <button 
          @click="handleLogout"
          class="p-1 hover:bg-red-50 text-slate-600 hover:text-red-600 rounded transition-colors ml-2"
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
import Awesomebar from './Awesomebar.vue'

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
