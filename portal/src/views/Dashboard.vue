<template>
  <div>
    <PageHeader 
      title="Executive & Operations Dashboard" 
      description="Real-time KPI overview across active projects, cost controls, procurement, inventory, and warranties."
    />

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-600 mb-2">
          <span class="text-sm font-semibold uppercase tracking-wider">Active Projects</span>
          <FolderKanban class="w-4 h-4 text-blue-600" />
        </div>
        <div class="text-2xl font-bold text-slate-900 font-mono">{{ metrics.active_projects ?? 0 }}</div>
        <div class="text-[11px] text-slate-600 mt-1">{{ metrics.completed_projects ?? 0 }} completed</div>
      </div>

      <div class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-600 mb-2">
          <span class="text-sm font-semibold uppercase tracking-wider">Sales Revenue</span>
          <Landmark class="w-4 h-4 text-emerald-400" />
        </div>
        <div class="text-2xl font-bold text-slate-900 font-mono">AED {{ formatCurrency(metrics.total_sales) }}</div>
        <div class="text-[11px] text-slate-600 mt-1">Submitted Sales Invoices</div>
      </div>

      <div class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-600 mb-2">
          <span class="text-sm font-semibold uppercase tracking-wider">Purchase Commitments</span>
          <ShoppingCart class="w-4 h-4 text-amber-400" />
        </div>
        <div class="text-2xl font-bold text-slate-900 font-mono">AED {{ formatCurrency(metrics.total_purchases) }}</div>
        <div class="text-[11px] text-slate-600 mt-1">Submitted Purchase Orders</div>
      </div>

      <div class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-600 mb-2">
          <span class="text-sm font-semibold uppercase tracking-wider">Active Warranties</span>
          <ShieldCheck class="w-4 h-4 text-blue-600" />
        </div>
        <div class="text-2xl font-bold text-slate-900 font-mono">{{ metrics.expiring_warranties ?? 0 }}</div>
        <div class="text-[11px] text-slate-600 mt-1">{{ metrics.open_ncrs ?? 0 }} Open Quality NCRs</div>
      </div>
    </div>

    <!-- Quick Navigation Workspaces Grid -->
    <div class="mb-4">
      <h3 class="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-3">All Workspaces</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        <router-link
          v-for="ws in navStore.workspaces"
          :key="ws.id"
          :to="ws.route"
          class="bg-white border border-slate-200 hover:border-blue-600/60 p-3 rounded-lg transition-all group"
        >
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-sm font-mono font-bold text-blue-600">{{ ws.number }}</span>
            <ChevronRight class="w-3.5 h-3.5 text-slate-600 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
          </div>
          <div class="text-sm font-semibold text-slate-800 group-hover:text-slate-900 truncate">{{ ws.label }}</div>
          <div class="text-[10px] text-slate-600 mt-0.5 truncate">{{ ws.sections.length }} sections</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { FolderKanban, Landmark, ShoppingCart, ShieldCheck, ChevronRight } from "lucide-vue-next"
import PageHeader from "../components/layout/PageHeader.vue"
import { useNavigationStore } from "../stores/navigation"
import { fetchDashboardSummary } from "../services/api"

const navStore = useNavigationStore()
const metrics = ref({})

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(async () => {
  try {
    const data = await fetchDashboardSummary()
    metrics.value = data || {}
  } catch (err) {
    console.error("Dashboard metrics error:", err)
  }
})
</script>
