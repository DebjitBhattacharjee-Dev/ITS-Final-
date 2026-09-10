import axios from 'axios'

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

export function getCsrfToken() {
  return window.csrf_token || window.frappe?.csrf_token || getCookie('csrf_token') || ''
}

const api = axios.create({
  baseURL: '',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    config.headers['X-Frappe-CSRF-Token'] = csrfToken
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (window.location.pathname !== '/portal-access') {
        window.location.href = '/portal-access'
      }
    }
    return Promise.reject(error)
  }
)

export default api
