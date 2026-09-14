import { useAuthStore } from '../stores/auth'
import { usePermissionsStore } from '../stores/permissions'
import { WORKSPACES } from '../config/navigation'

export async function setupGuards(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    const permStore = usePermissionsStore()

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

      if (!permStore.initialized) {
        await permStore.fetchPermissions()
      }

      if (to.path === '/portal' || to.path === '/portal/') {
        const firstWs = WORKSPACES.find(ws => permStore.isWorkspacePermitted(ws))
        if (firstWs) {
          return next(firstWs.route)
        }
        return next('/portal/dashboard')
      }

      return next()
    }

    next()
  })
}
