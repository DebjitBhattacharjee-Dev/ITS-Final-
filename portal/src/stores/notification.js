import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const activeDialog = ref(null)
  const toasts = ref([])
  let toastCounter = 0

  const showError = (title, message, options = {}) => {
    activeDialog.value = {
      id: Date.now(),
      type: 'error',
      title: title || 'Error',
      message: message || 'An error occurred.',
      okText: options.okText || 'OK',
      cancelText: null,
      onConfirm: null,
      onCancel: null
    }
  }

  const showWarning = (title, message, options = {}) => {
    activeDialog.value = {
      id: Date.now(),
      type: 'warning',
      title: title || 'Warning',
      message: message || 'Please review.',
      okText: options.okText || 'OK',
      cancelText: options.cancelText || null,
      onConfirm: options.onConfirm || null,
      onCancel: options.onCancel || null
    }
  }

  const showConfirm = (title, message, options = {}) => {
    return new Promise((resolve) => {
      activeDialog.value = {
        id: Date.now(),
        type: 'confirm',
        title: title || 'Confirm Action',
        message: message || 'Are you sure you want to proceed?',
        okText: options.okText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        resolvePromise: resolve
      }
    })
  }

  const showSuccess = (message, title = 'Success', duration = 3500) => {
    const id = ++toastCounter
    toasts.value.push({
      id,
      type: 'success',
      title,
      message,
      duration
    })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  const showInfoToast = (message, title = 'Info', duration = 3500) => {
    const id = ++toastCounter
    toasts.value.push({
      id,
      type: 'info',
      title,
      message,
      duration
    })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  const closeDialog = (confirmed = false) => {
    if (activeDialog.value) {
      if (activeDialog.value.resolvePromise) {
        activeDialog.value.resolvePromise(confirmed)
      }
      activeDialog.value = null
    }
  }

  const removeToast = (id) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return {
    activeDialog,
    toasts,
    showError,
    showWarning,
    showConfirm,
    showSuccess,
    showInfoToast,
    closeDialog,
    removeToast
  }
})
