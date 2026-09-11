<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <router-view />
    <SystemNotification />
  </div>
</template>

<script setup>
import SystemNotification from './components/ui/SystemNotification.vue'
</script>

