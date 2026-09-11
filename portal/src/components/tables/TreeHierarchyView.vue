<template>
  <div class="space-y-2 font-sans text-xs">
    <div v-if="loading" class="py-4 text-center text-slate-500">
      Loading tree structure...
    </div>
    <div v-else-if="error" class="py-4 text-center text-rose-600 font-medium">
      {{ error }}
    </div>
    <div v-else-if="nodes.length === 0" class="py-4 text-center text-slate-400">
      No tree nodes found.
    </div>
    <div v-else class="border border-slate-200 rounded-lg divide-y divide-slate-100 bg-white">
      <TreeNodeItem
        v-for="node in nodes"
        :key="node.name"
        :node="node"
        :doctype="doctype"
        @node-click="$emit('node-click', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TreeNodeItem from './TreeNodeItem.vue'
import { getTreeNodes } from '../../services/api'
import { extractFrappeErrorMessage } from '../../utils/error'

const props = defineProps({
  doctype: { type: String, required: true }
})

const emit = defineEmits(['node-click'])

const nodes = ref([])
const loading = ref(false)
const error = ref('')

const fetchRootNodes = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getTreeNodes(props.doctype)
    if (res.success) {
      nodes.value = res.data || []
    } else {
      error.value = res.error?.message || 'Failed to fetch tree nodes'
    }
  } catch (err) {
    error.value = extractFrappeErrorMessage(null, err)
  } finally {
    loading.value = false
  }
}

watch(() => props.doctype, () => {
  fetchRootNodes()
})

onMounted(() => {
  fetchRootNodes()
})
</script>
