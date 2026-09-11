<template>
  <div class="relative flex-1 max-w-lg mx-4" ref="searchContainerRef">
    <!-- Search Bar Input Box -->
    <div 
      class="relative flex items-center bg-slate-100/90 border border-slate-300 rounded-lg text-sm text-slate-800 focus-within:bg-white focus-within:border-blue-600 focus-within:ring-1 focus-within:ring-blue-500 shadow-2xs transition-all"
    >
      <Search class="w-4 h-4 text-slate-500 absolute left-3 shrink-0 pointer-events-none" />

      <input
        ref="searchInputRef"
        v-model="searchQuery"
        type="text"
        placeholder="Search for a DocType, document, report or action..."
        class="w-full bg-transparent pl-9 pr-16 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none font-medium"
        @focus="isOpen = true"
        @input="handleInput"
        @keydown.down.prevent="navigateResults('down')"
        @keydown.up.prevent="navigateResults('up')"
        @keydown.enter.prevent="selectHighlighted"
        @keydown.esc="closeDropdown"
      />

      <!-- Right Side Spinner / Clear / Keyboard Shortcut Badge -->
      <div class="absolute right-2.5 flex items-center space-x-1.5 pointer-events-none">
        <Loader2 v-if="loading" class="w-3.5 h-3.5 text-blue-600 animate-spin" />
        <button 
          v-else-if="searchQuery" 
          @click.stop="clearSearch"
          type="button"
          class="pointer-events-auto text-slate-400 hover:text-slate-700 p-0.5 rounded transition-colors"
        >
          <X class="w-3.5 h-3.5" />
        </button>
        <span v-else class="hidden sm:inline-flex items-center px-1.5 py-0.5 bg-slate-200 border border-slate-300 rounded text-[10px] font-mono font-bold text-slate-600">
          {{ isMac ? '⌘K' : 'Ctrl+K' }}
        </span>
      </div>
    </div>

    <!-- Dropdown Menu -->
    <div 
      v-if="isOpen && (searchQuery.trim().length >= 2 || hasResults)"
      class="absolute top-full left-0 right-0 mt-1.5 bg-white border border-slate-200 rounded-lg shadow-xl z-50 overflow-hidden max-h-96 overflow-y-auto text-sm"
    >
      <!-- Loading State -->
      <div v-if="loading && !hasResults" class="p-4 text-center text-slate-500 text-sm flex items-center justify-center space-x-2">
        <Loader2 class="w-4 h-4 text-blue-600 animate-spin" />
        <span>Searching ERPNext records...</span>
      </div>

      <!-- Results List -->
      <div v-else-if="hasResults" class="py-1.5 divide-y divide-slate-100">
        
        <!-- Category: DOCUMENT TYPES -->
        <div v-if="results.doctypes && results.doctypes.length > 0" class="py-1">
          <div class="px-3 py-1 text-[11px] font-bold font-mono text-slate-600 uppercase tracking-wider bg-slate-50/80">
            DOCUMENT TYPES
          </div>
          <div 
            v-for="(item, idx) in results.doctypes" 
            :key="'dt-' + item.doctype"
            @click="selectItem(item, 'doctype')"
            @mouseenter="selectedIndex = getItemIndex('doctype', idx)"
            :class="[
              'px-3 py-2 flex items-center justify-between cursor-pointer transition-colors',
              selectedIndex === getItemIndex('doctype', idx) ? 'bg-blue-50 text-blue-800 font-semibold' : 'hover:bg-slate-50 text-slate-800'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <FileText class="w-4 h-4 text-blue-600 shrink-0" />
              <span>{{ item.label }}</span>
            </div>
            <span class="text-[10px] font-mono text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
              {{ item.module }}
            </span>
          </div>
        </div>

        <!-- Category: ACTIONS -->
        <div v-if="results.actions && results.actions.length > 0" class="py-1">
          <div class="px-3 py-1 text-[11px] font-bold font-mono text-slate-600 uppercase tracking-wider bg-slate-50/80">
            ACTIONS
          </div>
          <div 
            v-for="(item, idx) in results.actions" 
            :key="'act-' + item.doctype"
            @click="selectItem(item, 'action')"
            @mouseenter="selectedIndex = getItemIndex('action', idx)"
            :class="[
              'px-3 py-2 flex items-center justify-between cursor-pointer transition-colors',
              selectedIndex === getItemIndex('action', idx) ? 'bg-emerald-50 text-emerald-800 font-semibold' : 'hover:bg-slate-50 text-slate-800'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <PlusCircle class="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{{ item.label }}</span>
            </div>
            <span class="text-[10px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
              New Record
            </span>
          </div>
        </div>

        <!-- Category: DOCUMENTS -->
        <div v-if="results.documents && results.documents.length > 0" class="py-1">
          <div class="px-3 py-1 text-[11px] font-bold font-mono text-slate-600 uppercase tracking-wider bg-slate-50/80">
            EXISTING DOCUMENTS
          </div>
          <div 
            v-for="(item, idx) in results.documents" 
            :key="'doc-' + item.doctype + '-' + item.name"
            @click="selectItem(item, 'document')"
            @mouseenter="selectedIndex = getItemIndex('document', idx)"
            :class="[
              'px-3 py-2 flex items-center justify-between cursor-pointer transition-colors',
              selectedIndex === getItemIndex('document', idx) ? 'bg-blue-50 text-blue-800 font-semibold' : 'hover:bg-slate-50 text-slate-800'
            ]"
          >
            <div class="flex items-center space-x-2.5 min-w-0 flex-1">
              <Folder class="w-4 h-4 text-slate-600 shrink-0" />
              <div class="truncate">
                <span class="font-mono text-blue-700 font-bold mr-2">{{ item.name }}</span>
                <span v-if="item.title && item.title !== item.name" class="text-slate-600 truncate">
                  - {{ item.title }}
                </span>
              </div>
            </div>
            
            <div class="flex items-center space-x-1.5 shrink-0 ml-2">
              <span v-if="item.project" class="text-[10px] font-mono text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                {{ item.project }}
              </span>
              <StatusBadge v-if="item.status" :status="item.status" />
            </div>
          </div>
        </div>

        <!-- Category: REPORTS -->
        <div v-if="results.reports && results.reports.length > 0" class="py-1">
          <div class="px-3 py-1 text-[11px] font-bold font-mono text-slate-600 uppercase tracking-wider bg-slate-50/80">
            REPORTS
          </div>
          <div 
            v-for="(item, idx) in results.reports" 
            :key="'rep-' + item.name"
            @click="selectItem(item, 'report')"
            @mouseenter="selectedIndex = getItemIndex('report', idx)"
            :class="[
              'px-3 py-2 flex items-center justify-between cursor-pointer transition-colors',
              selectedIndex === getItemIndex('report', idx) ? 'bg-purple-50 text-purple-800 font-semibold' : 'hover:bg-slate-50 text-slate-800'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <BarChart3 class="w-4 h-4 text-purple-600 shrink-0" />
              <span>{{ item.label }}</span>
            </div>
            <span class="text-[10px] font-mono text-purple-700 bg-purple-50 border border-purple-200 px-1.5 py-0.5 rounded">
              Report
            </span>
          </div>
        </div>

      </div>

      <!-- Empty State -->
      <div v-else-if="searchQuery.trim().length >= 2" class="p-6 text-center text-slate-600 text-sm">
        <p>No matching DocTypes, documents, or reports found for <span class="font-bold text-slate-900">"{{ searchQuery }}"</span>.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Loader2, X, FileText, PlusCircle, Folder, BarChart3 } from 'lucide-vue-next'
import { globalSearch } from '../../services/api'
import { resolveDocTypeRoute, resolveReportRoute } from '../../services/routeResolver'
import StatusBadge from '../tables/StatusBadge.vue'
import { useNotificationStore } from '../../stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()

const searchInputRef = ref(null)
const searchContainerRef = ref(null)
const searchQuery = ref('')
const isOpen = ref(false)
const loading = ref(false)
const selectedIndex = ref(0)

const results = ref({
  doctypes: [],
  actions: [],
  documents: [],
  reports: []
})

const isMac = computed(() => typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0)

const flatResultsList = computed(() => {
  const list = []
  for (const item of results.value.doctypes || []) {
    list.push({ ...item, itemType: 'doctype' })
  }
  for (const item of results.value.actions || []) {
    list.push({ ...item, itemType: 'action' })
  }
  for (const item of results.value.documents || []) {
    list.push({ ...item, itemType: 'document' })
  }
  for (const item of results.value.reports || []) {
    list.push({ ...item, itemType: 'report' })
  }
  return list
})

const hasResults = computed(() => flatResultsList.value.length > 0)

let debounceTimer = null

const handleInput = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  
  if (searchQuery.value.trim().length < 2) {
    results.value = { doctypes: [], actions: [], documents: [], reports: [] }
    loading.value = false
    return
  }

  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const data = await globalSearch(searchQuery.value)
      results.value = data || { doctypes: [], actions: [], documents: [], reports: [] }
      selectedIndex.value = 0
    } catch (err) {
      notificationStore.showError({
        title: 'Search Error',
        message: err.message || 'Failed to execute global search'
      })
    } finally {
      loading.value = false
    }
  }, 200)
}

const getItemIndex = (type, idx) => {
  let offset = 0
  if (type === 'action') {
    offset += (results.value.doctypes || []).length
  } else if (type === 'document') {
    offset += (results.value.doctypes || []).length + (results.value.actions || []).length
  } else if (type === 'report') {
    offset += (results.value.doctypes || []).length + (results.value.actions || []).length + (results.value.documents || []).length
  }
  return offset + idx
}

const navigateResults = (direction) => {
  const total = flatResultsList.value.length
  if (total === 0) return

  if (direction === 'down') {
    selectedIndex.value = (selectedIndex.value + 1) % total
  } else if (direction === 'up') {
    selectedIndex.value = (selectedIndex.value - 1 + total) % total
  }
}

const selectHighlighted = () => {
  const item = flatResultsList.value[selectedIndex.value]
  if (item) {
    selectItem(item, item.itemType)
  }
}

const selectItem = (item, type) => {
  isOpen.value = false
  searchQuery.value = ''

  if (type === 'doctype') {
    const route = resolveDocTypeRoute(item.doctype)
    router.push(route)
  } else if (type === 'action') {
    const route = resolveDocTypeRoute(item.doctype, null, 'new')
    router.push(route)
  } else if (type === 'document') {
    const route = resolveDocTypeRoute(item.doctype, item.name)
    router.push(route)
  } else if (type === 'report') {
    const route = resolveReportRoute(item.name, item.ref_doctype)
    router.push(route)
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  results.value = { doctypes: [], actions: [], documents: [], reports: [] }
}

const closeDropdown = () => {
  isOpen.value = false
}

const handleClickOutside = (e) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

const handleGlobalKeyDown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    if (searchInputRef.value) {
      searchInputRef.value.focus()
      searchInputRef.value.select()
      isOpen.value = true
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeyDown)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeyDown)
  document.removeEventListener('click', handleClickOutside)
})
</script>
