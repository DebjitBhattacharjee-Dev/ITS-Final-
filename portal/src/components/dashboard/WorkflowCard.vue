<template>
  <div 
    @click="navigate"
    class="bg-white border border-slate-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group flex flex-col"
  >
    <div class="flex items-start justify-between mb-3">
      <!-- Gate numbering (G0, G1) removed per request -->
    </div>
    
    <div class="text-sm font-semibold text-slate-800 mb-4 h-10 line-clamp-2">
      {{ displayLabel }}
    </div>
    
    <div class="mt-auto">
      <div class="text-3xl font-bold text-slate-900 font-mono mb-1 group-hover:text-blue-700">
        {{ displayCount }}
      </div>
      <div class="text-[11px] font-medium text-slate-500 uppercase tracking-wide">
        {{ displayState }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  fallbackGate: {
    type: String,
    required: true
  },
  fallbackLabel: {
    type: String,
    required: true
  }
})

const router = useRouter()

const displayGate = computed(() => props.data?.gate || props.fallbackGate)
const displayLabel = computed(() => props.data?.label || props.fallbackLabel.replace(/_/g, ' '))
const displayCount = computed(() => props.data ? props.data.count : 0)
const displayState = computed(() => props.data?.state_label || 'No Pending Items')

const navigate = () => {
  if (props.data && props.data.list_route) {
    // Navigate to the list route with filters
    // The GenericListView component handles URL ?filters=...
    const filterString = JSON.stringify(props.data.filters)
    router.push({
      path: props.data.list_route,
      query: { filters: filterString }
    })
  }
}
</script>
