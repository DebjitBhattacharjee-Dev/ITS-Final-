import api from './frappe'

export async function fetchDocList(doctype, fields = ['name', 'modified'], filters = {}, limit = 20) {
  const response = await api.get('/api/method/frappe.client.get_list', {
    params: {
      doctype,
      fields: JSON.stringify(fields),
      filters: JSON.stringify(filters),
      limit_page_length: limit
    }
  })
  return response.data.message || []
}

export async function fetchDashboardSummary() {
  const response = await api.get('/api/method/its_ui_redesign.api.dashboard.get_dashboard_summary')
  return response.data.message
}

export async function fetchProjects(status = null, search = null) {
  const response = await api.get('/api/method/its_ui_redesign.api.projects.get_projects', {
    params: { status, search }
  })
  return response.data.message || []
}

export async function fetchWarranties(warranty_type = null, search = null) {
  const response = await api.get('/api/method/its_ui_redesign.api.warranty.get_warranties', {
    params: { warranty_type, search }
  })
  return response.data.message || []
}
