<template>
  <div class="select-none">
    <div
      class="flex items-center justify-between px-3 py-2 hover:bg-slate-50 transition-colors cursor-pointer group"
      @click="$emit('node-click', node)"
    >
      <div class="flex items-center space-x-2">
        <button
          v-if="node.is_group"
          @click.stop="toggleExpand"
          class="p-0.5 text-slate-400 hover:text-slate-700 rounded transition-colors"
        >
          <ChevronRight class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-90': expanded }" />
        </button>
        <span v-else class="w-4"></span>

        <Folder v-if="node.is_group" class="w-4 h-4 text-amber-500 fill-amber-100" />
        <FileText v-else class="w-4 h-4 text-slate-400" />

        <span class="font-mono text-blue-600 font-bold group-hover:underline">{{ node.name }}</span>
        <span v-if="node.title && node.title !== node.name" class="text-slate-600 font-sans">({{ node.title }})</span>
      </div>

      <span v-if="node.is_group" class="text-[10px] uppercase font-mono font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
        Group
      </span>
    </div>

    <div v-if="expanded" class="pl-6 border-l border-slate-100 ml-4 space-y-1 py-1">
      <div v-if="loadingChildren" class="py-1 text-[11px] text-slate-400">Loading children...</div>
      <TreeNodeItem
        v-for="child in children"
        :key="child.name"
        :node="child"
        :doctype="doctype"
        @node-click="$emit('node-click', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronRight, Folder, FileText } from 'lucide-vue-next'
import { getTreeNodes } from '../../services/api'

const props = defineProps({
  node: { type: Object, required: true },
  doctype: { type: String, required: true }
})

const emit = defineEmits(['node-click'])

const expanded = ref(false)
const children = ref([])
const loadingChildren = ref(false)

const toggleExpand = async () => {
  expanded.value = !expanded.value
  if (expanded.value && children.value.length === 0) {
    loadingChildren.value = true
    try {
      const res = await getTreeNodes(props.doctype, null, props.node.name)
      if (res.success) {
        children.value = res.data || []
      }
    } catch (e) {
      console.error('Failed to load children nodes:', e)
    } finally {
      loadingChildren.value = false
    }
  }
}
</script>
