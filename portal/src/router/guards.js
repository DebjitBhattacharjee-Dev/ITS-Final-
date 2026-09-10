import { useAuthStore } from '../stores/auth'

export async function setupGuards(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    if (!authStore.initialized) {
      await authStore.checkSession()
    }

    if (to.path === '/portal-access') {
      if (authStore.isAuthenticated) {
        return next('/portal/dashboard')
      }
      return next()
    }

    if (to.path.startsWith('/portal')) {
      if (!authStore.isAuthenticated) {
        return next('/portal-access')
      }
      return next()
    }

    next()
  })
}
