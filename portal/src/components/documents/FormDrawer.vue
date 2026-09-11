<template>
  <div v-if="open" class="fixed inset-0 z-50 overflow-hidden bg-slate-950/70 backdrop-blur-sm flex justify-end transition-opacity">
    <div class="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
      <!-- Drawer Header -->
      <div class="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div>
          <h2 class="text-sm font-semibold text-slate-100 flex items-center space-x-2">
            <FileText class="w-4 h-4 text-blue-400" />
            <span>{{ isEdit ? 'Edit' : 'Create New' }} {{ docType }}</span>
          </h2>
          <p class="text-[11px] text-slate-400 mt-0.5">Authoritative ERPNext DocType Form</p>
        </div>
        <button @click="$emit('close')" class="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Drawer Body -->
      <div class="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        <div v-if="loadingTemplate" class="p-4 flex items-center justify-center text-slate-400 space-x-2">
          <Loader2 class="w-4 h-4 animate-spin text-blue-400" />
          <span>Fetching server defaults from Frappe...</span>
        </div>

        <div v-if="saving" class="p-3 bg-blue-950/40 border border-blue-800/40 rounded text-blue-300 text-xs flex items-center space-x-2">
          <Loader2 class="w-4 h-4 animate-spin text-blue-400" />
          <span>Saving document to ERPNext...</span>
        </div>

        <div v-if="error" class="p-3 bg-red-950/50 border border-red-800/60 rounded text-red-300 text-xs flex items-start space-x-2">
          <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <span class="font-medium whitespace-pre-wrap">{{ error }}</span>
        </div>

        <form v-if="!loadingTemplate" @submit.prevent="handleSubmit" class="space-y-4">
          <div v-for="field in formFields" :key="field.fieldname" class="space-y-1">
            <!-- Section Break Header -->
            <div v-if="field.fieldtype === 'Section Break'" class="pt-3 border-t border-slate-800 font-semibold text-slate-200 text-xs uppercase tracking-wider text-blue-400">
              {{ field.label || '' }}
            </div>

            <!-- Tab Break Header -->
            <div v-else-if="field.fieldtype === 'Tab Break'" class="pt-2 border-b border-slate-800 pb-1 font-semibold text-slate-300 text-xs text-slate-400 uppercase">
              {{ field.label || '' }}
            </div>

            <template v-else-if="!['Column Break', 'HTML'].includes(field.fieldtype)">
              <label class="block font-medium text-slate-300">
                {{ field.label }}
                <span v-if="field.reqd" class="text-red-400 ml-0.5">*</span>
              </label>

              <!-- Link Field -->
              <LinkInput
                v-if="field.fieldtype === 'Link'"
                v-model="formData[field.fieldname]"
                :targetDocType="field.options"
                :disabled="field.read_only"
              />

              <!-- Select Field -->
              <select 
                v-else-if="field.fieldtype === 'Select'" 
                v-model="formData[field.fieldname]"
                :required="field.reqd"
                :disabled="field.read_only"
                class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-600 disabled:opacity-50"
              >
                <option value="">Select {{ field.label }}</option>
                <option v-for="opt in parseOptions(field.options)" :key="opt" :value="opt">{{ opt }}</option>
              </select>

              <!-- Child Table Field -->
              <ChildTableEditor
                v-else-if="field.fieldtype === 'Table'"
                :label="field.label"
                :childFields="field.child_fields || []"
                v-model="formData[field.fieldname]"
                :readOnly="field.read_only"
              />

              <!-- Text / Data / Currency / Date Field -->
              <input 
                v-else-if="['Data', 'Currency', 'Float', 'Int', 'Date', 'Datetime'].includes(field.fieldtype)"
                v-model="formData[field.fieldname]"
                :type="field.fieldtype === 'Date' ? 'date' : field.fieldtype === 'Datetime' ? 'datetime-local' : ['Currency', 'Float', 'Int'].includes(field.fieldtype) ? 'number' : 'text'"
                :required="field.reqd"
                :readonly="field.read_only"
                :placeholder="`Enter ${field.label}`"
                class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-600 read-only:opacity-60"
              />

              <!-- Text Area / Small Text -->
              <textarea 
                v-else-if="['Text', 'Small Text', 'Long Text', 'Text Editor'].includes(field.fieldtype)"
                v-model="formData[field.fieldname]"
                :required="field.reqd"
                :readonly="field.read_only"
                rows="3"
                class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-600 read-only:opacity-60"
              ></textarea>

              <!-- Checkbox / Check -->
              <div v-else-if="field.fieldtype === 'Check'" class="flex items-center space-x-2 pt-1">
                <input 
                  type="checkbox"
                  v-model="formData[field.fieldname]"
                  :disabled="field.read_only"
                  class="rounded bg-slate-950 border-slate-800 text-blue-600 focus:ring-0"
                />
                <span class="text-xs text-slate-300">{{ field.label }}</span>
              </div>

              <!-- Read Only Field -->
              <div v-else-if="field.fieldtype === 'Read Only'" class="p-2 bg-slate-950/60 border border-slate-800 rounded text-slate-300 font-medium">
                {{ formData[field.fieldname] !== undefined && formData[field.fieldname] !== null ? formData[field.fieldname] : '-' }}
              </div>

              <span v-if="field.description" class="text-[10px] text-slate-500 block">{{ field.description }}</span>
            </template>
          </div>

          <div class="pt-4 border-t border-slate-800 flex items-center justify-end space-x-2">
            <button 
              type="button" 
              @click="$emit('close')"
              class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-xs transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              :disabled="saving"
              class="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded font-medium text-xs shadow transition-colors flex items-center space-x-1.5"
            >
              <Save class="w-3.5 h-3.5" />
              <span>{{ isEdit ? 'Save Changes' : 'Create Record' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X, FileText, Loader2, Save, AlertTriangle } from 'lucide-vue-next'
import LinkInput from './LinkInput.vue'
import ChildTableEditor from './ChildTableEditor.vue'
import { saveDocument, getNewDocumentTemplate } from '../../services/api'

const props = defineProps({
  open: { type: Boolean, default: false },
  docType: { type: String, required: true },
  fields: { type: Array, default: () => [] },
  initialData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close', 'saved'])

const formData = ref({})
const loadingTemplate = ref(false)
const saving = ref(false)
const error = ref('')
const isEdit = ref(false)

const formFields = computed(() => props.fields || [])

watch(() => props.open, async (val) => {
  if (val) {
    error.value = ''
    isEdit.value = !!props.initialData?.name
    if (isEdit.value) {
      formData.value = { ...props.initialData }
    } else {
      // Fetch server defaults via frappe.new_doc(docType)
      loadingTemplate.value = true
      try {
        const res = await getNewDocumentTemplate(props.docType)
        if (res.success) {
          formData.value = res.data || {}
        } else {
          formData.value = { ...props.initialData }
        }
      } catch (err) {
        formData.value = { ...props.initialData }
      } finally {
        loadingTemplate.value = false
      }
    }
  }
}, { immediate: true })

const parseOptions = (optionsStr) => {
  if (!optionsStr) return []
  return optionsStr.split('\n').map(s => s.trim()).filter(Boolean)
}

const handleSubmit = async () => {
  saving.value = true
  error.value = ''
  try {
    const res = await saveDocument(props.docType, formData.value)
    if (res.success) {
      emit('saved', res.data)
      emit('close')
    } else {
      error.value = res.error?.message || 'Failed to save record'
    }
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'An unexpected error occurred while saving'
  } finally {
    saving.value = false
  }
}
</script>
