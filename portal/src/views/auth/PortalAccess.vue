<template>
  <div class="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-blue-600 selection:text-white">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- App Identity Header -->
      <div class="flex items-center justify-center space-x-2 text-blue-500 mb-3">
        <Building2 class="w-8 h-8" />
      </div>
      <h2 class="text-center text-xl font-bold tracking-tight text-slate-100 uppercase">
        ITS Project Operations
      </h2>
      <p class="mt-1 text-center text-xs text-slate-400">
        Enterprise Construction &amp; Project Management Portal
      </p>
    </div>

    <div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4">
      <div class="bg-slate-900 border border-slate-800 py-8 px-6 shadow-xl rounded-xl sm:px-10">
        
        <!-- Error Alert -->
        <div v-if="authStore.error" class="mb-4 p-3 bg-red-950/60 border border-red-800/80 rounded text-xs text-red-300 flex items-start space-x-2">
          <AlertCircle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <span>{{ authStore.error }}</span>
        </div>

        <form class="space-y-4" @submit.prevent="handleLogin">
          <div>
            <label for="username" class="block text-xs font-medium text-slate-300 mb-1">
              Username or Email
            </label>
            <div class="relative">
              <User class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="username"
                v-model="usr"
                type="text"
                required
                autocomplete="username"
                placeholder="administrator"
                class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-600 transition-colors"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-xs font-medium text-slate-300 mb-1">
              Password
            </label>
            <div class="relative">
              <Lock class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="password"
                v-model="pwd"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="••••••••"
                class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-10 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-600 transition-colors"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
              >
                <Eye v-if="!showPassword" class="w-3.5 h-3.5" />
                <EyeOff v-else class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="pt-2">
            <button
              type="submit"
              :disabled="authStore.loading"
              class="w-full flex justify-center py-2 px-4 border border-blue-600/50 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
            >
              <Loader2 v-if="authStore.loading" class="w-4 h-4 animate-spin mr-2" />
              <span>{{ authStore.loading ? 'Signing in...' : 'Sign In to Portal' }}</span>
            </button>
          </div>
        </form>

        <div class="mt-6 border-t border-slate-800/80 pt-4 text-center">
          <span class="text-[11px] text-slate-500">
            Protected Enterprise System — Secured by Frappe Session Gate
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Building2, User, Lock, Eye, EyeOff, AlertCircle, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const usr = ref('')
const pwd = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  try {
    await authStore.login(usr.value, pwd.value)
    router.push('/portal')
  } catch (err) {
    // Error state handled in store
  }
}
</script>
