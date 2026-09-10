import { usePermissionsStore } from '../stores/permissions'
export function usePermissions() {
  return usePermissionsStore()
}
