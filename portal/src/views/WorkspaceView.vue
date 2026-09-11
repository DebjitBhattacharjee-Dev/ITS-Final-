<template>
  <div class="space-y-6">
    <PageHeader 
      :title="workspace.label" 
      :description="workspace.description"
    />

    <!-- Navigation Menu Cards Grid ONLY (No top dashboard widgets) -->
    <WorkspaceGrid :sections="workspace.sections" />
  </div>
</template>

<script setup>
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '../components/layout/PageHeader.vue'
import WorkspaceGrid from '../components/workspace/WorkspaceGrid.vue'
import { useNavigationStore } from '../stores/navigation'

const route = useRoute()
const navStore = useNavigationStore()

const workspace = computed(() => {
  const path = route.path
  const matched = navStore.workspaces.find(w => path.startsWith(w.route))
  return matched || navStore.activeWorkspace
})

watchEffect(() => {
  if (workspace.value) {
    navStore.setWorkspace(workspace.value.id)
  }
})
</script>
