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
      <GenericListView
        :doc-type="pageInfo.docType"
        :page-title="pageInfo.title"
        @open-create="openCreateDrawer"
      />

      <!-- Record Detail Modal Drawer -->
      <div 
        v-if="selectedDoc" 
        class="fixed inset-0 bg-white/30 backdrop-blur-xs flex justify-end z-40 transition-opacity"
        @click.self="selectedDoc = null"
      >
        <div class="w-full max-w-2xl bg-white border-l border-slate-200 h-full flex flex-col shadow-2xl overflow-hidden animate-slide-left">
          <div class="p-4 border-b border-slate-200 flex items-center justify-between bg-white">
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-sm font-mono font-bold text-blue-600">{{ selectedDoc.name }}</span>
                <StatusBadge :status="selectedDoc.status || 'Draft'" />
              </div>
              <h3 class="text-sm font-semibold text-slate-900 mt-1">
                {{ selectedDoc.title || selectedDoc.name }}
              </h3>
            </div>
            <button 
              @click="selectedDoc = null"
              class="p-1 hover:bg-slate-100 rounded text-slate-600 hover:text-slate-800 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Document Action Toolbar -->
          <div class="px-4 py-2 bg-white border-b border-slate-200 flex items-center justify-between flex-wrap gap-2 text-sm">
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
                class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium rounded flex items-center space-x-1 transition-colors"
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
              <div class="bg-white/30 border border-slate-200 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-3">Document Details</h4>
                <div class="grid grid-cols-2 gap-4">
                  <div 
                    v-for="(val, key) in filterDisplayFields(selectedDoc)" 
                    :key="key"
                    class="border-b border-slate-200/40 pb-2"
                  >
                    <div class="text-[10px] text-slate-600 font-mono uppercase">{{ formatFieldLabel(key) }}</div>
                    <div class="text-sm text-slate-800 font-mono mt-0.5 break-words">{{ val }}</div>
                  </div>
                </div>
              </div>

              <!-- Child Tables Preview -->
              <div v-for="(childRows, childKey) in filterChildTables(selectedDoc)" :key="childKey" class="bg-white/30 border border-slate-200 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3 flex items-center justify-between">
                  <span>{{ formatFieldLabel(childKey) }}</span>
                  <span class="text-[10px] text-slate-600 font-mono">{{ childRows.length }} rows</span>
                </h4>
                <div class="overflow-x-auto">
                  <table class="w-full text-left text-sm font-mono">
                    <thead>
                      <tr class="text-slate-600 border-b border-slate-200 text-[10px] uppercase">
                        <th v-for="(v, k) in childRows[0]" :key="k" class="py-1.5 px-2">{{ formatFieldLabel(k) }}</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200/40 text-slate-700">
                      <tr v-for="(r, idx) in childRows" :key="idx">
                        <td v-for="(v, k) in r" :key="k" class="py-1.5 px-2 truncate max-w-[150px]">{{ v }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Related Documents -->
              <div v-if="relatedDocs && relatedDocs.length" class="bg-white/30 border border-slate-200 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-3">Related ERPNext Documents</h4>
                <RelatedDocuments :documents="relatedDocs" />
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Edit / Create Form Engine Drawer -->
      <FormDrawer
        v-if="drawerOpen"
        :open="drawerOpen"
        :doc-type="drawerDocType || pageInfo.docType"
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
import { useRoute, useRouter } from 'vue-router'
import { RefreshCw, Plus, X, Edit3 } from 'lucide-vue-next'
import PageHeader from '../components/layout/PageHeader.vue'
import GenericListView from '../components/tables/GenericListView.vue'
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
import { useNotificationStore } from '../stores/notification'
import { extractFrappeErrorMessage } from '../utils/error'

const notificationStore = useNotificationStore()


const route = useRoute()
const router = useRouter()
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
const drawerDocType = ref('')
const drawerMode = ref('create')
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

const fetchMeta = async (dt) => {
  const targetType = dt || pageInfo.value.docType
  try {
    const res = await getDocTypeMeta(targetType)
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
      notificationStore.showError('Create Action Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Create Action Error', extractFrappeErrorMessage(null, err))
  }
}

const handleRowClick = (row) => {
  if (row && row.name) {
    openDocument(pageInfo.value.docType, row.name, router, route.path)
  }
}

const openCreateDrawer = async (docTypeToCreate) => {
  const targetType = (typeof docTypeToCreate === 'string' && docTypeToCreate) ? docTypeToCreate : pageInfo.value.docType
  drawerDocType.value = targetType
  drawerMode.value = 'create'
  await fetchMeta(targetType)
  editData.value = {}
  drawerOpen.value = true
}

const openEditDrawer = async () => {
  const targetType = pageInfo.value.docType
  drawerDocType.value = targetType
  drawerMode.value = 'edit'
  await fetchMeta(targetType)
  editData.value = { ...selectedDoc.value }
  drawerOpen.value = true
}

const handleRecordSaved = (savedDoc) => {
  if (selectedDoc.value && savedDoc && savedDoc.name === selectedDoc.value.name) {
    selectedDoc.value = savedDoc
  }
  notificationStore.showSuccess('Document saved successfully')
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
      notificationStore.showError('Print Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Print Error', extractFrappeErrorMessage(null, err))
  }
}

const handleSubmitDoc = async () => {
  try {
    if (pageInfo.value.docType === "Purchase Order") {
      const gateRes = await validateSupplierPORelease(selectedDoc.value.name)
      if (!gateRes.success) {
        notificationStore.showWarning("Business Gate Blocked", gateRes.error?.message || "Finance Commitment required.")
        return
      }
    }
    const res = await submitDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      selectedDoc.value = res.data
      notificationStore.showSuccess('Document submitted successfully')
      loadContextualTargets(pageInfo.value.docType)
      loadData()
    } else {
      notificationStore.showError('Submit Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Submit Error', extractFrappeErrorMessage(null, err))
  }
}

const handleCancelDoc = async () => {
  try {
    const res = await cancelDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      selectedDoc.value = res.data
      notificationStore.showSuccess('Document cancelled successfully')
      loadContextualTargets(pageInfo.value.docType)
      loadData()
    } else {
      notificationStore.showError('Cancel Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Cancel Error', extractFrappeErrorMessage(null, err))
  }
}

const handleAmendDoc = async () => {
  try {
    const res = await amendDocument(pageInfo.value.docType, selectedDoc.value.name)
    if (res.success) {
      editData.value = res.data
      drawerOpen.value = true
      notificationStore.showSuccess('Amended draft created')
    } else {
      notificationStore.showError('Amend Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Amend Error', extractFrappeErrorMessage(null, err))
  }
}

const handleWorkflowAction = async (action) => {
  try {
    const res = await applyWorkflowAction(pageInfo.value.docType, selectedDoc.value.name, action)
    if (res.success) {
      selectedDoc.value = res.data
      notificationStore.showSuccess(`Workflow action "${action}" applied`)
      loadContextualTargets(pageInfo.value.docType)
      handleRowClick(selectedDoc.value)
      loadData()
    } else {
      notificationStore.showError('Workflow Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Workflow Error', extractFrappeErrorMessage(null, err))
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
