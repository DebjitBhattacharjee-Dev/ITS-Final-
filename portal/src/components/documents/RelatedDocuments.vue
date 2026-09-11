<template>
  <div class="bg-slate-900 border border-slate-800/80 rounded-lg p-4 shadow-sm">
    <h3 class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
      <Link2 class="w-3.5 h-3.5 text-blue-400" />
      <span>Linked ERPNext Documents</span>
    </h3>

    <div v-if="!related || related.length === 0" class="text-xs text-slate-500 italic py-2">
      No linked documents found for this record.
    </div>

    <div v-else class="space-y-3">
      <div 
        v-for="rel in related" 
        :key="rel.doctype"
        class="bg-slate-950 border border-slate-800/60 rounded p-2.5"
      >
        <div class="flex items-center justify-between text-xs mb-1.5">
          <span class="font-medium text-slate-200">{{ rel.doctype }}</span>
          <span class="px-2 py-0.5 bg-blue-950 text-blue-400 border border-blue-800/40 rounded-full text-[10px] font-mono font-semibold">
            {{ rel.count }} record{{ rel.count === 1 ? "" : "s" }}
          </span>
        </div>

        <div class="space-y-1 mt-2">
          <div 
            v-for="doc in rel.recent" 
            :key="doc.name"
            class="flex items-center justify-between text-[11px] text-slate-400 bg-slate-900/50 hover:bg-slate-900 px-2 py-1 rounded transition-colors"
          >
            <span class="font-mono text-slate-300 font-medium">{{ doc.name }}</span>
            <span class="text-[10px] text-slate-500">{{ doc.status || (doc.docstatus === 1 ? "Submitted" : doc.docstatus === 2 ? "Cancelled" : "Draft") }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Link2 } from "lucide-vue-next"
import { openDocument } from "../../config/navigation"

const router = useRouter()

defineProps({
  related: { type: Array, default: () => [] }
})

const handleNavigate = (docType, name) => {
  openDocument(docType, name, router)
}
</script>
