<template>
  <Badge :variant="badgeVariant">
    {{ status || 'Draft' }}
  </Badge>
</template>

<script setup>
import { computed } from 'vue'
import Badge from '../ui/Badge.vue'

const props = defineProps({
  status: { type: String, default: 'Open' }
})

const badgeVariant = computed(() => {
  const s = (props.status || '').toLowerCase()
  if (['completed', 'approved', 'submitted', 'paid', 'active', 'closed'].includes(s)) return 'success'
  if (['pending', 'in progress', 'under review', 'open'].includes(s)) return 'info'
  if (['warning', 'overdue', 'partially paid'].includes(s)) return 'warning'
  if (['cancelled', 'rejected', 'failed', 'expired', 'high risk'].includes(s)) return 'danger'
  return 'default'
})
</script>
