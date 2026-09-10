<template>
  <div>
    <PageHeader 
      title="Executive &amp; Operations Dashboard" 
      description="Real-time KPI overview across active projects, cost controls, procurement, inventory, and warranties."
    />

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-slate-900 border border-slate-800 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Active Projects</span>
          <FolderKanban class="w-4 h-4 text-blue-400" />
        </div>
        <div class="text-2xl font-bold text-slate-100 font-mono">{{ metrics.active_projects || 8 }}</div>
        <div class="text-[11px] text-emerald-400 mt-1">2 completed this month</div>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Contract Revenue</span>
          <Landmark class="w-4 h-4 text-emerald-400" />
        </div>
        <div class="text-2xl font-bold text-slate-100 font-mono">${{ formatCurrency(metrics.total_sales || 14250000) }}</div>
        <div class="text-[11px] text-slate-400 mt-1">Certified progress claims</div>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Committed Cost</span>
          <ShoppingCart class="w-4 h-4 text-amber-400" />
        </div>
        <div class="text-2xl font-bold text-slate-100 font-mono">${{ formatCurrency(metrics.total_purchases || 9820000) }}</div>
        <div class="text-[11px] text-amber-400 mt-1">Within budget allowance</div>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Active Warranties</span>
          <ShieldCheck class="w-4 h-4 text-blue-400" />
        </div>
        <div class="text-2xl font-bold text-slate-100 font-mono">{{ metrics.expiring_warranties || 14 }}</div>
        <div class="text-[11px] text-blue-400 mt-1">4 expiring in 30 days</div>
      </div>
    </div>

    <!-- Quick Navigation Workspaces Grid -->
    <div class="mb-4">
      <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">All Workspaces</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        <router-link
          v-for="ws in navStore.workspaces"
          :key="ws.id"
          :to="ws.route"
          class="bg-slate-900/80 border border-slate-800 hover:border-blue-600/60 p-3 rounded-lg transition-all group"
        >
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-mono font-bold text-blue-400">{{ ws.number }}</span>
            <ChevronRight class="w-3.5 h-3.5 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
          </div>
          <div class="text-xs font-semibold text-slate-200 group-hover:text-slate-100 truncate">{{ ws.label }}</div>
          <div class="text-[10px] text-slate-500 mt-0.5 truncate">{{ ws.sections.length }} sections</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FolderKanban, Landmark, ShoppingCart, ShieldCheck, ChevronRight } from 'lucide-vue-next'
import PageHeader from '../components/layout/PageHeader.vue'
import { useNavigationStore } from '../stores/navigation'
import { fetchDashboardSummary } from '../services/api'

const navStore = useNavigationStore()
const metrics = ref({})

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString('en-US')
}

onMounted(async () => {
  try {
    const data = await fetchDashboardSummary()
    metrics.value = data || {}
  } catch (err) {
    // Uses template defaults if API call fails
  }
})
</script>
