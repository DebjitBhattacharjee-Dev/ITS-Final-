<template>
  <div class="px-6 py-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Workflow Dashboard</h1>
      <p class="text-slate-500 mt-1">Track pending and action-required documents across the ITS business process.</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-3">
      <AlertCircle class="w-5 h-5 mt-0.5 shrink-0 text-red-500" />
      <div>
        <h3 class="font-semibold text-red-800">Failed to load dashboard</h3>
        <p class="text-sm mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="bg-white border border-slate-200 rounded-lg p-5 animate-pulse">
        <div class="h-4 bg-slate-200 rounded w-12 mb-3"></div>
        <div class="h-5 bg-slate-200 rounded w-3/4 mb-4"></div>
        <div class="h-8 bg-slate-200 rounded w-16 mb-2"></div>
        <div class="h-3 bg-slate-200 rounded w-1/2"></div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="space-y-10">
      
      <!-- COMMERCIAL -->
      <section v-if="filterKeys(['G0_Lead', 'G1_Opportunity', 'G2_Supplier_Quotation', 'G3_Quotation', 'G3.5_Project_Contract']).length > 0">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Commercial</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <WorkflowCard 
            v-for="key in filterKeys(['G0_Lead', 'G1_Opportunity', 'G2_Supplier_Quotation', 'G3_Quotation', 'G3.5_Project_Contract'])" 
            :key="key" 
            :data="metrics[key]" 
            :fallbackGate="key.split('_')[0]"
            :fallbackLabel="key.split('_')[1].replace('-', ' ')"
          />
        </div>
      </section>

      <!-- ORDER & FINANCE -->
      <section v-if="filterKeys(['G5.5_Sales_Order', 'G7_Purchase_Order']).length > 0">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Order & Finance</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <WorkflowCard 
            v-for="key in filterKeys(['G5.5_Sales_Order', 'G7_Purchase_Order'])" 
            :key="key" 
            :data="metrics[key]"
            :fallbackGate="key.split('_')[0]"
            :fallbackLabel="key.split('_')[1].replace('-', ' ')"
          />
        </div>
      </section>

      <!-- QUALITY & DELIVERY -->
      <section v-if="filterKeys(['G8_Factory_Acceptance_Test', 'G8_Integrated_Factory_Acceptance_Test', 'G8.5_Snag_List', 'G9.5_Delivery_Note']).length > 0">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Quality & Delivery</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <WorkflowCard 
            v-for="key in filterKeys(['G8_Factory_Acceptance_Test', 'G8_Integrated_Factory_Acceptance_Test', 'G8.5_Snag_List', 'G9.5_Delivery_Note'])" 
            :key="key" 
            :data="metrics[key]" 
            :fallbackGate="key.split('_')[0]"
            :fallbackLabel="key.split('_')[1].replace('_', ' ')"
          />
        </div>
      </section>

      <!-- COMMISSIONING & BILLING -->
      <section v-if="filterKeys(['G9.7_Project_Handover', 'G10.5_Sales_Invoice', 'G11_Project_Warranty']).length > 0">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Commissioning & Billing</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <WorkflowCard 
            v-for="key in filterKeys(['G9.7_Project_Handover', 'G10.5_Sales_Invoice', 'G11_Project_Warranty'])" 
            :key="key" 
            :data="metrics[key]" 
            :fallbackGate="key.split('_')[0]"
            :fallbackLabel="key.split('_')[1].replace('_', ' ')"
          />
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { AlertCircle } from "lucide-vue-next"
import WorkflowCard from "../components/dashboard/WorkflowCard.vue"
import { callApi } from "../services/api"
import { usePermissionsStore } from "../stores/permissions"

const metrics = ref({})
const loading = ref(true)
const error = ref(null)
const permStore = usePermissionsStore()

const filterKeys = (keys) => {
  return keys.filter(k => metrics.value[k] && permStore.canRead(metrics.value[k].doctype))
}

const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await callApi("its_ui_redesign.api.dashboard.get_workflow_summary", {})
    metrics.value = data || {}
  } catch (err) {
    console.error("Dashboard metrics error:", err)
    error.value = err.message || "Failed to load workflow metrics"
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
