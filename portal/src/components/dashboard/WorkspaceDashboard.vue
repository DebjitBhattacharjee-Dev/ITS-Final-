<template>
  <div class="space-y-6">
    <!-- Header & Filter Bar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 p-4 rounded-xl backdrop-blur-sm">
      <div>
        <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <LayoutDashboard class="w-5 h-5 text-blue-600" />
          {{ workspaceTitle }}
        </h2>
        <p class="text-sm text-slate-600 mt-0.5">Real-time ERPNext live operational metrics & business analytics</p>
      </div>

      <div class="flex items-center gap-3">
        <button 
          @click="loadDashboard" 
          :disabled="loading"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-medium rounded-lg border border-slate-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-28 bg-white border border-slate-200 rounded-xl animate-pulse"></div>
    </div>

    <template v-else>
      <!-- KPI Number Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div 
          v-for="(kpi, idx) in dashboard.kpis" 
          :key="idx"
          @click="handleKpiClick(kpi)"
          class="bg-white border border-slate-200 hover:border-blue-600/50 cursor-pointer rounded-xl p-4 transition-all shadow-sm flex flex-col justify-between group"
        >
          <div class="flex items-center justify-between text-slate-600 mb-2">
            <span class="text-sm font-semibold uppercase tracking-wider text-slate-600 group-hover:text-slate-800 transition-colors">{{ kpi.label }}</span>
            <component :is="getKpiIcon(kpi.color)" class="w-4 h-4" :class="getKpiIconClass(kpi.color)" />
          </div>
          <div>
            <div class="text-2xl font-bold text-slate-900 font-mono tracking-tight group-hover:text-blue-600 transition-colors">
              {{ formatVal(kpi.value, kpi.type) }}
            </div>
            <div class="text-[11px] text-slate-600 mt-1 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full" :class="getKpiDotClass(kpi.color)"></span>
              Live Frappe database metric
            </div>
          </div>
        </div>
      </div>

      <!-- Charts & Distribution Breakdown -->
      <div v-if="dashboard.charts && dashboard.charts.length" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div 
          v-for="(chart, cIdx) in dashboard.charts" 
          :key="cIdx"
          class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between"
        >
          <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-4 flex items-center gap-2">
            <BarChart2 class="w-4 h-4 text-blue-600" />
            {{ chart.title }}
          </h3>

          <div v-if="chart.data && chart.data.length" class="space-y-3">
            <div v-for="(item, iIdx) in chart.data" :key="iIdx" class="space-y-1">
              <div class="flex items-center justify-between text-sm font-medium">
                <span class="text-slate-700 truncate">{{ item[chart.label_key] || 'Unspecified' }}</span>
                <span class="font-mono text-slate-800">{{ item[chart.val_key] }}</span>
              </div>
              <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div 
                  class="h-full bg-blue-500 rounded-full transition-all duration-500"
                  :style="{ width: getPercentage(item[chart.val_key], chart.data, chart.val_key) + '%' }"
                ></div>
              </div>
            </div>
          </div>
          <div v-else class="py-8 text-center text-sm text-slate-600">
            No records found for distribution breakdown
          </div>
        </div>
      </div>

      <!-- Recent Records Quick Table -->
      <div v-if="dashboard.recent_list && dashboard.recent_list.length" class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-2">
            <FileText class="w-4 h-4 text-emerald-400" />
            Recent Operational {{ dashboard.doctype }} Records
          </h3>
          <span class="text-[11px] text-slate-600 font-mono">{{ dashboard.recent_list.length }} items</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="text-slate-600 border-b border-slate-200 uppercase text-[10px] tracking-wider font-semibold">
                <th class="py-2.5 px-3">Record ID</th>
                <th class="py-2.5 px-3">Title / Details</th>
                <th class="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200/60 text-slate-700 font-mono">
              <tr 
                v-for="rec in dashboard.recent_list" 
                :key="rec.name"
                class="hover:bg-slate-50 transition-colors"
              >
                <td class="py-2.5 px-3 font-bold text-blue-600">
                  {{ rec.name }}
                </td>
                <td class="py-2.5 px-3 text-slate-800">
                  {{ rec.project_name || rec.subject || rec.title || rec.customer || rec.supplier || rec.employee_name || rec.production_item || 'Record Item' }}
                </td>
                <td class="py-2.5 px-3">
                  <span 
                    class="px-2 py-0.5 text-[10px] font-semibold rounded-full border"
                    :class="getStatusBadgeClass(rec.status)"
                  >
                    {{ rec.status || 'Active' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  LayoutDashboard, RefreshCw, FolderKanban, Landmark, ShoppingCart, 
  ShieldCheck, BarChart2, FileText 
} from 'lucide-vue-next'
import { fetchWorkspaceDashboard } from '../../services/api'
import { openDocument } from '../../config/navigation'

const props = defineProps({
  workspaceId: {
    type: String,
    required: true
  },
  workspaceTitle: {
    type: String,
    default: 'Section Dashboard'
  }
})

const router = useRouter()
const loading = ref(true)
const dashboard = ref({ kpis: [], charts: [], recent_list: [] })

const loadDashboard = async () => {
  loading.value = true
  try {
    const res = await fetchWorkspaceDashboard(props.workspaceId)
    dashboard.value = res || { kpis: [], charts: [], recent_list: [] }
  } catch (err) {
    console.error('Failed to load section dashboard:', err)
  } finally {
    loading.value = false
  }
}

const handleKpiClick = (kpi) => {
  if (dashboard.value.doctype) {
    // Determine route slug
    const dt = dashboard.value.doctype.toLowerCase().replace(/\s+/g, '-')
    router.push(`/portal/${props.workspaceId}/${dt}`)
  }
}

watch(() => props.workspaceId, () => {
  loadDashboard()
})

onMounted(() => {
  loadDashboard()
})

const formatVal = (val, type) => {
  if (type === 'currency') {
    return 'AED ' + Number(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  return Number(val || 0).toLocaleString('en-US')
}

const getPercentage = (val, dataList, valKey) => {
  const total = dataList.reduce((acc, curr) => acc + Number(curr[valKey] || 0), 0)
  if (!total) return 0
  return Math.round((Number(val || 0) / total) * 100)
}

const getKpiIcon = (color) => {
  if (color === 'emerald') return Landmark
  if (color === 'amber') return ShoppingCart
  if (color === 'purple' || color === 'indigo') return ShieldCheck
  return FolderKanban
}

const getKpiIconClass = (color) => {
  if (color === 'emerald') return 'text-emerald-400'
  if (color === 'amber') return 'text-amber-400'
  if (color === 'rose') return 'text-rose-400'
  if (color === 'purple') return 'text-purple-400'
  if (color === 'indigo') return 'text-indigo-400'
  return 'text-blue-600'
}

const getKpiDotClass = (color) => {
  if (color === 'emerald') return 'bg-emerald-500'
  if (color === 'amber') return 'bg-amber-500'
  if (color === 'rose') return 'bg-rose-500'
  if (color === 'purple') return 'bg-purple-500'
  if (color === 'indigo') return 'bg-indigo-500'
  return 'bg-blue-500'
}

const getStatusBadgeClass = (status) => {
  const s = (status || '').toLowerCase()
  if (s.includes('completed') || s.includes('paid') || s.includes('approved')) {
    return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
  }
  if (s.includes('open') || s.includes('working') || s.includes('in progress')) {
    return 'bg-blue-500/10 text-blue-600 border-blue-500/30'
  }
  if (s.includes('draft') || s.includes('pending')) {
    return 'bg-amber-500/10 text-amber-400 border-amber-500/30'
  }
  if (s.includes('overdue') || s.includes('cancelled') || s.includes('rejected')) {
    return 'bg-rose-500/10 text-rose-400 border-rose-500/30'
  }
  return 'bg-slate-100 text-slate-700 border-slate-200'
}
</script>
