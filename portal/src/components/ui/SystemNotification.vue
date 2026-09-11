<template>
  <div>
    <!-- BLOCKING SYSTEM DIALOG MODAL -->
    <Transition name="fade-scale">
      <div 
        v-if="dialog" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-100 backdrop-blur-xs"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="dialog.id + '-title'"
        :aria-describedby="dialog.id + '-desc'"
        @keydown.esc="handleEsc"
        tabindex="-1"
        ref="modalOverlayRef"
      >
        <div 
          class="w-full max-w-md bg-white border border-slate-200 rounded-xl shadow-2xl overflow-hidden text-slate-900"
          @click.stop
        >
          <!-- Modal Header -->
          <div class="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between bg-white/20">
            <div class="flex items-center space-x-2.5">
              <AlertCircle v-if="dialog.type === 'error'" class="w-4 h-4 text-rose-500 shrink-0" />
              <AlertTriangle v-else-if="dialog.type === 'warning' || dialog.type === 'confirm'" class="w-4 h-4 text-amber-500 shrink-0" />
              <Info v-else class="w-4 h-4 text-blue-600 shrink-0" />

              <h3 
                :id="dialog.id + '-title'"
                class="text-sm font-bold uppercase tracking-wider font-mono text-slate-800"
              >
                {{ dialog.title }}
              </h3>
            </div>

            <button 
              @click="close(false)" 
              class="text-slate-600 hover:text-slate-700 p-1 rounded-md transition-colors"
              aria-label="Close dialog"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Modal Body -->
          <div class="px-5 py-4 text-sm text-slate-700 leading-relaxed font-sans" :id="dialog.id + '-desc'">
            <p class="whitespace-pre-wrap select-text break-words">{{ dialog.message }}</p>
          </div>

          <!-- Modal Footer Actions -->
          <div class="px-5 py-3 border-t border-slate-200 bg-slate-100 flex items-center justify-end space-x-2">
            <button
              v-if="dialog.cancelText"
              @click="close(false)"
              type="button"
              class="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded transition-colors"
            >
              {{ dialog.cancelText }}
            </button>

            <button
              ref="okBtnRef"
              @click="close(true)"
              type="button"
              :class="okButtonClass"
            >
              {{ dialog.okText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- NON-BLOCKING TOAST NOTIFICATIONS (TOP RIGHT) -->
    <div class="fixed top-4 right-4 z-50 flex flex-col space-y-2 max-w-sm w-full pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto bg-white border border-slate-200 shadow-xl rounded-lg p-3 flex items-start space-x-3 text-sm text-slate-800"
        >
          <CheckCircle2 v-if="t.type === 'success'" class="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <Info v-else class="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />

          <div class="flex-1 min-w-0">
            <div v-if="t.title" class="font-bold text-slate-900 text-[11px] font-mono uppercase tracking-wider mb-0.5">
              {{ t.title }}
            </div>
            <div class="text-slate-700 truncate font-sans">{{ t.message }}</div>
          </div>

          <button 
            @click="removeToast(t.id)" 
            class="text-slate-600 hover:text-slate-700 p-0.5 rounded"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, nextTick, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { AlertCircle, AlertTriangle, Info, CheckCircle2, X } from 'lucide-vue-next'
import { useNotificationStore } from '../../stores/notification'

const store = useNotificationStore()
const { activeDialog: dialog, toasts } = storeToRefs(store)

const okBtnRef = ref(null)
const modalOverlayRef = ref(null)

const okButtonClass = computed(() => {
  if (!dialog.value) return ''
  if (dialog.value.type === 'error') {
    return 'px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold rounded shadow-xs transition-colors'
  }
  if (dialog.value.type === 'warning' || dialog.value.type === 'confirm') {
    return 'px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded shadow-xs transition-colors'
  }
  return 'px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-medium rounded transition-colors'
})

const close = (confirmed) => {
  store.closeDialog(confirmed)
}

const removeToast = (id) => {
  store.removeToast(id)
}

const handleEsc = () => {
  close(false)
}

watch(dialog, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (okBtnRef.value) {
        okBtnRef.value.focus()
      } else if (modalOverlayRef.value) {
        modalOverlayRef.value.focus()
      }
    })
  }
})
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
