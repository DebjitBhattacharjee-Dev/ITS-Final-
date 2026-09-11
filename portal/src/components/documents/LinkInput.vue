<template>
  <div class="relative">
    <div class="relative">
      <input 
        v-model="searchQuery"
        @focus="onFocus"
        @input="onInput"
        :placeholder="placeholder || `Select ${targetDocType}`"
        :disabled="disabled"
        class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 pr-8 text-xs text-slate-200 focus:outline-none focus:border-blue-600 disabled:opacity-50"
      />
      <button 
        v-if="searchQuery && !disabled"
        type="button"
        @click="clear"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
      >
        <X class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Options Dropdown -->
    <div 
      v-if="showDropdown && options.length > 0"
      class="absolute z-50 left-0 right-0 mt-1 bg-slate-900 border border-slate-800 rounded-md shadow-xl max-h-48 overflow-y-auto py-1 text-xs"
    >
      <button 
        v-for="opt in options" 
        :key="opt.value"
        type="button"
        @click="selectOption(opt)"
        class="w-full text-left px-3 py-1.5 hover:bg-blue-950/60 hover:text-blue-300 text-slate-200 truncate flex items-center justify-between"
      >
        <span>{{ opt.label }}</span>
        <span class="font-mono text-[10px] text-slate-500 ml-2">{{ opt.value }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { searchLinkOptions } from '../../services/api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  targetDocType: { type: String, required: true },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const searchQuery = ref(props.modelValue || '')
const options = ref([])
const showDropdown = ref(false)
let debounceTimeout = null

watch(() => props.modelValue, (val) => {
  searchQuery.value = val || ''
})

const fetchOptions = async (query = '') => {
  try {
    const res = await searchLinkOptions(props.targetDocType, query)
    if (res.success) {
      options.value = res.data || []
    }
  } catch (err) {
    console.error('Link fetch error:', err)
  }
}

const onFocus = () => {
  if (props.disabled) return
  showDropdown.value = true
  fetchOptions(searchQuery.value)
}

const onInput = () => {
  emit('update:modelValue', searchQuery.value)
  showDropdown.value = true
  clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    fetchOptions(searchQuery.value)
  }, 250)
}

const selectOption = (opt) => {
  searchQuery.value = opt.value
  emit('update:modelValue', opt.value)
  showDropdown.value = false
}

const clear = () => {
  searchQuery.value = ''
  emit('update:modelValue', '')
  showDropdown.value = false
}
</script>
