import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export const usePermissionsStore = defineStore('permissions', () => {
  const authStore = useAuthStore()

  function hasRole(requiredRoles) {
    if (!requiredRoles || requiredRoles.length === 0) return true
    if (authStore.userRoles.includes('System Manager') || authStore.userRoles.includes('Administrator')) {
      return true
    }
    return requiredRoles.some(role => authStore.userRoles.includes(role))
  }

  return {
    hasRole
  }
})
