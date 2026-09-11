<template>
  <div class="space-y-6">
    <!-- SECTION-SPECIFIC OPERATIONAL DASHBOARD VIEW -->
    <template v-if="isDashboardRoute">
      <WorkspaceDashboard 
        :workspace-id="workspaceId"
        :workspace-title="sectionDashboardTitle"
      />
    </template>

    <!-- STANDARD DOCTYPE LIST VIEW & DOCUMENT ENGINE -->
    <template v-else>
      <PageHeader 
        :title="pageInfo.title" 
        :description="`View and manage ${pageInfo.title} records.`"
      >
        <template #actions>
          <div class="flex items-center space-x-2">
            <button
              @click="loadData"
              class="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors"
            >
              <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
              <span>Refresh</span>
            </button>
            <button
              @click="openCreateDrawer"
              class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>New {{ pageInfo.title }}</span>
            </button>
          </div>
        </template>
      </PageHeader>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <DataTable
          :columns="columns"
          :rows="rows"
          :total-count="totalCount"
          :page="page"
          :page-size="pageSize"
          :loading="loading"
          :error="error"
          @search="handleSearch"
          @page-change="handlePageChange"
          @row-click="handleRowClick"
        />
      </div>

      <!-- Record Detail Modal Drawer -->
      <div 
        v-if="selectedDoc" 
        class="fixed inset-0 bg-slate-950/70 backdrop-blur-xs flex justify-end z-40 transition-opacity"
        @click.self="selectedDoc = null"
      >
        <div class="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl overflow-hidden animate-slide-left">
          <div class="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-mono font-bold text-blue-400">{{ selectedDoc.name }}</span>
                <StatusBadge :status="selectedDoc.status || 'Draft'" />
              </div>
              <h3 class="text-sm font-semibold text-slate-100 mt-1">
                {{ selectedDoc.title || selectedDoc.name }}
              </h3>
            </div>
            <button 
              @click="selectedDoc = null"
              class="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Document Action Toolbar -->
          <div class="px-4 py-2 bg-slate-950 border-b border-slate-800/80 flex items-center justify-between flex-wrap gap-2 text-xs">
            <!-- Dynamic Workflow Actions -->
            <div v-if="workflowInfo && workflowInfo.transitions && workflowInfo.transitions.length" class="flex items-center space-x-1.5">
              <button
                v-for="trans in workflowInfo.transitions"
                :key="trans.action"
                @click="handleWorkflowAction(trans.action)"
                class="px-2.5 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/40 text-indigo-200 font-semibold rounded transition-colors"
              >
                {{ trans.action }}
              </button>
            </div>

            <!-- Standard Actions -->
            <div class="flex items-center space-x-2 ml-auto">
              <button
                v-if="selectedPermissions && selectedPermissions.write && selectedDoc.docstatus === 0"
                @click="openEditDrawer"
                class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded flex items-center space-x-1 transition-colors"
              >
                <Edit3 class="w-3 h-3" />
                <span>Edit</span>
              </button>
              <button
                v-if="selectedPermissions && selectedPermissions.submit && selectedDoc.docstatus === 0"
                @click="handleSubmitDoc"
                class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded transition-colors"
              >
                Submit
              </button>
              <button
                v-if="selectedPermissions && selectedPermissions.cancel && selectedDoc.docstatus === 1"
                @click="handleCancelDoc"
                class="px-2.5 py-1 bg-rose-600/30 hover:bg-rose-600/50 border border-rose-500/40 text-rose-300 font-semibold rounded transition-colors"
              >
                Cancel
              </button>
              <button
                v-if="selectedPermissions && selectedPermissions.amend && selectedDoc.docstatus === 2"
                @click="handleAmendDoc"
                class="px-2.5 py-1 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-500/40 text-amber-300 font-semibold rounded transition-colors"
              >
                Amend
              </button>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <LoadingState v-if="detailLoading" message="Loading record details..." />

            <template v-else>
              <!-- Primary Document Info Grid -->
              <div class="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
                <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Document Details</h4>
                <div class="grid grid-cols-2 gap-4">
                  <div 
                    v-for="(val, key) in filterDisplayFields(selectedDoc)" 
                    :key="key"
                    class="border-b border-slate-800/40 pb-2"
                  >
                    <div class="text-[10px] text-slate-500 font-mono uppercase">{{ formatFieldLabel(key) }}</div>
                    <div class="text-xs text-slate-200 font-mono mt-0.5 break-words">{{ val }}</div>
                  </div>
                </div>
              </div>

              <!-- Child Tables Preview -->
              <div v-for="(childRows, childKey) in filterChildTables(selectedDoc)" :key="childKey" class="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
                <h4 class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center justify-between">
                  <span>{{ formatFieldLabel(childKey) }}</span>
                  <span class="text-[10px] text-slate-500 font-mono">{{ childRows.length }} rows</span>
                </h4>
                <div class="overflow-x-auto">
                  <table class="w-full text-left text-xs font-mono">
                    <thead>
                      <tr class="text-slate-500 border-b border-slate-800 text-[10px] uppercase">
                        <th v-for="(v, k) in childRows[0]" :key="k" class="py-1.5 px-2">{{ formatFieldLabel(k) }}</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800/40 text-slate-300">
                      <tr v-for="(r, idx) in childRows" :key="idx">
                        <td v-for="(v, k) in r" :key="k" class="py-1.5 px-2 truncate max-w-[150px]">{{ v }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Related Documents -->
              <div v-if="relatedDocs && relatedDocs.length" class="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
                <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Related ERPNext Documents</h4>
                <RelatedDocuments :documents="relatedDocs" />
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Edit / Create Form Engine Drawer -->
      <FormDrawer
        v-if="drawerOpen"
        :doc-type="pageInfo.docType"
        :initial-data="editData"
        :fields="formFields"
        @close="drawerOpen = false"
        @saved="handleRecordSaved"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { RefreshCw, Plus, X, Edit3 } from 'lucide-vue-next'
import PageHeader from '../components/layout/PageHeader.vue'
import DataTable from '../components/tables/DataTable.vue'
import StatusBadge from '../components/tables/StatusBadge.vue'
import RelatedDocuments from '../components/documents/RelatedDocuments.vue'
import FormDrawer from '../components/documents/FormDrawer.vue'
import WorkspaceDashboard from '../components/dashboard/WorkspaceDashboard.vue'
import LoadingState from '../components/ui/LoadingState.vue'
import { 
  getDocumentList, 
  getDocumentDetail, 
  getDocTypeMeta, 
  submitDocument, 
  cancelDocument, 
  amendDocument, 
  applyWorkflowAction 
} from '../services/api'
import { workspaces, openDocument } from '../config/navigation'

const route = useRoute()
const loading = ref(false)
const error = ref('')
const rows = ref([])
const page = ref(1)
const pageSize = ref(15)
const totalCount = ref(0)
const searchText = ref('')

const metaInfo = ref(null)
const selectedDoc = ref(null)
const selectedDocMeta = ref(null)
const selectedPermissions = ref(null)
const workflowInfo = ref(null)
const relatedDocs = ref([])
const detailLoading = ref(false)

const drawerOpen = ref(false)
const formFields = ref([])
const editData = ref({})

const isDashboardRoute = computed(() => {
  const p = route.path.toLowerCase()
  return p.endsWith('/dashboard') || route.params.module === 'dashboard' || pageInfo.value.viewType === 'dashboard'
})

const workspaceId = computed(() => {
  const path = route.path
  const matched = workspaces.find(w => path.startsWith(w.route))
  return matched ? matched.id : 'project-management'
})

const sectionDashboardTitle = computed(() => {
  const currentPath = route.path
  for (const ws of workspaces) {
    for (const sec of ws.sections) {
      for (const item of sec.items) {
        if (item.route === currentPath) {
          return `${sec.title} Dashboard`
        }
      }
    }
  }
  return `${pageInfo.value.title || 'Section'} Dashboard`
})

const pageInfo = computed(() => {
  const currentPath = route.path
  for (const ws of workspaces) {
    for (const sec of ws.sections) {
      for (const item of sec.items) {
        if (item.route === currentPath) {
          return { title: item.label, docType: item.docType || 'Project', viewType: item.viewType }
        }
      }
    }
  }
  const parts = currentPath.split('/')
  const slug = parts[parts.length - 1]
  const title = slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  return { title, docType: 'Project' }
})

const columns = computed(() => {
  if (metaInfo.value && metaInfo.value.list_fields && metaInfo.value.list_fields.length > 0) {
    return metaInfo.value.list_fields
  }
  return [
    { key: 'name', label: 'ID / Name' },
    { key: 'title', label: 'Title / Description' },
    { key: 'status', label: 'Status' },
    { key: 'modified', label: 'Last Modified' }
  ]
})

const loadData = async () => {
  if (isDashboardRoute.value) return

  loading.value = true
  error.value = ''
  try {
    if (!metaInfo.value || metaInfo.value.name !== pageInfo.value.docType) {
      const metaRes = await getDocTypeMeta(pageInfo.value.docType)
      if (metaRes.success) {
        metaInfo.value = metaRes.data
        formFields.value = metaRes.data.fields || []
      }
    }

    const res = await getDocumentList(pageInfo.value.docType, {
      page: page.value,
      pageLength: pageSize.value,
      searchText: searchText.value
    })
    
    if (res.success) {
      const titleField = res.meta?.title_field || metaInfo.value?.title_field || 'name'
      const statusField = res.meta?.status_field || metaInfo.value?.status_field

      rows.value = res.data.map(item => {
        let statusVal = item.status
        if (!statusVal && statusField && item[statusField] !== undefined) {
          if (statusField === 'disabled') {
            statusVal = item.disabled ? 'Disabled' : 'Active'
          } else {
            statusVal = String(item[statusField])
          }
        }
        if (!statusVal) {
          statusVal = item.docstatus === 1 ? 'Submitted' : (item.docstatus === 2 ? 'Cancelled' : 'Draft')
        }

        return {
          ...item,
          title: item[titleField] || item.name,
          status: statusVal
        }
      })
      totalCount.value = res.meta?.total || rows.value.length
    } else {
      error.value = res.error?.message || 'Failed to load records'
    }
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

const fetchMeta = async () => {
  try {
    const res = await getDocTypeMeta(pageInfo.value.docType)
    if (res.success) {
      metaInfo.value = res.data
      formFields.value = res.data.fields || []
    }
  } catch (err) {
    console.error('Meta fetch error:', err)
  }
}

const handleSearch = (query) => {
  searchText.value = query
  page.value = 1
  loadData()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  loadData()
}


const contextualTargets = ref([])
const showCreateDropdown = ref(false)

const loadContextualTargets = async (docType) => {
  contextualTargets.value = []
  showCreateDropdown.value = false
  try {
    const res = await getContextualCreateOptions(docType)
    if (res && res.success) {
      contextualTargets.value = res.data || []
    }
  } catch (err) {
    contextualTargets.value = []
  }
}

const handleCreateTarget = async (targetDocType) => {
  showCreateDropdown.value = false
  if (!selectedDoc.value) return
  try {
    const res = await getCreateTargetPayload(pageInfo.value.docType, selectedDoc.value.name, targetDocType)
    if (res && res.success) {
      drawerDocType.value = targetDocType
      editData.value = res.data || {}
      drawerMode.value = 'create'
      drawerOpen.value = true
    } else {
      alert("Failed to pre-fill payload: " + (res?.error?.message || "Unknown error"))
    }
  } catch (err) {
    alert("Error preparing target document: " + (err.message || "Unknown error"))
  }
}

const handleRowClick = (row) => {
  if (row && row.name) {
    openDocument(pageInfo.value.docType, row.name, router, route.path)
  }
}

const openCreateDrawer = async () => {
  await fetchMeta()
  editData.value = {}
  drawerOpen.value = true
}

const openEditDrawer = async () => {
  await fetchMeta()
  editData.value = { ...selectedDoc.value }
  drawerOpen.value = true
}

const handleRecordSaved = (savedDoc) => {
  if (selectedDoc.value && savedDoc && savedDoc.name === selectedDoc.value.name) {
    selectedDoc.value = savedDoc
  }
  loadData()
}


const handlePrintPdf = async () => {
  if (!selectedDoc.value) return
  try {
    const res = await getDocumentPdf(pageInfo.value.docType, selectedDoc.value.name)
    if (res && res.success && res.data?.pdf_base64) {
      const byteCharacters = atob(res.data.pdf_base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'application/pdf' })
      const blobUrl = URL.createObjectURL(blob)
      window.open(blobUrl, '_blank')
    } else {
      alert('Print error: ' + (res?.error?.message || 'Failed to generate PDF'))
    }
  } catch (err) {
    alert('Print error: ' + (err.message || 'Error communicating with server'))
  }
}

const handleSubmitDoc = async () => {
  try {
    if (pageInfo.value.docType === "Purchase Order") {
      const gateRes = await validateSupplierPORelease(selectedDoc.value.name)
      if (!gateRes.success) {
        alert("BUSINESS GATE BLOCKED: " + (gateRes.error?.message || "Finance Commitment required."))
        return
      }
    }
    const res = await submitDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      selectedDoc.value = res.data
      loadContextualTargets(pageInfo.value.docType)
      loadData()
    } else {
      alert('Submit error: ' + (res.error?.message || 'Failed to submit'))
    }
  } catch (err) {
    alert('Submit error: ' + (err.response?.data?.message || err.message))
  }
}

const handleCancelDoc = async () => {
  try {
    const res = await cancelDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      selectedDoc.value = res.data
      loadContextualTargets(pageInfo.value.docType)
      loadData()
    } else {
      alert('Cancel error: ' + (res.error?.message || 'Failed to cancel'))
    }
  } catch (err) {
    alert('Cancel error: ' + (err.response?.data?.message || err.message))
  }
}

const handleAmendDoc = async () => {
  try {
    const res = await amendDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      editData.value = res.data
      drawerOpen.value = true
    } else {
      alert('Amend error: ' + (res.error?.message || 'Failed to amend'))
    }
  } catch (err) {
    alert('Amend error: ' + (err.response?.data?.message || err.message))
  }
}

const handleWorkflowAction = async (action) => {
  try {
    const res = await applyWorkflowAction(pageInfo.value.docType, selectedDoc.value.name, action)
    if (res.success) {
      selectedDoc.value = res.data
      loadContextualTargets(pageInfo.value.docType)
      handleRowClick(selectedDoc.value)
      loadData()
    } else {
      alert('Workflow error: ' + (res.error?.message || 'Failed action'))
    }
  } catch (err) {
    alert('Workflow error: ' + (err.response?.data?.message || err.message))
  }
}

const filterDisplayFields = (doc) => {
  if (!doc) return {}
  const ignored = ['doctype', 'docstatus', 'idx', '_user_tags', '_comments', '_assign', '_liked_by']
  const filtered = {}
  for (const [k, v] of Object.entries(doc)) {
    if (!ignored.includes(k) && !Array.isArray(v) && typeof v !== 'object') {
      filtered[k] = v
    }
  }
  return filtered
}

const filterChildTables = (doc) => {
  if (!doc) return {}
  const childs = {}
  for (const [k, v] of Object.entries(doc)) {
    if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'object') {
      childs[k] = v.map(row => {
        const cleanRow = {}
        for (const [rk, rv] of Object.entries(row)) {
          if (!['name', 'owner', 'creation', 'modified', 'modified_by', 'parent', 'parentfield', 'parenttype', 'docstatus', 'idx'].includes(rk)) {
            cleanRow[rk] = rv
          }
        }
        return cleanRow
      })
    }
  }
  return childs
}

const formatFieldLabel = (key) => {
  return key.replace(/_/g, ' ').replace(/\w/g, l => l.toUpperCase())
}

onMounted(() => {
  loadData()
})

watch(() => route.path, () => {
  metaInfo.value = null
  page.value = 1
  searchText.value = ''
  selectedDoc.value = null
  loadData()
})
</script>
