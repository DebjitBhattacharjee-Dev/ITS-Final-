import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { getUserPermissions } from '../services/api'
import { WORKSPACES } from '../config/navigation'

export const usePermissionsStore = defineStore('permissions', () => {
  const authStore = useAuthStore()
  const docPermissions = ref({})
  const initialized = ref(false)
  const loading = ref(false)

  function hasRole(requiredRoles) {
    if (!requiredRoles || requiredRoles.length === 0) return true
    if (authStore.userRoles.includes('System Manager') || authStore.userRoles.includes('Administrator')) {
      return true
    }
    return requiredRoles.some(role => authStore.userRoles.includes(role))
  }

  async function fetchPermissions() {
    if (loading.value) return
    loading.value = true
    try {
      const res = await getUserPermissions()
      if (res && res.data) {
        docPermissions.value = res.data
      }
    } catch (err) {
      console.error('Failed to fetch user permissions:', err)
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  function normalizeKey(dt) {
    if (!dt || typeof dt !== 'string') return dt
    if (['sales-order', 'sales-orders', 'salesorder', 'salesorders'].includes(dt.toLowerCase())) return 'Sales Order'
    return dt
  }

  function getDocPerm(docType) {
    if (!docType) return { read: true, create: true, write: true, delete: true, submit: true, cancel: true, amend: true }
    const key = normalizeKey(docType)
    if (docPermissions.value[key]) return docPermissions.value[key]
    if (docPermissions.value[docType]) return docPermissions.value[docType]
    const lower = String(docType).toLowerCase()
    if (docPermissions.value[lower]) return docPermissions.value[lower]
    return { read: true, create: true, write: true, delete: true, submit: false, cancel: false, amend: false }
  }

  function canRead(docType) {
    if (!docType) return true
    const key = normalizeKey(docType)
    if (docPermissions.value[key] !== undefined) {
      return !!docPermissions.value[key].read
    }
    if (docPermissions.value[docType] !== undefined) {
      return !!docPermissions.value[docType].read
    }
    const lower = String(docType).toLowerCase()
    if (docPermissions.value[lower] !== undefined) {
      return !!docPermissions.value[lower].read
    }
    return true
  }

  function canCreate(docType) {
    if (!docType) return true
    const key = normalizeKey(docType)
    if (docPermissions.value[key] !== undefined) return !!docPermissions.value[key].create
    if (docPermissions.value[docType] !== undefined) return !!docPermissions.value[docType].create
    const lower = String(docType).toLowerCase()
    if (docPermissions.value[lower] !== undefined) return !!docPermissions.value[lower].create
    return true
  }

  function canWrite(docType) {
    if (!docType) return true
    const key = normalizeKey(docType)
    if (docPermissions.value[key] !== undefined) return !!docPermissions.value[key].write
    if (docPermissions.value[docType] !== undefined) return !!docPermissions.value[docType].write
    const lower = String(docType).toLowerCase()
    if (docPermissions.value[lower] !== undefined) return !!docPermissions.value[lower].write
    return true
  }

  function canDelete(docType) {
    if (!docType) return true
    const key = normalizeKey(docType)
    if (docPermissions.value[key] !== undefined) return !!docPermissions.value[key].delete
    if (docPermissions.value[docType] !== undefined) return !!docPermissions.value[docType].delete
    const lower = String(docType).toLowerCase()
    if (docPermissions.value[lower] !== undefined) return !!docPermissions.value[lower].delete
    return true
  }

  function canSubmit(docType) {
    if (!docType) return false
    if (docPermissions.value[docType] !== undefined) {
      return !!docPermissions.value[docType].submit
    }
    return false
  }

  function canCancel(docType) {
    if (!docType) return false
    if (docPermissions.value[docType] !== undefined) {
      return !!docPermissions.value[docType].cancel
    }
    return false
  }

  function canAmend(docType) {
    if (!docType) return false
    if (docPermissions.value[docType] !== undefined) {
      return !!docPermissions.value[docType].amend
    }
    return false
  }

  function isItemPermitted(item) {
    if (!item) return false
    if (item.admin_only && authStore.user?.user !== 'Administrator') return false
    if (item.docType && !canRead(item.docType)) return false
    if (item.required_roles && !hasRole(item.required_roles)) return false
    return true
  }

  function isSectionPermitted(section) {
    if (!section) return false
    if (section.admin_only && authStore.user?.user !== 'Administrator') return false
    if (section.items && section.items.length > 0) {
      return section.items.some(item => isItemPermitted(item))
    }
    return true
  }

  function isWorkspacePermitted(workspace) {
    if (!workspace) return false
    if (workspace.sections && workspace.sections.length > 0) {
      return workspace.sections.some(sec => isSectionPermitted(sec))
    }
    if (workspace.required_roles) {
      return hasRole(workspace.required_roles)
    }
    return true
  }

  function canAccessRoute(path) {
    if (!path || !path.startsWith('/portal')) return true
    if (['/portal', '/portal/', '/portal/dashboard', '/portal/403', '/portal/404', '/portal/session-expired'].includes(path)) return true

    for (const ws of WORKSPACES) {
      for (const sec of ws.sections || []) {
        for (const item of sec.items || []) {
          if (item.route && (path === item.route || path.startsWith(item.route + '/'))) {
            return isItemPermitted(item)
          }
        }
      }
    }
    return true
  }

  return {
    docPermissions,
    initialized,
    loading,
    hasRole,
    fetchPermissions,
    getDocPerm,
    canRead,
    canCreate,
    canWrite,
    canDelete,
    canSubmit,
    canCancel,
    canAmend,
    isItemPermitted,
    isSectionPermitted,
    isWorkspacePermitted,
    canAccessRoute
  }
})
