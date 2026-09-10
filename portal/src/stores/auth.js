import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, logoutApi, getLoggedUserApi } from '../services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const initialized = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value && user.value !== 'Guest')
  const userFullName = computed(() => user.value?.full_name || user.value?.user || 'User')
  const userRoles = computed(() => user.value?.roles || [])

  async function checkSession() {
    loading.value = true
    try {
      if (window.frappe?.boot?.user?.name && window.frappe.boot.user.name !== 'Guest') {
        user.value = {
          user: window.frappe.boot.user.name,
          email: window.frappe.boot.user.email,
          full_name: window.frappe.boot.user.full_name,
          roles: window.frappe.boot.user.roles || []
        }
      } else {
        const data = await getLoggedUserApi()
        user.value = data
      }
    } catch (err) {
      user.value = null
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function login(usr, pwd) {
    loading.value = true
    error.value = null
    try {
      await loginApi(usr, pwd)
      await checkSession()
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Invalid username or password'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await logoutApi()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      loading.value = false
      window.location.href = '/portal-access'
    }
  }

  return {
    user,
    loading,
    initialized,
    error,
    isAuthenticated,
    userFullName,
    userRoles,
    checkSession,
    login,
    logout
  }
})
