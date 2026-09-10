import api, { getCsrfToken } from '../services/frappe'
export function useFrappe() {
  return {
    api,
    getCsrfToken
  }
}
