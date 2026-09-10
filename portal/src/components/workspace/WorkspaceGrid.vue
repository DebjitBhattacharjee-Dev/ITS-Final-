<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <WorkspaceCard
      v-for="section in sections"
      :key="section.title"
      :section="section"
    />
  </div>
</template>

<script setup>
import WorkspaceCard from './WorkspaceCard.vue'

defineProps({
  sections: { type: Array, required: true }
})
</script>
