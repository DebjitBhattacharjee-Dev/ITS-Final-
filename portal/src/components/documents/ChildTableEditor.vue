<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block font-medium text-slate-700 text-sm">
        {{ computedLabel }} ({{ tableRows.length }} rows)
      </label>
      <button 
        v-if="!readOnly"
        type="button" 
        @click="addRow" 
        class="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded text-[11px] transition-colors flex items-center space-x-1"
      >
        <Plus class="w-3 h-3" />
        <span>Add Row</span>
      </button>
    </div>

    <div class="overflow-x-auto border border-slate-200 rounded-lg bg-white/30">
      <table class="w-full text-left text-sm">
        <thead class="bg-white border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider select-none">
          <tr>
            <th class="py-2 px-2.5 w-8 text-center">#</th>
            <th 
              v-for="col in displayColumns" 
              :key="col.fieldname" 
              class="py-2 px-2.5 min-w-[120px]"
            >
              {{ col.label }}
              <span v-if="col.reqd" class="text-rose-400 ml-0.5">*</span>
            </th>
            <th v-if="!readOnly" class="py-2 px-2.5 w-10 text-center"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200/60">
          <tr v-if="tableRows.length === 0">
            <td :colspan="displayColumns.length + (readOnly ? 1 : 2)" class="py-4 text-center text-slate-600 text-[11px] italic">
              No rows added. Click "Add Row" to enter items.
            </td>
          </tr>
          <tr v-for="(row, idx) in tableRows" :key="idx" class="hover:bg-white/40">
            <td class="py-2 px-2.5 text-center font-mono text-[11px] text-slate-600 select-none">
              {{ idx + 1 }}
            </td>
            <td v-for="col in displayColumns" :key="col.fieldname" class="py-1.5 px-2">
              <template v-if="!readOnly">
                <LinkInput
                  v-if="col.fieldtype === 'Link'"
                  :doctype="col.options"
                  v-model="row[col.fieldname]"
                />

                <select 
                  v-else-if="col.fieldtype === 'Select'"
                  v-model="row[col.fieldname]"
                  class="w-full bg-white border border-slate-200 rounded px-2 py-1 text-sm text-slate-800 focus:outline-none focus:border-blue-600"
                >
                  <option value="">Select {{ col.label }}</option>
                  <option v-for="opt in parseOptions(col.options)" :key="opt" :value="opt">{{ opt }}</option>
                </select>

                <div v-else-if="col.fieldtype === 'Check'" class="flex items-center justify-center">
                  <input
                    type="checkbox"
                    v-model="row[col.fieldname]"
                    :true-value="1"
                    :false-value="0"
                    class="w-4 h-4 rounded border-slate-200 bg-white text-blue-600"
                  />
                </div>

                <input 
                  v-else-if="['Currency', 'Float', 'Int', 'Percent'].includes(col.fieldtype)"
                  v-model.number="row[col.fieldname]"
                  type="number"
                  class="w-full bg-white border border-slate-200 rounded px-2 py-1 text-sm text-slate-800 focus:outline-none focus:border-blue-600 font-mono"
                />

                <input 
                  v-else-if="col.fieldtype === 'Date'"
                  v-model="row[col.fieldname]"
                  type="date"
                  class="w-full bg-white border border-slate-200 rounded px-2 py-1 text-sm text-slate-800 focus:outline-none focus:border-blue-600"
                />

                <input 
                  v-else
                  v-model="row[col.fieldname]"
                  type="text"
                  class="w-full bg-white border border-slate-200 rounded px-2 py-1 text-sm text-slate-800 focus:outline-none focus:border-blue-600"
                />
              </template>

              <span v-else class="text-slate-700 font-medium text-sm break-all">
                {{ row[col.fieldname] !== undefined && row[col.fieldname] !== null ? row[col.fieldname] : '-' }}
              </span>
            </td>
            <td v-if="!readOnly" class="py-1.5 px-2 text-center">
              <button 
                type="button" 
                @click="removeRow(idx)" 
                class="p-1 text-slate-600 hover:text-rose-400 hover:bg-slate-100 rounded transition-colors"
                title="Remove Row"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import LinkInput from './LinkInput.vue'
import { getDocTypeMeta } from '../../services/api'

const props = defineProps({
  tableField: { type: Object, default: () => ({}) },
  label: { type: String, default: '' },
  childFields: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  readOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['update:rows', 'update:modelValue'])

const fieldsList = ref(props.childFields || [])

const computedLabel = computed(() => props.label || props.tableField?.label || 'Table Items')

const tableRows = computed({
  get: () => props.rows?.length ? props.rows : (props.modelValue || []),
  set: (val) => {
    emit('update:rows', val)
    emit('update:modelValue', val)
  }
})

const loadChildMeta = async () => {
  const childDocType = props.tableField?.options
  if (childDocType && fieldsList.value.length === 0) {
    try {
      const res = await getDocTypeMeta(childDocType)
      if (res && res.fields) {
        fieldsList.value = res.fields
      } else if (res && res.data && res.data.fields) {
        fieldsList.value = res.data.fields
      }
    } catch (e) {
      console.error('Child doctype meta error:', e)
    }
  }
}

onMounted(() => {
  loadChildMeta()
})

watch(() => props.tableField, () => {
  loadChildMeta()
})

const displayColumns = computed(() => {
  const all = fieldsList.value.length ? fieldsList.value : props.childFields
  if (!all || all.length === 0) return []
  const inList = all.filter(f => f.in_list_view && f.fieldname)
  if (inList.length > 0) return inList.slice(0, 8)
  return all.filter(f => f.fieldname && !['Section Break', 'Column Break', 'HTML'].includes(f.fieldtype)).slice(0, 8)
})

const addRow = () => {
  const newRow = {}
  const all = fieldsList.value.length ? fieldsList.value : props.childFields
  all.forEach(f => {
    if (f.fieldname) {
      newRow[f.fieldname] = f.default || (['Currency', 'Float', 'Int'].includes(f.fieldtype) ? 0 : '')
    }
  })
  const updated = [...tableRows.value, newRow]
  emit('update:rows', updated)
  emit('update:modelValue', updated)
}

const removeRow = (index) => {
  const updated = [...tableRows.value]
  updated.splice(index, 1)
  emit('update:rows', updated)
  emit('update:modelValue', updated)
}

const parseOptions = (optionsStr) => {
  if (!optionsStr) return []
  if (Array.isArray(optionsStr)) return optionsStr
  return String(optionsStr).split(/\r?\n/).map(s => s.trim()).filter(Boolean)
}
</script>
