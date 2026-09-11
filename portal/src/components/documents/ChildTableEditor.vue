<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block font-medium text-slate-300 text-xs">
        {{ label }} ({{ rows.length }} rows)
      </label>
      <button 
        v-if="!readOnly"
        type="button" 
        @click="addRow" 
        class="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-blue-400 rounded text-[11px] border border-slate-700 transition-colors flex items-center space-x-1"
      >
        <Plus class="w-3 h-3" />
        <span>Add Row</span>
      </button>
    </div>

    <div class="overflow-x-auto border border-slate-800 rounded-lg bg-slate-950/60">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-950 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider select-none">
          <tr>
            <th class="py-2 px-2.5 w-8 text-center">#</th>
            <th 
              v-for="col in displayColumns" 
              :key="col.fieldname" 
              class="py-2 px-2.5"
            >
              {{ col.label }}
              <span v-if="col.reqd" class="text-red-400 ml-0.5">*</span>
            </th>
            <th v-if="!readOnly" class="py-2 px-2.5 w-10 text-center"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          <tr v-if="rows.length === 0">
            <td :colspan="displayColumns.length + (readOnly ? 1 : 2)" class="py-3 text-center text-slate-500 text-[11px] italic">
              No rows added yet.
            </td>
          </tr>
          <tr v-for="(row, idx) in rows" :key="idx" class="hover:bg-slate-900/40">
            <td class="py-2 px-2.5 text-center font-mono text-[11px] text-slate-500 select-none">
              {{ idx + 1 }}
            </td>
            <td v-for="col in displayColumns" :key="col.fieldname" class="py-1.5 px-2">
              <input 
                v-if="!readOnly && ['Data', 'Currency', 'Float', 'Int', 'Date'].includes(col.fieldtype)"
                v-model="row[col.fieldname]"
                :type="col.fieldtype === 'Date' ? 'date' : ['Currency', 'Float', 'Int'].includes(col.fieldtype) ? 'number' : 'text'"
                class="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-blue-600"
              />
              <select 
                v-else-if="!readOnly && col.fieldtype === 'Select'"
                v-model="row[col.fieldname]"
                class="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-blue-600"
              >
                <option value="">Select</option>
                <option v-for="opt in parseOptions(col.options)" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <span v-else class="text-slate-300 font-medium text-xs break-all">
                {{ row[col.fieldname] !== undefined && row[col.fieldname] !== null ? row[col.fieldname] : '-' }}
              </span>
            </td>
            <td v-if="!readOnly" class="py-1.5 px-2 text-center">
              <button 
                type="button" 
                @click="removeRow(idx)" 
                class="p-1 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
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
import { computed } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  label: { type: String, required: true },
  childFields: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  readOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const rows = computed({
  get: () => props.modelValue || [],
  set: (val) => emit('update:modelValue', val)
})

const displayColumns = computed(() => {
  if (props.childFields.length === 0) return []
  // Prefer in_list_view fields or top 6 readable fields
  const inList = props.childFields.filter(f => f.in_list_view)
  if (inList.length > 0) return inList.slice(0, 6)
  return props.childFields.filter(f => !['Section Break', 'Column Break', 'HTML'].includes(f.fieldtype)).slice(0, 6)
})

const addRow = () => {
  const newRow = {}
  props.childFields.forEach(f => {
    newRow[f.fieldname] = f.default || ''
  })
  emit('update:modelValue', [...rows.value, newRow])
}

const removeRow = (index) => {
  const copy = [...rows.value]
  copy.splice(index, 1)
  emit('update:modelValue', copy)
}

const parseOptions = (optionsStr) => {
  if (!optionsStr) return []
  return optionsStr.split('\n').map(s => s.trim()).filter(Boolean)
}
</script>
