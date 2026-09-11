/**
 * Centralized utility for extracting meaningful human-readable Frappe/ERPNext error messages.
 */
export function extractFrappeErrorMessage(res = null, err = null) {
  // 1. Direct API response dictionary check
  if (res) {
    if (res.error) {
      if (typeof res.error === 'string') return res.error
      if (res.error.message) return res.error.message
    }
    if (res.message && typeof res.message === 'object') {
      if (res.message.error?.message) return res.message.error.message
      if (res.message.message && typeof res.message.message === 'string') return res.message.message
    }
  }

  // 2. Axios Error object check
  if (err) {
    const data = err.response?.data

    if (data) {
      // Check _server_messages (Frappe's default msgprint/throw JSON array)
      if (data._server_messages) {
        try {
          const rawMsgs = typeof data._server_messages === 'string' ? JSON.parse(data._server_messages) : data._server_messages
          if (Array.isArray(rawMsgs) && rawMsgs.length > 0) {
            const firstMsgObj = typeof rawMsgs[0] === 'string' ? JSON.parse(rawMsgs[0]) : rawMsgs[0]
            if (firstMsgObj && firstMsgObj.message) {
              // Strip HTML tags if any (e.g. <details><summary>...</summary></details>)
              const cleanMsg = String(firstMsgObj.message).replace(/<[^>]*>?/gm, '').trim()
              if (cleanMsg) return cleanMsg
            }
          }
        } catch (e) {
          // ignore json parse error and fallback
        }
      }

      // Check nested message.error.message
      if (data.message && typeof data.message === 'object' && data.message.error?.message) {
        return data.message.error.message
      }

      // Check direct error.message
      if (data.error && typeof data.error === 'object' && data.error.message) {
        return data.error.message
      }
      if (typeof data.error === 'string') {
        return data.error
      }

      // Check exception string (e.g. "frappe.exceptions.ValidationError: Root cannot have a parent cost center")
      if (data.exception && typeof data.exception === 'string') {
        const parts = data.exception.split(':')
        if (parts.length > 1) {
          const cleanExc = parts.slice(1).join(':').replace(/<[^>]*>?/gm, '').trim()
          if (cleanExc) return cleanExc
        }
      }

      // Check message string
      if (typeof data.message === 'string' && data.message.trim()) {
        return data.message.replace(/<[^>]*>?/gm, '').trim()
      }
    }

    if (err.message) {
      if (err.message.includes('Network Error')) return 'Network connection failure. Please check your internet connection.'
      if (err.message.includes('timeout')) return 'Request timed out while communicating with server.'
      return err.message
    }
  }

  return 'An unexpected error occurred while communicating with the server.'
}
