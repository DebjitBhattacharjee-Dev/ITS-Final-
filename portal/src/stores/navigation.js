import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { workspaces } from '../config/navigation'

export const useNavigationStore = defineStore('navigation', () => {
  const activeWorkspaceId = ref('project-management')
  // Workspaces sidebar is CLOSED by default on initial login/page load
  const sidebarCollapsed = ref(true)

  const activeWorkspace = computed(() => {
    return workspaces.find(w => w.id === activeWorkspaceId.value) || workspaces[0]
  })

  function setWorkspace(id) {
    activeWorkspaceId.value = id
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function closeSidebar() {
    sidebarCollapsed.value = true
  }

  function openSidebar() {
    sidebarCollapsed.value = false
  }

  return {
    workspaces,
    activeWorkspaceId,
    activeWorkspace,
    sidebarCollapsed,
    setWorkspace,
    toggleSidebar,
    closeSidebar,
    openSidebar
  }
})
