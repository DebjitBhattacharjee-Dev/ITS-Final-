<template>
  <div class="space-y-4">
    <!-- Top Breadcrumb & Navigation -->
    <div class="flex items-center justify-between border-b border-slate-200 pb-3">
      <div class="flex items-center space-x-2 text-sm text-slate-600">
        <button @click="goBackToList" class="hover:text-slate-800 flex items-center space-x-1 font-medium transition-colors">
          <ArrowLeft class="w-3.5 h-3.5" />
          <span>Back to List</span>
        </button>
        <span class="text-slate-600">/</span>
        <span class="font-semibold text-slate-800">{{ pageTitle }}</span>
        <span class="text-slate-600">/</span>
        <span class="font-mono text-blue-600 font-bold">{{ docId }}</span>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="fetchDocumentData"
          class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-sm font-medium flex items-center space-x-1 transition-colors"
        >
          <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="p-12 flex flex-col items-center justify-center text-slate-600 space-y-3">
      <Loader2 class="w-6 h-6 animate-spin text-blue-600" />
      <span class="text-sm">Loading ERPNext document details...</span>
    </div>

    <div v-else-if="error" class="p-6 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 text-sm">
      <div class="font-bold flex items-center space-x-2 mb-1">
        <AlertCircle class="w-4 h-4" />
        <span>Failed to Load Document</span>
      </div>
      <p>{{ error }}</p>
      <button @click="goBackToList" class="mt-3 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded text-sm">
        Return to List
      </button>
    </div>

    <div v-else-if="doc" class="space-y-4">
      <!-- Full-Page Document Header Card -->
      <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <div class="flex items-center space-x-3">
              <h1 class="text-base font-bold font-mono text-blue-600">{{ doc.name }}</h1>
              <StatusBadge :status="doc.status || (doc.docstatus === 1 ? 'Submitted' : doc.docstatus === 2 ? 'Cancelled' : 'Draft')" />
              <span v-if="doc.workflow_state" class="px-2 py-0.5 bg-indigo-950/80 border border-indigo-700/50 text-indigo-300 rounded-full text-[10px] font-semibold">
                {{ doc.workflow_state }}
              </span>
            </div>
            <p class="text-sm text-slate-600 mt-1">
              {{ docType }} — Modified {{ doc.modified ? new Date(doc.modified).toLocaleString() : 'Recently' }} by {{ doc.modified_by || 'System' }}
            </p>
          </div>

          <!-- Document Action Toolbar -->
          <div class="flex items-center space-x-2 flex-wrap gap-1.5 text-sm">
            <!-- Dynamic Workflow Actions -->
            <template v-if="workflowInfo && workflowInfo.transitions && workflowInfo.transitions.length">
              <button
                v-for="trans in workflowInfo.transitions"
                :key="trans.action"
                @click="handleWorkflowAction(trans.action)"
                class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded transition-colors shadow-xs"
              >
                {{ trans.action }}
              </button>
            </template>

            <!-- Contextual Create > Dropdown -->
            <div v-if="contextualTargets && contextualTargets.length" class="relative inline-block text-left">
              <button
                @click="showCreateDropdown = !showCreateDropdown"
                class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded flex items-center space-x-1 transition-colors shadow-xs"
              >
                <span>Create</span>
                <ChevronDown class="w-3.5 h-3.5 ml-0.5" />
              </button>
              <div
                v-if="showCreateDropdown"
                class="origin-top-right absolute right-0 mt-1 w-48 rounded-md shadow-lg bg-white border border-slate-200 ring-1 ring-black ring-opacity-5 z-50 py-1"
              >
                <button
                  v-for="target in contextualTargets"
                  :key="target"
                  @click="handleCreateTarget(target)"
                  class="w-full text-left px-3 py-2 text-sm text-slate-800 hover:bg-blue-50 hover:text-blue-600 flex items-center justify-between transition-colors"
                >
                  <span>{{ target }}</span>
                  <ArrowRight class="w-3 h-3 text-slate-600" />
                </button>
              </div>
            </div>

            <!-- Standard Document Actions -->
            <button
              v-if="!isEditing && doc.docstatus === 0 && userPermissions.write"
              @click="isEditing = true"
              class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium rounded flex items-center space-x-1 transition-colors"
            >
              <Edit3 class="w-3.5 h-3.5" />
              <span>Edit</span>
            </button>

            <button
              v-if="isEditing"
              @click="isEditing = false"
              class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded transition-colors"
            >
              Cancel Edit
            </button>

            <button
              v-if="isEditing"
              @click="handleSaveDoc"
              :disabled="saving"
              class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded flex items-center space-x-1 transition-colors shadow-xs"
            >
              <Save class="w-3.5 h-3.5" />
              <span>{{ saving ? 'Saving...' : 'Save' }}</span>
            </button>

            <button
              v-if="doc.docstatus === 0 && userPermissions.submit && meta?.is_submittable"
              @click="handleSubmitDoc"
              class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded transition-colors shadow-xs"
            >
              Submit
            </button>

            <button
              v-if="doc.docstatus === 1 && userPermissions.cancel && meta?.is_submittable"
              @click="handleCancelDoc"
              class="px-3 py-1.5 bg-rose-600/30 hover:bg-rose-600/50 border border-rose-500/40 text-rose-300 font-semibold rounded transition-colors"
            >
              Cancel
            </button>

            <button
              v-if="doc.docstatus === 2 && userPermissions.amend && meta?.is_submittable"
              @click="handleAmendDoc"
              class="px-3 py-1.5 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-500/40 text-amber-300 font-semibold rounded transition-colors"
            >
              Amend
            </button>

            <!-- Duplicate Button -->
            <button
              v-if="userPermissions.create"
              @click="handleDuplicateDoc"
              class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium rounded flex items-center space-x-1 transition-colors"
              title="Duplicate into a new draft"
            >
              <Copy class="w-3.5 h-3.5 text-indigo-400" />
              <span>Duplicate</span>
            </button>

            <!-- Delete Button -->
            <button
              v-if="userPermissions.delete && doc.docstatus === 0"
              @click="handleDeleteDoc"
              class="px-3 py-1.5 bg-rose-950/60 hover:bg-rose-900/80 border border-rose-800/80 text-rose-300 font-medium rounded flex items-center space-x-1 transition-colors"
              title="Delete this document"
            >
              <Trash2 class="w-3.5 h-3.5" />
              <span>Delete</span>
            </button>

            <!-- Print PDF Button -->
            <button
              @click="handlePrintPdf"
              class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium rounded flex items-center space-x-1 transition-colors"
            >
              <Printer class="w-3.5 h-3.5 text-blue-600" />
              <span>Print PDF</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Main Document Form Body -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Left 2 Columns: Form Fields & Child Tables -->
        <div class="lg:col-span-2 space-y-4">
          <!-- Fields Card -->
          <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider border-b border-slate-200 pb-2">
              Document Fields
            </h2>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div v-for="field in formFields" :key="field.fieldname" class="space-y-1">
                <label class="block text-[11px] font-medium text-slate-600">
                  {{ field.label }}
                  <span v-if="field.reqd" class="text-rose-400">*</span>
                </label>

                <!-- Read Only View -->
                <div v-if="!isEditing || field.read_only || doc.docstatus !== 0" class="p-2 bg-white/30 border border-slate-200 rounded text-slate-800 font-medium text-sm font-mono min-h-[34px] flex items-center">
                  {{ formatFieldValue(formData[field.fieldname], field) }}
                </div>

                <!-- Editable Input View -->
                <template v-else>
                  <LinkInput
                    v-if="field.fieldtype === 'Link'"
                    :doctype="field.options"
                    v-model="formData[field.fieldname]"
                    :placeholder="'Select ' + field.label"
                  />

                  <select
                    v-else-if="field.fieldtype === 'Select'"
                    v-model="formData[field.fieldname]"
                    class="w-full bg-white border border-slate-200 rounded px-2.5 py-1.5 text-slate-800 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option v-for="opt in parseSelectOptions(field.options)" :key="opt" :value="opt">
                      {{ opt }}
                    </option>
                  </select>

                  <input
                    v-else-if="['Currency', 'Float', 'Int', 'Percent'].includes(field.fieldtype)"
                    type="number"
                    v-model.number="formData[field.fieldname]"
                    class="w-full bg-white border border-slate-200 rounded px-2.5 py-1.5 text-slate-800 text-sm focus:outline-none focus:border-blue-500 font-mono"
                  />

                  <input
                    v-else-if="field.fieldtype === 'Date'"
                    type="date"
                    v-model="formData[field.fieldname]"
                    class="w-full bg-white border border-slate-200 rounded px-2.5 py-1.5 text-slate-800 text-sm focus:outline-none focus:border-blue-500"
                  />

                  <div v-else-if="field.fieldtype === 'Check'" class="flex items-center space-x-2 py-1">
                    <input
                      type="checkbox"
                      v-model="formData[field.fieldname]"
                      :true-value="1"
                      :false-value="0"
                      class="w-4 h-4 rounded border-slate-200 bg-white text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-slate-700 text-sm font-medium">{{ field.label }}</span>
                  </div>

                  <textarea
                    v-else-if="['Small Text', 'Text', 'Long Text', 'Code'].includes(field.fieldtype)"
                    v-model="formData[field.fieldname]"
                    rows="3"
                    class="w-full bg-white border border-slate-200 rounded px-2.5 py-1.5 text-slate-800 text-sm focus:outline-none focus:border-blue-500"
                  ></textarea>

                  <input
                    v-else
                    type="text"
                    v-model="formData[field.fieldname]"
                    class="w-full bg-white border border-slate-200 rounded px-2.5 py-1.5 text-slate-800 text-sm focus:outline-none focus:border-blue-500"
                  />
                </template>
              </div>
            </div>
          </div>

          <!-- Child Tables Section -->
          <div v-for="tableField in tableFields" :key="tableField.fieldname" class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
            <h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider border-b border-slate-200 pb-2">
              {{ tableField.label }}
            </h2>
            <ChildTableEditor
              :table-field="tableField"
              :rows="formData[tableField.fieldname] || []"
              :read-only="!isEditing || doc.docstatus !== 0"
              @update:rows="newRows => formData[tableField.fieldname] = newRows"
            />
          </div>
        </div>

        <!-- Right 1 Column: Linked Related Documents & Audit Sidebar -->
        <div class="space-y-4">
          <!-- Related Documents Card -->
          <RelatedDocuments :related="relatedDocs" />

          <!-- Audit Meta Card -->
          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3 text-sm">
            <h3 class="font-bold text-slate-700 uppercase tracking-wider border-b border-slate-200 pb-2 text-[11px]">
              Audit & System Metadata
            </h3>
            <div class="space-y-2 text-slate-600 text-[11px]">
              <div class="flex justify-between">
                <span>Created By:</span>
                <span class="text-slate-800 font-mono">{{ doc.owner || 'System' }}</span>
              </div>
              <div class="flex justify-between">
                <span>Created On:</span>
                <span class="text-slate-800 font-mono">{{ doc.creation ? new Date(doc.creation).toLocaleDateString() : '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span>Last Modified:</span>
                <span class="text-slate-800 font-mono">{{ doc.modified ? new Date(doc.modified).toLocaleDateString() : '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span>DocStatus:</span>
                <span class="text-slate-800 font-mono">{{ doc.docstatus }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, RefreshCw, Loader2, AlertCircle, Edit3, Save, Printer,
  ChevronDown, ArrowRight, Copy, Trash2, CheckCircle2
} from 'lucide-vue-next'
import StatusBadge from '../components/tables/StatusBadge.vue'
import LinkInput from '../components/documents/LinkInput.vue'
import ChildTableEditor from '../components/documents/ChildTableEditor.vue'
import RelatedDocuments from '../components/documents/RelatedDocuments.vue'
import {
  getDocumentDetail,
  saveDocument,
  submitDocument,
  cancelDocument,
  amendDocument,
  deleteDocument,
  duplicateDocument,
  applyWorkflowAction,
  getDocTypeMeta,
  getRelatedDocuments,
  getDocumentPdf,
  getContextualCreateOptions,
  getCreateTargetPayload,
  validateSupplierPORelease
} from '../services/api'
import { WORKSPACES } from '../config/navigation'
import { useNotificationStore } from '../stores/notification'
import { extractFrappeErrorMessage } from '../utils/error'

const notificationStore = useNotificationStore()


const route = useRoute()
const router = useRouter()

const docId = ref(route.params.id)
const doc = ref(null)
const formData = ref({})
const meta = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const isEditing = ref(false)
const workflowInfo = ref(null)
const userPermissions = ref({ read: true, write: true, create: true, delete: true, submit: false, cancel: false, amend: false })
const relatedDocs = ref([])
const contextualTargets = ref([])
const showCreateDropdown = ref(false)

const pathInfo = computed(() => {
  const listPath = route.path.substring(0, route.path.lastIndexOf('/'))
  for (const ws of WORKSPACES) {
    for (const sec of ws.sections || []) {
      for (const item of sec.items || []) {
        if (item.route === listPath) {
          return { title: item.label, docType: item.docType || 'Project' }
        }
      }
    }
  }
  return { title: route.params.module || 'Document', docType: route.params.module || 'Project' }
})

const docType = computed(() => pathInfo.value?.docType || 'Project')
const pageTitle = computed(() => pathInfo.value?.title || docType.value)

const formFields = computed(() => {
  if (!meta.value?.fields) return []
  return meta.value.fields.filter(f => !['Table', 'HTML', 'Heading', 'Column Break', 'Section Break'].includes(f.fieldtype) && !f.hidden)
})

const tableFields = computed(() => {
  if (!meta.value?.fields) return []
  return meta.value.fields.filter(f => f.fieldtype === 'Table')
})

const fetchDocumentData = async () => {
  loading.value = true
  error.value = null
  try {
    const [detailRes, metaRes, relRes, optsRes] = await Promise.all([
      getDocumentDetail(docType.value, docId.value),
      getDocTypeMeta(docType.value),
      getRelatedDocuments(docType.value, docId.value),
      getContextualCreateOptions(docType.value)
    ])

    if (detailRes && detailRes.success && detailRes.data) {
      const docData = detailRes.data.document || detailRes.data.doc
      doc.value = docData
      formData.value = { ...docData }
      workflowInfo.value = detailRes.data.workflow
      if (detailRes.data.permissions) {
        userPermissions.value = detailRes.data.permissions
      }
      if (detailRes.data.related) {
        relatedDocs.value = detailRes.data.related
      }
    } else {
      error.value = detailRes?.error?.message || 'Document not found'
    }

    if (metaRes && metaRes.success) {
      meta.value = metaRes.data
    }

    if (relRes && relRes.success) {
      relatedDocs.value = relRes.data || []
    }

    if (optsRes && optsRes.success) {
      contextualTargets.value = optsRes.data || []
    }
  } catch (err) {
    error.value = err.message || 'Failed to fetch document'
  } finally {
    loading.value = false
  }
}

const handleSaveDoc = async () => {
  saving.value = true
  try {
    const res = await saveDocument(docType.value, formData.value)
    if (res && res.success) {
      doc.value = res.data
      formData.value = { ...res.data }
      isEditing.value = false
      notificationStore.showSuccess('Document saved successfully')
      fetchDocumentData()
    } else {
      notificationStore.showError('Save Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Save Error', extractFrappeErrorMessage(null, err))
  } finally {
    saving.value = false
  }
}

const handleSubmitDoc = async () => {
  try {
    if (docType.value === 'Purchase Order') {
      const gateRes = await validateSupplierPORelease(doc.value.name)
      if (!gateRes.success) {
        notificationStore.showWarning('Business Gate Blocked', gateRes.error?.message || 'Finance Commitment required.')
        return
      }
    }
    const res = await submitDocument(docType.value, doc.value.name)
    if (res && res.success) {
      doc.value = res.data
      notificationStore.showSuccess('Document submitted successfully')
      fetchDocumentData()
    } else {
      notificationStore.showError('Submit Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Submit Error', extractFrappeErrorMessage(null, err))
  }
}

const handleCancelDoc = async () => {
  try {
    const res = await cancelDocument(docType.value, doc.value.name)
    if (res && res.success) {
      doc.value = res.data
      notificationStore.showSuccess('Document cancelled successfully')
      fetchDocumentData()
    } else {
      notificationStore.showError('Cancel Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Cancel Error', extractFrappeErrorMessage(null, err))
  }
}

const handleAmendDoc = async () => {
  try {
    const res = await amendDocument(docType.value, doc.value.name)
    if (res && res.success) {
      doc.value = res.data
      formData.value = { ...res.data }
      isEditing.value = true
      notificationStore.showSuccess('Amended draft created')
    } else {
      notificationStore.showError('Amend Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Amend Error', extractFrappeErrorMessage(null, err))
  }
}

const handleDeleteDoc = async () => {
  const confirmed = await notificationStore.showConfirm(
    'Delete Document',
    `Are you sure you want to delete ${docType.value} "${doc.value.name}"? This action cannot be undone.`
  )
  if (!confirmed) return

  try {
    const res = await deleteDocument(docType.value, doc.value.name)
    if (res && res.success) {
      notificationStore.showSuccess('Document deleted successfully')
      goBackToList()
    } else {
      notificationStore.showError('Delete Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Delete Error', extractFrappeErrorMessage(null, err))
  }
}

const handleDuplicateDoc = async () => {
  try {
    const res = await duplicateDocument(docType.value, doc.value.name)
    if (res && res.success) {
      doc.value = res.data
      formData.value = { ...res.data }
      isEditing.value = true
      notificationStore.showSuccess('Document duplicated successfully')
    } else {
      notificationStore.showError('Duplicate Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Duplicate Error', extractFrappeErrorMessage(null, err))
  }
}

const handleWorkflowAction = async (action) => {
  try {
    const res = await applyWorkflowAction(docType.value, doc.value.name, action)
    if (res && res.success) {
      notificationStore.showSuccess(`Workflow action "${action}" applied`)
      fetchDocumentData()
    } else {
      notificationStore.showError('Workflow Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Workflow Error', extractFrappeErrorMessage(null, err))
  }
}

const handleCreateTarget = async (targetDocType) => {
  showCreateDropdown.value = false
  try {
    const res = await getCreateTargetPayload(docType.value, doc.value.name, targetDocType)
    if (res && res.success) {
      router.push({
        path: route.path.substring(0, route.path.lastIndexOf('/')),
        query: { create_target: targetDocType, payload: JSON.stringify(res.data) }
      })
    } else {
      notificationStore.showError('Create Action Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Create Action Error', extractFrappeErrorMessage(null, err))
  }
}

const handlePrintPdf = async () => {
  try {
    const res = await getDocumentPdf(docType.value, doc.value.name)
    if (res && res.success && (res.data?.pdf_base64 || res.data?.html_base64)) {
      const b64 = res.data.pdf_base64 || res.data.html_base64
      const mime = res.data.pdf_base64 ? 'application/pdf' : 'text/html'
      const byteCharacters = atob(b64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: mime })
      const blobUrl = URL.createObjectURL(blob)
      window.open(blobUrl, '_blank')
    } else {
      notificationStore.showError('Print Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Print Error', extractFrappeErrorMessage(null, err))
  }
}


const goBackToList = () => {
  const lastSlash = route.path.lastIndexOf('/')
  if (lastSlash > 0) {
    router.push(route.path.substring(0, lastSlash))
  } else {
    router.back()
  }
}

const formatFieldValue = (val, field) => {
  if (val === null || val === undefined || val === '') return '-'
  if (['Currency', 'Float'].includes(field.fieldtype)) {
    return 'AED ' + Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  return val
}

const parseSelectOptions = (options) => {
  if (!options) return []
  if (Array.isArray(options)) return options
  return String(options).split(/\r?\n/).map(o => o.trim()).filter(Boolean)
}

onMounted(() => {
  fetchDocumentData()
})

watch(() => route.params.id, (newId) => {
  if (newId) {
    docId.value = newId
    fetchDocumentData()
  }
})
</script>
