import api from "./frappe"

export async function getUsers(options = {}) {
  const { search = "", role = "", enabled = "", userType = "", page = 1, pageLength = 20 } = options
  const response = await api.get("/api/method/its_ui_redesign.api.admin.get_users", {
    params: { search, role, enabled, user_type: userType, page, page_length: pageLength }
  })
  return response.data.message || response.data
}

export async function getUserDetail(userId) {
  const response = await api.get("/api/method/its_ui_redesign.api.admin.get_user_detail", {
    params: { user_id: userId }
  })
  return response.data.message || response.data
}

export async function saveUser(userData, roles = null, isNew = false) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.save_user", {
    user_data: JSON.stringify(userData),
    roles: roles ? JSON.stringify(roles) : null,
    is_new: isNew ? 1 : 0
  })
  return response.data.message || response.data
}

export async function sendPasswordResetEmail(userId) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.send_password_reset_email", {
    user_id: userId
  })
  return response.data.message || response.data
}

export async function setUserPassword(userId, newPassword) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.set_user_password", {
    user_id: userId,
    new_password: newPassword
  })
  return response.data.message || response.data
}

export async function setUserEnabled(userId, enabled) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.set_user_enabled", {
    user_id: userId,
    enabled
  })
  return response.data.message || response.data
}

export async function addUserPermission(userId, allowDocType, forValue, isDefault = 0, applicableFor = null, hideDescendants = 0) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.add_user_permission", {
    user_id: userId,
    allow_doctype: allowDocType,
    for_value: forValue,
    is_default: isDefault ? 1 : 0,
    applicable_for: applicableFor || null,
    hide_descendants: hideDescendants ? 1 : 0
  })
  return response.data.message || response.data
}

export async function deleteUserPermission(userPermissionName) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.delete_user_permission", {
    user_permission_name: userPermissionName
  })
  return response.data.message || response.data
}

export async function getRoles() {
  const response = await api.get("/api/method/its_ui_redesign.api.admin.get_roles")
  return response.data.message || response.data
}

export async function saveRole(roleName, deskAccess = 1, disabled = 0) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.save_role", {
    role_name: roleName,
    desk_access: deskAccess ? 1 : 0,
    disabled: disabled ? 1 : 0
  })
  return response.data.message || response.data
}

export async function getRoleUsers(roleName) {
  const response = await api.get("/api/method/its_ui_redesign.api.admin.get_role_users", {
    params: { role_name: roleName }
  })
  return response.data.message || response.data
}

export async function getRolePermissionMatrix(docType = null, role = null) {
  const response = await api.get("/api/method/its_ui_redesign.api.admin.get_role_permission_matrix", {
    params: { doctype: docType, role }
  })
  return response.data.message || response.data
}

export async function updateRolePermission(docType, role, permLevel = 0, pType = "read", value = 0, ifOwner = 0) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.update_role_permission", {
    doctype: docType,
    role,
    permlevel: permLevel,
    ptype: pType,
    value: value ? 1 : 0,
    if_owner: ifOwner ? 1 : 0
  })
  return response.data.message || response.data
}

export async function addRolePermissionRule(docType, role, permLevel = 0) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.add_role_permission_rule", {
    doctype: docType,
    role,
    permlevel: permLevel
  })
  return response.data.message || response.data
}

export async function deleteRolePermissionRule(docType, role, permLevel = 0, ifOwner = 0) {
  const response = await api.post("/api/method/its_ui_redesign.api.admin.delete_role_permission_rule", {
    doctype: docType,
    role,
    permlevel: permLevel,
    if_owner: ifOwner ? 1 : 0
  })
  return response.data.message || response.data
}

