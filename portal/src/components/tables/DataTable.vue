<template>
  <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
    <!-- Header Controls -->
    <div class="p-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-white">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="w-3.5 h-3.5 text-slate-600 absolute left-2.5 top-1/2 -translate-y-1/2" />
        <input 
          v-model="searchQuery"
          @input="$emit('search', searchQuery)"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full bg-white border border-slate-200 rounded pl-8 pr-3 py-1.5 text-sm text-slate-800 placeholder-slate-500 focus:outline-none focus:border-blue-600 transition-colors"
        />
      </div>

      <div class="flex items-center space-x-2">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Table Content -->
    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" @retry="$emit('reload')" />
    <EmptyState v-else-if="displayRows.length === 0" />

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-100 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider select-none">
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
        <tbody class="divide-y divide-slate-200/50">
          <tr 
            v-for="(row, idx) in displayRows" 
            :key="row.name || idx"
            @click="$emit('row-click', row)"
            class="hover:bg-blue-50/60 cursor-pointer transition-colors group"
          >
            <td 
              v-for="col in columns" 
              :key="col.key"
              class="py-2.5 px-3 text-slate-700 font-medium truncate max-w-xs"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                <StatusBadge v-if="col.key === 'status'" :status="row[col.key]" />
                <span v-else-if="['name', 'title', 'id', 'customer_name', 'supplier_name', 'project_name'].includes(col.key)" class="font-mono text-blue-600 font-medium group-hover:underline">{{ row[col.key] }}</span>
                <span v-else>{{ row[col.key] }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalRecords > 0" class="p-2.5 border-t border-slate-200 bg-white/20 flex items-center justify-between text-sm text-slate-600">
      <span>Showing {{ paginationStart }} to {{ paginationEnd }} of {{ totalRecords }} records</span>
      <div class="flex items-center space-x-1">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage <= 1"
          class="px-2.5 py-1 bg-white hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-slate-700 disabled:opacity-40 disabled:hover:bg-white disabled:hover:text-slate-700 rounded border border-slate-200 transition-colors"
        >
          Previous
        </button>
        <span class="px-2 font-mono text-slate-700">{{ currentPage }} / {{ maxPage }}</span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage >= maxPage"
          class="px-2.5 py-1 bg-white hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-slate-700 disabled:opacity-40 disabled:hover:bg-white disabled:hover:text-slate-700 rounded border border-slate-200 transition-colors"
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
  pageSize: { type: Number, default: 10 },
  totalCount: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  serverSide: { type: Boolean, default: false }
})

const emit = defineEmits(['reload', 'row-click', 'search', 'page-change'])

const searchQuery = ref('')

const displayRows = computed(() => {
  if (props.serverSide) return props.rows
  if (!searchQuery.value) {
    const start = (props.page - 1) * props.pageSize
    return props.rows.slice(start, start + props.pageSize)
  }
  const q = searchQuery.value.toLowerCase()
  return props.rows.filter(r => Object.values(r).some(val => String(val).toLowerCase().includes(q)))
})

const totalRecords = computed(() => props.serverSide ? props.totalCount : (searchQuery.value ? displayRows.value.length : props.rows.length))
const currentPage = computed(() => props.page)
const maxPage = computed(() => Math.ceil(totalRecords.value / props.pageSize) || 1)

const paginationStart = computed(() => totalRecords.value === 0 ? 0 : ((currentPage.value - 1) * props.pageSize) + 1)
const paginationEnd = computed(() => Math.min(currentPage.value * props.pageSize, totalRecords.value))

const changePage = (newPage) => {
  if (newPage < 1 || newPage > maxPage.value) return
  emit('page-change', newPage)
}
</script>
