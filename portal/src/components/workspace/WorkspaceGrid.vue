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
import { usePermissionsStore } from '../../stores/permissions'

const props = defineProps({
  sections: { type: Array, required: true }
})

const permStore = usePermissionsStore()

const visibleSections = computed(() => {
  if (!props.sections) return []
  return props.sections.filter(s => permStore.isSectionPermitted(s))
})
</script>
