<template>
  <div class="relative w-full">
    <div class="relative flex items-center">
      <input
        type="text"
        :value="displayLabel"
        @input="onInput"
        @focus="openDropdown"
        :placeholder="placeholder || `Search ${doctype}...`"
        class="w-full bg-white border border-slate-200 rounded-lg pl-2.5 pr-7 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-sans"
      />
      <button
        v-if="modelValue"
        @click="clear"
        type="button"
        class="absolute right-2 text-slate-400 hover:text-slate-600 p-0.5"
      >
        <X class="w-3 h-3" />
      </button>
      <Search v-else class="w-3.5 h-3.5 text-slate-400 absolute right-2.5 pointer-events-none" />
    </div>

    <!-- Search Options Dropdown -->
    <div
      v-if="isOpen"
      class="absolute left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-40 max-h-48 overflow-y-auto divide-y divide-slate-100 text-xs"
    >
      <div v-if="loading" class="p-2 text-center text-slate-400">
        Searching {{ doctype }}...
      </div>
      <div v-else-if="options.length === 0" class="p-2 text-center text-slate-400">
        No matching {{ doctype }} records.
      </div>
      <button
        v-else
        v-for="opt in options"
        :key="opt.value"
        @click="selectOption(opt)"
        type="button"
        class="w-full text-left px-2.5 py-1.5 hover:bg-blue-50 transition-colors flex items-center justify-between group"
      >
        <span class="font-mono text-blue-600 font-bold group-hover:underline">{{ opt.value }}</span>
        <span v-if="opt.label && opt.label !== opt.value" class="text-slate-500 font-sans truncate max-w-[150px]">{{ opt.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search, X } from 'lucide-vue-next'
import { searchLinkOptions } from '../../services/api'

const props = defineProps({
  doctype: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  placeholder: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const loading = ref(false)
const searchQuery = ref('')
const options = ref([])

const displayLabel = computed(() => {
  if (isOpen.value) return searchQuery.value
  return props.modelValue || ''
})

const fetchOptions = async (query = '') => {
  if (!props.doctype) return
  loading.value = true
  try {
    const res = await searchLinkOptions(props.doctype, query)
    if (res.success) {
      options.value = res.data || []
    }
  } catch (e) {
    options.value = []
  } finally {
    loading.value = false
  }
}

const openDropdown = () => {
  isOpen.value = true
  searchQuery.value = ''
  fetchOptions('')
}

const onInput = (e) => {
  searchQuery.value = e.target.value
  isOpen.value = true
  fetchOptions(searchQuery.value)
}

const selectOption = (opt) => {
  emit('update:modelValue', opt.value)
  isOpen.value = false
  searchQuery.value = ''
}

const clear = () => {
  emit('update:modelValue', '')
  searchQuery.value = ''
  isOpen.value = false
}

// Close on outside click
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      isOpen.value = false
    }
  })
})
</script>
