<template>
  <div class="bg-slate-900 border border-slate-800/80 rounded-lg shadow-sm overflow-hidden">
    <!-- Header Controls -->
    <div class="p-3 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 bg-slate-900/60">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
        <input 
          v-model="searchQuery"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-600 transition-colors"
        />
      </div>

      <div class="flex items-center space-x-2">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Table Content -->
    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" @retry="$emit('reload')" />
    <EmptyState v-else-if="filteredRows.length === 0" />

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-950/80 border-b border-slate-800/80 text-slate-400 font-semibold uppercase text-[10px] tracking-wider select-none">
          <tr>
            <th 
              v-for="col in columns" 
              :key="col.key"
              class="py-2.5 px-3"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/50">
          <tr 
            v-for="(row, idx) in paginatedRows" 
            :key="row.name || idx"
            class="hover:bg-slate-800/40 transition-colors group"
          >
            <td 
              v-for="col in columns" 
              :key="col.key"
              class="py-2 px-3 text-slate-300 font-normal truncate max-w-xs"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                <StatusBadge v-if="col.key === 'status'" :status="row[col.key]" />
                <span v-else>{{ row[col.key] }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="filteredRows.length > 0" class="p-2.5 border-t border-slate-800/80 bg-slate-950/50 flex items-center justify-between text-xs text-slate-400">
      <span>Showing {{ paginationStart }} to {{ paginationEnd }} of {{ filteredRows.length }} records</span>
      <div class="flex items-center space-x-1">
        <button 
          @click="page--" 
          :disabled="page === 1"
          class="px-2 py-1 bg-slate-800/60 hover:bg-slate-800 text-slate-300 disabled:opacity-40 disabled:hover:bg-slate-800/60 rounded border border-slate-700/50 transition-colors"
        >
          Previous
        </button>
        <span class="px-2 font-mono text-slate-300">{{ page }} / {{ totalPages }}</span>
        <button 
          @click="page++" 
          :disabled="page >= totalPages"
          class="px-2 py-1 bg-slate-800/60 hover:bg-slate-800 text-slate-300 disabled:opacity-40 disabled:hover:bg-slate-800/60 rounded border border-slate-700/50 transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'
import LoadingState from '../ui/LoadingState.vue'
import EmptyState from '../ui/EmptyState.vue'
import ErrorState from '../ui/ErrorState.vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  searchPlaceholder: { type: String, default: 'Search records...' },
  pageSize: { type: Number, default: 10 }
})

defineEmits(['reload'])

const searchQuery = ref('')
const page = ref(1)

const filteredRows = computed(() => {
  if (!searchQuery.value) return props.rows
  const q = searchQuery.value.toLowerCase()
  return props.rows.filter(r => 
    Object.values(r).some(val => String(val).toLowerCase().includes(q))
  )
})

const totalPages = computed(() => Math.ceil(filteredRows.value.length / props.pageSize) || 1)
const paginationStart = computed(() => ((page.value - 1) * props.pageSize) + 1)
const paginationEnd = computed(() => Math.min(page.value * props.pageSize, filteredRows.value.length))

const paginatedRows = computed(() => {
  const start = (page.value - 1) * props.pageSize
  return filteredRows.value.slice(start, start + props.pageSize)
})
</script>
