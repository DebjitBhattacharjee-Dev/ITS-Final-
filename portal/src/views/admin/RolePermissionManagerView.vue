<template>
  <div class="role-permission-container p-6 space-y-6">

    <!-- Page Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
          <span class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </span>
          Role Permission Manager
        </h1>
        <p class="text-sm text-slate-500 mt-1">Create roles, configure DocType permissions, and view assigned users</p>
      </div>
      <button @click="showNewRoleModal = true" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm flex items-center gap-2">
        <span class="text-lg leading-none">+</span> New Role
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">

      <!-- LEFT: Role List Panel -->
      <div class="lg:col-span-1 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b border-slate-200 bg-slate-50">
          <h2 class="text-xs font-bold text-slate-600 uppercase tracking-wider">Roles</h2>
          <input
            v-model="roleSearch"
            type="text"
            placeholder="Search roles..."
            class="mt-2 w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
        <div class="overflow-y-auto max-h-[650px] divide-y divide-slate-100">
          <div
            v-for="r in filteredRoles"
            :key="r.name"
            @click="selectRole(r)"
            :class="[
              'px-4 py-3 cursor-pointer transition-colors text-sm',
              selectedRole === r.name
                ? 'bg-indigo-50 text-indigo-700 font-semibold border-l-4 border-l-indigo-600'
                : 'text-slate-700 hover:bg-slate-50'
            ]"
          >
            <div class="font-medium truncate">{{ r.role_name }}</div>
            <div class="text-xs text-slate-400 mt-0.5">{{ r.desk_access ? 'Desk Access' : 'Portal Only' }}{{ r.disabled ? ' · Disabled' : '' }}</div>
          </div>
          <div v-if="filteredRoles.length === 0" class="p-4 text-sm text-slate-400 text-center">No roles found</div>
        </div>
      </div>

      <!-- RIGHT: Permission Config & Users Panel -->
      <div class="lg:col-span-3 space-y-5">

        <!-- No role selected state -->
        <div v-if="!selectedRole" class="bg-white rounded-xl border border-slate-200 shadow-sm p-12 text-center">
          <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
          </svg>
          <p class="text-slate-500 font-medium">Select a role from the sidebar to configure its permissions</p>
          <p class="text-xs text-slate-400 mt-1">Or create a new role using the button above</p>
        </div>

        <template v-else>
          <!-- Role Header -->
          <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-800">{{ selectedRole }}</h2>
              <p class="text-xs text-slate-500 mt-0.5">
                Native Frappe Role &mdash;
                <span class="font-semibold text-indigo-600">{{ assignedUsers.length }}</span> user(s) assigned
              </p>
            </div>
            <div class="flex items-center gap-3">
              <span :class="selectedRoleData?.disabled ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'"
                class="text-xs px-2.5 py-1 rounded-full font-medium">
                {{ selectedRoleData?.disabled ? 'Disabled' : 'Active' }}
              </span>
            </div>
          </div>

          <!-- DocType Selector Panel -->
          <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <div class="flex flex-col sm:flex-row sm:items-center gap-3">
              <div class="flex-1">
                <label class="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">Select DocType</label>
                <select
                  v-model="selectedDocType"
                  @change="fetchMatrix"
                  class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-800 focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none"
                >
                  <option value="">-- Select DocType --</option>
                  <option v-for="dt in keyDocTypes" :key="dt" :value="dt">{{ dt }}</option>
                </select>
              </div>
              <div v-if="selectedDocType" class="sm:self-end text-xs text-slate-400">
                Permissions map directly to native Frappe DocPerm rules
              </div>
            </div>
          </div>

          <!-- Permission Rules Table -->
          <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Permission Rules</h3>
              <button
                v-if="selectedDocType"
                @click="handleAddRow"
                class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
              >
                <span>+</span> Add Permission Row
              </button>
            </div>

            <div v-if="!selectedDocType" class="p-10 text-center text-slate-400 text-sm">
              Select a DocType above to view and configure permission rules for <strong>{{ selectedRole }}</strong>
            </div>

            <div v-else-if="matrixLoading" class="p-10 text-center text-slate-500 text-sm">
              Loading permission rules...
            </div>

            <div v-else>
              <div v-if="matrix.length === 0" class="p-8 text-center">
                <p class="text-sm text-slate-500 mb-3">No permission rules found for <strong>{{ selectedRole }}</strong> on <strong>{{ selectedDocType }}</strong></p>
                <button @click="handleAddRow" class="px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-lg hover:bg-indigo-700 transition-colors">
                  + Add Permission Row
                </button>
              </div>

              <div v-else class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-100/70 border-b border-slate-200 font-semibold text-slate-600 uppercase tracking-wider">
                      <th class="py-3 px-4 w-40">Document Type</th>
                      <th class="py-3 px-4 w-44">Role</th>
                      <th class="py-3 px-4">Permissions</th>
                      <th class="py-3 px-4 w-16 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-200">
                    <tr v-for="(rule, idx) in matrix" :key="rule.name || idx" class="hover:bg-slate-50/50 transition-colors align-top">
                      
                      <!-- Document Type -->
                      <td class="py-4 px-4 font-semibold text-slate-800">
                        {{ rule.parent || selectedDocType }}
                      </td>

                      <!-- Role -->
                      <td class="py-4 px-4 text-slate-700 font-medium">
                        {{ rule.role || selectedRole }}
                      </td>

                      <!-- Permissions Matrix (3 Columns) -->
                      <td class="py-4 px-4">
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-x-6 gap-y-2 text-slate-700">
                          
                          <!-- Column 1 -->
                          <div class="space-y-1.5">
                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.select"
                                @change="toggleField(rule, 'select', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span class="font-medium">Select</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.create"
                                @change="toggleField(rule, 'create', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Create</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.email"
                                @change="toggleField(rule, 'email', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Email</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.export"
                                @change="toggleField(rule, 'export', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Export</span>
                            </label>

                            <label v-if="rule.is_submittable" class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none text-indigo-700">
                              <input
                                type="checkbox"
                                :checked="!!rule.submit"
                                @change="toggleField(rule, 'submit', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span class="font-semibold">Submit</span>
                            </label>
                          </div>

                          <!-- Column 2 -->
                          <div class="space-y-1.5">
                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.read"
                                @change="toggleField(rule, 'read', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span class="font-semibold text-slate-900">Read</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.delete"
                                @change="toggleField(rule, 'delete', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Delete</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.report"
                                @change="toggleField(rule, 'report', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Report</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.share"
                                @change="toggleField(rule, 'share', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Share</span>
                            </label>

                            <label v-if="rule.is_submittable" class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none text-indigo-700">
                              <input
                                type="checkbox"
                                :checked="!!rule.cancel"
                                @change="toggleField(rule, 'cancel', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Cancel</span>
                            </label>
                          </div>

                          <!-- Column 3 -->
                          <div class="space-y-1.5">
                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.write"
                                @change="toggleField(rule, 'write', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span class="font-medium">Write</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.print"
                                @change="toggleField(rule, 'print', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Print</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.import"
                                @change="toggleField(rule, 'import', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Import</span>
                            </label>

                            <label class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.if_owner"
                                @change="toggleField(rule, 'if_owner', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span class="italic text-slate-600">Only If Creator</span>
                            </label>

                            <label v-if="rule.is_submittable" class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none text-indigo-700">
                              <input
                                type="checkbox"
                                :checked="!!rule.amend"
                                @change="toggleField(rule, 'amend', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Amend</span>
                            </label>

                            <label v-if="rule.set_user_permissions !== undefined" class="flex items-center gap-2 cursor-pointer hover:text-slate-900 select-none">
                              <input
                                type="checkbox"
                                :checked="!!rule.set_user_permissions"
                                @change="toggleField(rule, 'set_user_permissions', $event.target.checked)"
                                class="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                              />
                              <span>Set User Permissions</span>
                            </label>
                          </div>

                        </div>
                      </td>

                      <!-- Action (Trash button) -->
                      <td class="py-4 px-4 text-center">
                        <button
                          @click="handleDeleteRule(rule)"
                          class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                          title="Delete Permission Rule"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Assigned Users Panel -->
          <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Users With This Role ({{ assignedUsers.length }})
              </h3>
              <router-link to="/portal/administration/users" class="text-xs text-indigo-600 hover:underline font-semibold flex items-center gap-1">
                Manage Users &rarr;
              </router-link>
            </div>

            <div v-if="usersLoading" class="p-6 text-center text-xs text-slate-400">
              Loading users...
            </div>
            <div v-else-if="assignedUsers.length === 0" class="p-6 text-center text-xs text-slate-400">
              No users currently assigned to <strong>{{ selectedRole }}</strong>
            </div>
            <ul v-else class="divide-y divide-slate-100 max-h-60 overflow-y-auto">
              <li v-for="u in assignedUsers" :key="u.name" class="p-3.5 flex items-center justify-between hover:bg-slate-50 text-xs">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center font-bold uppercase text-xs">
                    {{ (u.full_name || u.name || '?').charAt(0) }}
                  </div>
                  <div>
                    <div class="font-semibold text-slate-800">{{ u.full_name || u.name }}</div>
                    <div class="text-slate-400 text-[11px]">{{ u.email || u.name }}</div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span :class="u.enabled ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'"
                    class="text-[11px] px-2 py-0.5 rounded-full font-medium">
                    {{ u.enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                  <router-link :to="`/portal/administration/users/${encodeURIComponent(u.name)}`"
                    class="text-indigo-600 hover:underline font-medium ml-1">
                    Open &rarr;
                  </router-link>
                </div>
              </li>
            </ul>
          </div>

        </template>
      </div>
    </div>

    <!-- New Role Modal -->
    <div v-if="showNewRoleModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
        <h3 class="text-base font-bold text-slate-800 border-b pb-2">Create Native Frappe Role</h3>

        <div class="space-y-3 text-sm">
          <div>
            <label class="block font-medium text-slate-700 mb-1">Role Name *</label>
            <input
              v-model="newRoleName"
              type="text"
              placeholder="e.g. UAT-ITS-Site Engineer"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
          <div class="flex items-center gap-2 pt-1">
            <input v-model="newRoleDeskAccess" type="checkbox" id="deskAccessChk" class="rounded text-indigo-600" />
            <label for="deskAccessChk" class="text-slate-700 cursor-pointer">Desk Access</label>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="newRoleDisabled" type="checkbox" id="disabledChk" class="rounded text-indigo-600" />
            <label for="disabledChk" class="text-slate-700 cursor-pointer">Disabled</label>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t pt-3">
          <button @click="showNewRoleModal = false; newRoleName = ''" class="px-4 py-2 border rounded-lg text-slate-600 hover:bg-slate-50 transition-colors">Cancel</button>
          <button @click="handleCreateRole" :disabled="creatingRole" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors">
            {{ creatingRole ? 'Creating...' : 'Create Role' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getRoles,
  saveRole,
  getRolePermissionMatrix,
  updateRolePermission,
  addRolePermissionRule,
  deleteRolePermissionRule,
  getRoleUsers
} from '../../services/admin'
import { useNotificationStore } from '../../stores/notification'

const notificationStore = useNotificationStore()
const roles = ref([])
const roleSearch = ref('')
const selectedRole = ref('')
const selectedRoleData = ref(null)
const selectedDocType = ref('')
const matrix = ref([])
const matrixLoading = ref(false)
const assignedUsers = ref([])
const usersLoading = ref(false)

const showNewRoleModal = ref(false)
const newRoleName = ref('')
const newRoleDeskAccess = ref(true)
const newRoleDisabled = ref(false)
const creatingRole = ref(false)

const keyDocTypes = [
  "Employee", "Project", "Sales Order", "Purchase Order", "Sales Invoice", "Purchase Invoice",
  "Payment Entry", "Item", "Warehouse", "Work Order", "Asset",
  "Project Contract", "Project Variation", "Project Warranty", "Factory Acceptance Test",
  "Snag List", "Customer", "Supplier", "Quotation", "Request for Quotation",
  "Material Request", "Stock Entry", "Salary Slip", "Leave Application", "Attendance",
  "Timesheet", "Expense Claim", "Budget", "Cost Center", "User", "Role"
]

const filteredRoles = computed(() => {
  const q = roleSearch.value.trim().toLowerCase()
  if (!q) return roles.value
  return roles.value.filter(r =>
    r.role_name.toLowerCase().includes(q) || r.name.toLowerCase().includes(q)
  )
})

function notifyError(err, fallbackTitle = 'Error') {
  const status = err.response?.status
  if (status === 403) {
    notificationStore.showError('Permission Denied', 'You do not have administrator permissions to access or modify roles.')
    return
  }
  const msg = err.response?.data?.error?.message || err.response?.data?.message || err.message || 'An unexpected error occurred.'
  notificationStore.showError(fallbackTitle, msg)
}

async function loadRoles() {
  try {
    const res = await getRoles()
    roles.value = (res.data || res || []).filter(r => !['All', 'Guest', 'Administrator'].includes(r.name))
  } catch (err) {
    console.error('Error loading roles:', err)
    notifyError(err, 'Role Loading Failed')
  }
}

async function selectRole(r) {
  selectedRole.value = r.name
  selectedRoleData.value = r
  selectedDocType.value = ''
  matrix.value = []
  assignedUsers.value = []
  await loadRoleUsers()
}

async function loadRoleUsers() {
  if (!selectedRole.value) return
  usersLoading.value = true
  try {
    const res = await getRoleUsers(selectedRole.value)
    assignedUsers.value = res.data || res || []
  } catch (err) {
    console.error('Error loading role users:', err)
    notifyError(err, 'Failed to Load Assigned Users')
  } finally {
    usersLoading.value = false
  }
}

async function fetchMatrix() {
  if (!selectedRole.value || !selectedDocType.value) {
    matrix.value = []
    return
  }
  matrixLoading.value = true
  try {
    const res = await getRolePermissionMatrix(selectedDocType.value, selectedRole.value)
    matrix.value = res.data || res || []
  } catch (err) {
    console.error('Error fetching matrix:', err)
    notifyError(err, 'Failed to Load Permission Matrix')
  } finally {
    matrixLoading.value = false
  }
}

async function toggleField(rule, pType, checked) {
  try {
    const permLevel = rule.permlevel !== undefined ? rule.permlevel : 0
    const ifOwner = rule.if_owner !== undefined ? rule.if_owner : 0
    await updateRolePermission(
      rule.parent || selectedDocType.value,
      rule.role || selectedRole.value,
      permLevel,
      pType,
      checked ? 1 : 0,
      ifOwner
    )
    rule[pType] = checked ? 1 : 0
    notificationStore.showSuccess(`Permission "${pType}" updated`)
  } catch (err) {
    notifyError(err, 'Permission Update Failed')
    await fetchMatrix()
  }
}

async function handleAddRow() {
  if (!selectedDocType.value || !selectedRole.value) return
  try {
    const res = await addRolePermissionRule(selectedDocType.value, selectedRole.value, 0)
    if (res && res.success === false) {
      notificationStore.showError('Add Rule Error', res.error?.message || 'Could not add rule')
    } else {
      notificationStore.showSuccess('Permission row added')
      await fetchMatrix()
    }
  } catch (err) {
    notifyError(err, 'Failed to Add Permission Row')
  }
}

async function handleDeleteRule(rule) {
  const confirmed = await notificationStore.showConfirm(
    'Delete Permission Rule',
    `Are you sure you want to delete permission rule for role "${rule.role || selectedRole.value}" on "${rule.parent || selectedDocType.value}"?`
  )
  if (!confirmed) return

  try {
    const permLevel = rule.permlevel !== undefined ? rule.permlevel : 0
    const ifOwner = rule.if_owner !== undefined ? rule.if_owner : 0
    await deleteRolePermissionRule(
      rule.parent || selectedDocType.value,
      rule.role || selectedRole.value,
      permLevel,
      ifOwner
    )
    notificationStore.showSuccess('Permission rule deleted')
    await fetchMatrix()
  } catch (err) {
    notifyError(err, 'Failed to Delete Permission Rule')
  }
}

async function handleCreateRole() {
  if (!newRoleName.value.trim()) {
    notificationStore.showWarning('Validation Error', 'Role Name is required')
    return
  }
  creatingRole.value = true
  try {
    await saveRole(newRoleName.value.trim(), newRoleDeskAccess.value ? 1 : 0, newRoleDisabled.value ? 1 : 0)
    showNewRoleModal.value = false
    const name = newRoleName.value.trim()
    newRoleName.value = ''
    newRoleDeskAccess.value = true
    newRoleDisabled.value = false
    notificationStore.showSuccess(`Role "${name}" created successfully`)
    await loadRoles()
    const created = roles.value.find(r => r.name === name || r.role_name === name)
    if (created) await selectRole(created)
  } catch (err) {
    notifyError(err, 'Failed to Create Role')
  } finally {
    creatingRole.value = false
  }
}

onMounted(async () => {
  await loadRoles()
})
</script>
