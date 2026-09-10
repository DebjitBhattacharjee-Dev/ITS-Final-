<template>
  <div class="mb-6">
    <Breadcrumb :subPage="subPage" />
    <h1 class="text-xl font-bold text-slate-100 tracking-tight">{{ title }}</h1>
    <p v-if="description" class="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">{{ description }}</p>
  </div>
</template>

<script setup>
import Breadcrumb from './Breadcrumb.vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  subPage: { type: String, default: '' }
})
</script>
