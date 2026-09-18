<template>
  <header class="h-12 bg-white border-b border-slate-200 px-4 flex items-center justify-between text-sm text-slate-700 select-none z-30 shadow-2xs">
    <div class="flex items-center space-x-3 shrink-0">
      <div class="flex items-center space-x-2.5 font-medium tracking-tight">
        <img src="/images/its_logo.png" alt="ITS" class="h-6 w-auto object-contain" />
        <span class="text-slate-900 font-bold hidden sm:inline">ITS Project Operations</span>
      </div>
    </div>

    <!-- ERPNext Awesomebar Search -->
    <Awesomebar />

    <div class="flex items-center space-x-4 shrink-0">
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
import { LogOut } from 'lucide-vue-next'
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
