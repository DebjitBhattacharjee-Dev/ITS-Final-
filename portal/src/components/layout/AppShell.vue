<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans">
    <TopBar />
    <div class="flex-1 flex overflow-hidden">
      <Sidebar />
      <main class="flex-1 md:ml-64 overflow-y-auto p-6 bg-slate-50">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import TopBar from './TopBar.vue'
import Sidebar from './Sidebar.vue'
</script>
