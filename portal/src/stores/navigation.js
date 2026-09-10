import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { workspaces } from '../config/navigation'

export const useNavigationStore = defineStore('navigation', () => {
  const activeWorkspaceId = ref('project-management')
  const sidebarCollapsed = ref(false)

  const activeWorkspace = computed(() => {
    return workspaces.find(w => w.id === activeWorkspaceId.value) || workspaces[0]
  })

  function setWorkspace(id) {
    activeWorkspaceId.value = id
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    workspaces,
    activeWorkspaceId,
    activeWorkspace,
    sidebarCollapsed,
    setWorkspace,
    toggleSidebar
  }
})
