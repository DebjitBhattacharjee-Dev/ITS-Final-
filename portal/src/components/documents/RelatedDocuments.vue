<template>
  <div class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
    <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
      <Link2 class="w-3.5 h-3.5 text-blue-600" />
      <span>Linked ERPNext Documents</span>
    </h3>

    <div v-if="!related || related.length === 0" class="text-sm text-slate-600 italic py-2">
      No linked documents found for this record.
    </div>

    <div v-else class="space-y-3">
      <div 
        v-for="rel in related" 
        :key="rel.doctype"
        class="bg-white border border-slate-200 rounded p-2.5"
      >
        <div class="flex items-center justify-between text-sm mb-1.5">
          <span class="font-medium text-slate-800">{{ rel.doctype }}</span>
          <span class="px-2 py-0.5 bg-blue-50 text-blue-600 border border-blue-800/40 rounded-full text-[10px] font-mono font-semibold">
            {{ rel.count }} record{{ rel.count === 1 ? "" : "s" }}
          </span>
        </div>

        <div class="space-y-1 mt-2">
          <div 
            v-for="doc in rel.recent" 
            :key="doc.name"
            class="flex items-center justify-between text-[11px] text-slate-600 bg-slate-50 hover:bg-white px-2 py-1 rounded transition-colors"
          >
            <span class="font-mono text-slate-700 font-medium">{{ doc.name }}</span>
            <span class="text-[10px] text-slate-600">{{ doc.status || (doc.docstatus === 1 ? "Submitted" : doc.docstatus === 2 ? "Cancelled" : "Draft") }}</span>
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
