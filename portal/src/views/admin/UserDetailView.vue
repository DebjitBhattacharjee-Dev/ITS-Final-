<template>
  <div class="user-detail-container p-6 space-y-6">
    <!-- Back Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div class="flex items-center gap-4">
        <router-link to="/portal/administration/users" class="p-2 text-slate-400 hover:text-slate-700 bg-slate-100 rounded-lg transition-colors cursor-pointer">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>

        <div v-if="user">
          <h1 class="text-xl font-bold text-slate-800 flex items-center gap-3">
            {{ user.full_name || (user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.email) }}
            <span :class="user.enabled ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'" class="px-2.5 py-0.5 rounded-full text-xs border font-medium">
              ● {{ user.enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </h1>
          <p class="text-xs text-slate-500 mt-0.5 font-mono">{{ user.email }}</p>
        </div>
        <div v-else class="text-sm text-slate-400">Loading user details...</div>
      </div>

      <div class="flex items-center gap-3">
        <button 
          @click="saveUserChanges" 
          :disabled="saving || !user" 
          class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm cursor-pointer flex items-center gap-2"
        >
          <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ saving ? 'Saving Changes...' : 'Save Configuration' }}
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex border-b border-slate-200 bg-white px-6 pt-3 rounded-xl border shadow-sm overflow-x-auto">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        class="px-5 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap cursor-pointer"
        :class="activeTab === tab.id ? 'border-indigo-600 text-indigo-600 font-semibold' : 'border-transparent text-slate-500 hover:text-slate-800'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- TAB 1: USER INFORMATION -->
    <div v-if="activeTab === 'info'" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div class="border-b pb-3 flex justify-between items-center">
        <div>
          <h3 class="text-base font-semibold text-slate-800">Native Frappe User Profile</h3>
          <p class="text-xs text-slate-500 mt-0.5">Primary identity and account configuration stored in native User DocType</p>
        </div>
      </div>

      <div v-if="user" class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
        <div>
          <label class="block font-medium text-slate-700 mb-1">Email / Username (Identity) *</label>
          <input :value="user.email" disabled class="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-slate-500 font-mono cursor-not-allowed" />
          <p class="text-xs text-slate-400 mt-1">Unique identifier in Frappe authentication system.</p>
        </div>

        <div>
          <label class="block font-medium text-slate-700 mb-1">First Name *</label>
          <input v-model="user.first_name" type="text" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
        </div>

        <div>
          <label class="block font-medium text-slate-700 mb-1">Middle Name</label>
          <input v-model="user.middle_name" type="text" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
        </div>

        <div>
          <label class="block font-medium text-slate-700 mb-1">Last Name</label>
          <input v-model="user.last_name" type="text" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
        </div>

        <div>
          <label class="block font-medium text-slate-700 mb-1">User Type</label>
          <select v-model="user.user_type" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            <option value="System User">System User</option>
            <option value="Website User">Website User</option>
          </select>
        </div>

        <div class="flex items-center gap-3 pt-6">
          <input v-model="user.enabled" type="checkbox" id="userEnabledCheck" class="w-4 h-4 rounded text-indigo-600" />
          <label for="userEnabledCheck" class="font-medium text-slate-700 cursor-pointer">Enable User Account</label>
        </div>

        <div class="md:col-span-2 border-t pt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-500">
          <div><span class="font-semibold text-slate-700">Account Created:</span> {{ user.creation || '—' }}</div>
          <div><span class="font-semibold text-slate-700">Last Active / Login:</span> {{ user.last_active || user.last_login || 'Never' }}</div>
        </div>
      </div>
    </div>

    <!-- TAB 2: ROLE ASSIGNMENTS -->
    <div v-if="activeTab === 'roles'" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div class="flex justify-between items-center border-b pb-3">
        <div>
          <h3 class="text-base font-semibold text-slate-800">Assigned Frappe Roles</h3>
          <p class="text-xs text-slate-500 mt-0.5">Direct native role assignments stored in User's `Has Role` child table</p>
        </div>
        <div class="text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
          {{ assignedRoles.length }} Roles Selected
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <label 
          v-for="r in allRoles" 
          :key="r.name"
          class="flex items-center gap-3 p-3 border rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
          :class="assignedRoles.includes(r.name) ? 'border-indigo-300 bg-indigo-50/50' : 'border-slate-200'"
        >
          <input 
            type="checkbox" 
            :value="r.name" 
            v-model="assignedRoles"
            class="w-4 h-4 rounded text-indigo-600" 
          />
          <div>
            <div class="text-sm font-medium text-slate-800">{{ r.role_name || r.name }}</div>
            <div class="text-xs text-slate-400">{{ r.desk_access ? 'Desk & Portal Access' : 'Portal Access' }}</div>
          </div>
        </label>
      </div>
    </div>

    <!-- TAB 3: USER PERMISSIONS -->
    <div v-if="activeTab === 'permissions'" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div class="flex justify-between items-center border-b pb-3">
        <div>
          <h3 class="text-base font-semibold text-slate-800">Native Frappe User Permissions</h3>
          <p class="text-xs text-slate-500 mt-0.5">Record-level scoping restrictions enforced natively in ERPNext & Custom Portal</p>
        </div>
        <button @click="showAddPermissionModal = true" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm cursor-pointer">
          + Add User Permission
        </button>
      </div>

      <table v-if="userPermissions.length > 0" class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase">
            <th class="py-3 px-4">Allow DocType</th>
            <th class="py-3 px-4">For Value (ID)</th>
            <th class="py-3 px-4">Default</th>
            <th class="py-3 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="up in userPermissions" :key="up.name">
            <td class="py-3 px-4 font-medium text-slate-800">{{ up.allow }}</td>
            <td class="py-3 px-4 font-mono text-xs text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded border border-indigo-100 inline-block my-1">{{ up.for_value }}</td>
            <td class="py-3 px-4">
              <span v-if="up.is_default" class="text-xs bg-emerald-100 text-emerald-800 font-medium px-2 py-0.5 rounded">Default</span>
            </td>
            <td class="py-3 px-4 text-right">
              <button @click="handleRemovePermission(up.name)" class="text-xs text-rose-600 hover:text-rose-800 font-semibold cursor-pointer">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="p-8 text-center text-slate-400 text-sm">No record-level User Permissions currently configured for this user.</div>
    </div>

    <!-- TAB 4: SECURITY / PASSWORD MANAGEMENT -->
    <div v-if="activeTab === 'security'" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div class="border-b pb-3">
        <h3 class="text-base font-semibold text-slate-800">Password Management & Security</h3>
        <p class="text-xs text-slate-500 mt-0.5">Secure password reset instructions and password policies powered by native Frappe authentication</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Send Password Reset Email -->
        <div class="p-5 border border-slate-200 rounded-xl bg-slate-50/50 space-y-3">
          <div class="flex items-center gap-3 text-slate-800 font-semibold">
            <span class="p-2 bg-indigo-100 text-indigo-700 rounded-lg">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 002-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </span>
            Send Password Setup / Reset Email
          </div>
          <p class="text-xs text-slate-600">
            Sends a secure password setup link to <strong class="text-slate-900 font-mono">{{ user?.email }}</strong>. The user can click the link to choose their own password securely.
          </p>
          <button 
            @click="handleSendPasswordReset"
            :disabled="sendingMail"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm cursor-pointer flex items-center gap-2"
          >
            <span v-if="sendingMail" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            {{ sendingMail ? 'Sending Email...' : 'Send Password Setup Email' }}
          </button>
        </div>

        <!-- Administrator Set Password -->
        <div class="p-5 border border-slate-200 rounded-xl bg-slate-50/50 space-y-3">
          <div class="flex items-center gap-3 text-slate-800 font-semibold">
            <span class="p-2 bg-amber-100 text-amber-700 rounded-lg">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </span>
            Set New Password Directly
          </div>
          <p class="text-xs text-slate-600">
            Administratively update the password for <strong class="text-slate-900 font-mono">{{ user?.email }}</strong>. Passwords are securely hashed by Frappe authentication.
          </p>
          <button 
            @click="showSetPasswordModal = true"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm cursor-pointer"
          >
            Set New Password
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 5: EFFECTIVE ACCESS MATRIX -->
    <div v-if="activeTab === 'effective'" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div class="border-b pb-3">
        <h3 class="text-base font-semibold text-slate-800">Dynamic Effective Access Matrix</h3>
        <p class="text-xs text-slate-500 mt-0.5">Informational access summary computed dynamically from assigned native Frappe Roles</p>
      </div>

      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase">
            <th class="py-3 px-4">DocType</th>
            <th class="py-3 px-4 text-center">Read</th>
            <th class="py-3 px-4 text-center">Create</th>
            <th class="py-3 px-4 text-center">Write</th>
            <th class="py-3 px-4 text-center">Delete</th>
            <th class="py-3 px-4 text-center">Submit</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="(perms, dt) in effectiveAccess" :key="dt">
            <td class="py-3 px-4 font-medium text-slate-800">{{ dt }}</td>
            <td class="py-3 px-4 text-center"><span :class="perms.read ? 'text-emerald-600 font-bold' : 'text-slate-300'">{{ perms.read ? '✓' : '✕' }}</span></td>
            <td class="py-3 px-4 text-center"><span :class="perms.create ? 'text-emerald-600 font-bold' : 'text-slate-300'">{{ perms.create ? '✓' : '✕' }}</span></td>
            <td class="py-3 px-4 text-center"><span :class="perms.write ? 'text-emerald-600 font-bold' : 'text-slate-300'">{{ perms.write ? '✓' : '✕' }}</span></td>
            <td class="py-3 px-4 text-center"><span :class="perms.delete ? 'text-emerald-600 font-bold' : 'text-slate-300'">{{ perms.delete ? '✓' : '✕' }}</span></td>
            <td class="py-3 px-4 text-center"><span :class="perms.submit ? 'text-emerald-600 font-bold' : 'text-slate-300'">{{ perms.submit ? '✓' : '✕' }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add User Permission Modal -->
    <div v-if="showAddPermissionModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
        <h3 class="text-base font-bold text-slate-800 border-b pb-2">Add Native User Permission</h3>

        <div class="space-y-3 text-sm">
          <div>
            <label class="block font-medium text-slate-700 mb-1">Allow DocType *</label>
            <select v-model="newPerm.allow" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
              <option value="Project">Project</option>
              <option value="Company">Company</option>
              <option value="Warehouse">Warehouse</option>
              <option value="Customer">Customer</option>
              <option value="Supplier">Supplier</option>
              <option value="Cost Center">Cost Center</option>
              <option value="Branch">Branch</option>
            </select>
          </div>

          <div>
            <label class="block font-medium text-slate-700 mb-1">For Value (ID / Name) *</label>
            <input v-model="newPerm.for_value" type="text" placeholder="e.g. PROJ-001 or Main Warehouse" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
          </div>

          <div class="flex items-center gap-2 pt-2">
            <input v-model="newPerm.is_default" type="checkbox" id="isDefaultCheck" class="rounded text-indigo-600" />
            <label for="isDefaultCheck" class="text-slate-700 cursor-pointer">Set as Default Permission</label>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t pt-3">
          <button @click="showAddPermissionModal = false" class="px-4 py-2 border rounded-lg text-slate-600 font-medium">Cancel</button>
          <button @click="handleAddPermission" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium shadow-sm">Add Permission</button>
        </div>
      </div>
    </div>

    <!-- Set Password Modal -->
    <div v-if="showSetPasswordModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
        <div class="flex justify-between items-center border-b pb-2">
          <h3 class="text-base font-bold text-slate-800">Set New User Password</h3>
          <button @click="showSetPasswordModal = false" class="text-slate-400 hover:text-slate-600 font-bold">✕</button>
        </div>

        <form @submit.prevent="handleSetPassword" class="space-y-4 text-sm">
          <div>
            <label class="block font-medium text-slate-700 mb-1">New Password *</label>
            <input 
              v-model="newPassword" 
              type="password" 
              required
              placeholder="••••••••" 
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" 
            />
          </div>

          <div>
            <label class="block font-medium text-slate-700 mb-1">Confirm New Password *</label>
            <input 
              v-model="confirmPassword" 
              type="password" 
              required
              placeholder="••••••••" 
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" 
            />
          </div>

          <div class="flex justify-end gap-3 border-t pt-3">
            <button type="button" @click="showSetPasswordModal = false" class="px-4 py-2 border rounded-lg text-slate-600 font-medium">Cancel</button>
            <button type="submit" :disabled="settingPassword" class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-black font-medium shadow-sm flex items-center gap-2">
              <span v-if="settingPassword" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              {{ settingPassword ? 'Updating...' : 'Set Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getUserDetail, saveUser, getRoles, addUserPermission, deleteUserPermission, sendPasswordResetEmail, setUserPassword } from '../../services/admin'
import { useNotificationStore } from '../../stores/notification'

const route = useRoute()
const userId = decodeURIComponent(route.params.user || route.params.id || '')
const notification = useNotificationStore()

const user = ref(null)
const assignedRoles = ref([])
const allRoles = ref([])
const userPermissions = ref([])
const effectiveAccess = ref({})

const saving = ref(false)
const sendingMail = ref(false)
const settingPassword = ref(false)

const showAddPermissionModal = ref(false)
const showSetPasswordModal = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')

const activeTab = ref('info')
const tabs = [
  { id: 'info', label: 'User Information' },
  { id: 'roles', label: 'Role Assignments' },
  { id: 'permissions', label: 'User Permissions' },
  { id: 'security', label: 'Security & Password' },
  { id: 'effective', label: 'Effective Access' }
]

const newPerm = ref({
  allow: 'Project',
  for_value: '',
  is_default: false
})

async function loadData() {
  try {
    const rolesRes = await getRoles()
    allRoles.value = rolesRes.data || rolesRes || []

    const res = await getUserDetail(userId)
    const data = res.data || res
    if (data) {
      user.value = data.user
      assignedRoles.value = data.roles || []
      userPermissions.value = data.user_permissions || []
      effectiveAccess.value = data.effective_access || {}
    }
  } catch (err) {
    console.error('Error loading user details:', err)
    notification.showError('Error Loading User', err.message || 'Failed to load user detail')
  }
}

async function saveUserChanges() {
  if (!user.value) return
  saving.value = true
  try {
    await saveUser(user.value, assignedRoles.value)
    await loadData()
    notification.showSuccess('User configuration and assigned roles saved successfully.', 'Saved')
  } catch (err) {
    notification.showError('Error Saving User', err.message || 'Failed to save changes')
  } finally {
    saving.value = false
  }
}

async function handleAddPermission() {
  if (!newPerm.value.for_value) {
    notification.showWarning('Missing Value', 'Please enter a target value (e.g. Project ID).')
    return
  }
  try {
    await addUserPermission(userId, newPerm.value.allow, newPerm.value.for_value, newPerm.value.is_default ? 1 : 0)
    showAddPermissionModal.value = false
    newPerm.value.for_value = ''
    await loadData()
    notification.showSuccess('User Permission added successfully.', 'Permission Added')
  } catch (err) {
    notification.showError('Error Adding Permission', err.message || 'Failed to add User Permission')
  }
}

async function handleRemovePermission(permName) {
  const confirmed = await notification.showConfirm('Remove User Permission', 'Are you sure you want to remove this record-level User Permission?')
  if (!confirmed) return
  try {
    await deleteUserPermission(permName)
    await loadData()
    notification.showSuccess('User Permission removed.', 'Permission Removed')
  } catch (err) {
    notification.showError('Error Removing Permission', err.message || 'Failed to remove User Permission')
  }
}

async function handleSendPasswordReset() {
  if (!user.value || !user.value.email) return
  sendingMail.value = true
  try {
    const res = await sendPasswordResetEmail(user.value.email)
    if (res.success || res.status === 'success') {
      notification.showSuccess(`Password setup email sent to ${user.value.email}.`, 'Email Sent')
    } else {
      notification.showWarning('Email Result', res.message || 'Email action completed.')
    }
  } catch (err) {
    notification.showError('Email Error', err.message || 'Failed to send password setup email')
  } finally {
    sendingMail.value = false
  }
}

async function handleSetPassword() {
  if (!newPassword.value) {
    notification.showWarning('Password Missing', 'Please enter a new password.')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    notification.showWarning('Password Mismatch', 'The passwords entered do not match.')
    return
  }

  settingPassword.value = true
  try {
    await setUserPassword(userId, newPassword.value)
    showSetPasswordModal.value = false
    newPassword.value = ''
    confirmPassword.value = ''
    notification.showSuccess(`Password updated successfully for ${user.value.email}.`, 'Password Updated')
  } catch (err) {
    notification.showError('Password Error', err.message || 'Failed to set password')
  } finally {
    settingPassword.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

