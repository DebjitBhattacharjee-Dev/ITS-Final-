import api from './frappe'

export async function loginApi(usr, pwd) {
  const response = await api.post('/api/method/its_ui_redesign.api.auth.login', { usr, pwd })
  return response.data.message
}

export async function logoutApi() {
  const response = await api.post('/api/method/its_ui_redesign.api.auth.logout')
  return response.data.message
}

export async function getLoggedUserApi() {
  const response = await api.get('/api/method/its_ui_redesign.api.auth.get_logged_user')
  return response.data.message
}
