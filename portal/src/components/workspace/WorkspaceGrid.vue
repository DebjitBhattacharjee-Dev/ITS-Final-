<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <WorkspaceCard
      v-for="section in visibleSections"
      :key="section.title"
      :section="section"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import WorkspaceCard from './WorkspaceCard.vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  sections: { type: Array, required: true }
})

const authStore = useAuthStore()

const visibleSections = computed(() => {
  const isAdministrator = authStore.user?.user === 'Administrator'
  return props.sections.filter(s => {
    if (s.admin_only && !isAdministrator) return false
    return true
  })
})
</script>
