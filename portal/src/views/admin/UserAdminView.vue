<template>
  <div class="user-admin-container p-6 space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
          <span class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </span>
          User Management & User Creation
        </h1>
        <p class="text-sm text-slate-500 mt-1">Manage native Frappe users, roles, and permissions directly</p>
      </div>

      <div class="flex items-center gap-3">
        <button 
          @click="openCreateModal"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg transition-colors shadow-sm cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          + New User
        </button>
      </div>
    </div>

    <!-- Filters & Search -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
      <div class="relative w-full md:w-80">
        <input 
          v-model="searchText"
          @input="debounceSearch"
          type="text"
          placeholder="Search by name, email, user ID..."
          class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
        />
        <svg class="w-4 h-4 text-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
        <!-- Status Filter -->
        <div class="flex items-center gap-1 text-xs text-slate-500 font-medium">
          <span>Enabled:</span>
          <select 
            v-model="statusFilter"
            @change="applyFilters"
            class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">Any</option>
            <option value="1">Enabled Only</option>
            <option value="0">Disabled Only</option>
          </select>
        </div>

        <!-- User Type Filter -->
        <div class="flex items-center gap-1 text-xs text-slate-500 font-medium">
          <span>Type:</span>
          <select 
            v-model="userTypeFilter"
            @change="applyFilters"
            class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">Any</option>
            <option value="System User">System User</option>
            <option value="Website User">Website User</option>
          </select>
        </div>

        <!-- Role Filter -->
        <div class="flex items-center gap-1 text-xs text-slate-500 font-medium">
          <span>Role:</span>
          <select 
            v-model="roleFilter"
            @change="applyFilters"
            class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer max-w-[160px]"
          >
            <option value="">Any Role</option>
            <option v-for="r in availableRoles" :key="r.name" :value="r.name">{{ r.role_name || r.name }}</option>
          </select>
        </div>

        <button 
          v-if="searchText || statusFilter || userTypeFilter || roleFilter"
          @click="clearFilters"
          class="px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 rounded-lg transition-colors cursor-pointer"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-slate-500 flex items-center justify-center gap-2">
        <svg class="w-5 h-5 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading native Frappe users...
      </div>

      <div v-else-if="users.length === 0" class="p-12 text-center text-slate-500">
        <svg class="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        No matching Frappe users found.
      </div>

      <table v-else class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            <th class="py-3.5 px-4">Email / User ID</th>
            <th class="py-3.5 px-4">Full Name</th>
            <th class="py-3.5 px-4">Status</th>
            <th class="py-3.5 px-4">User Type</th>
            <th class="py-3.5 px-4">Assigned Roles</th>
            <th class="py-3.5 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 text-sm">
          <tr v-for="u in users" :key="u.name" class="hover:bg-slate-50/80 transition-colors">
            <!-- Email / User ID -->
            <td class="py-3.5 px-4 font-medium text-slate-900">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-xs shrink-0">
                  {{ (u.first_name || u.email || 'U')[0].toUpperCase() }}
                </div>
                <div class="truncate max-w-[200px]" :title="u.email">
                  {{ u.email }}
                </div>
              </div>
            </td>

            <!-- Full Name -->
            <td class="py-3.5 px-4 text-slate-700">
              {{ u.full_name || (u.first_name ? `${u.first_name} ${u.last_name || ''}`.trim() : '—') }}
            </td>

            <!-- Status -->
            <td class="py-3.5 px-4">
              <span 
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="u.enabled ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="u.enabled ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                {{ u.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </td>

            <!-- User Type -->
            <td class="py-3.5 px-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                {{ u.user_type || 'System User' }}
              </span>
            </td>

            <!-- Roles -->
            <td class="py-3.5 px-4">
              <div class="flex flex-wrap gap-1 items-center max-w-[240px]">
                <span 
                  v-for="r in (u.roles || []).slice(0, 2)" 
                  :key="r"
                  class="inline-block px-2 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded text-xs font-medium"
                >
                  {{ r }}
                </span>
                <span v-if="(u.roles || []).length > 2" class="text-xs text-slate-400 font-medium">
                  +{{ u.roles.length - 2 }} more
                </span>
                <span v-if="!u.roles || u.roles.length === 0" class="text-xs text-slate-400">
                  No roles
                </span>
              </div>
            </td>

            <!-- Action -->
            <td class="py-3.5 px-4 text-right">
              <router-link 
                :to="`/portal/administration/users/${encodeURIComponent(u.name)}`"
                class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors border border-indigo-200"
              >
                Open User
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Server-side Pagination Footer -->
      <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-600">
        <div>
          Showing page <span class="font-semibold text-slate-800">{{ page }}</span> — 
          Total <span class="font-semibold text-slate-800">{{ totalCount }}</span> user records
        </div>

        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-xs">Page size:</span>
            <select v-model="pageLength" @change="applyFilters" class="px-2 py-1 bg-white border border-slate-200 rounded text-xs">
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>

          <div class="flex items-center gap-1">
            <button 
              @click="changePage(page - 1)" 
              :disabled="page <= 1"
              class="px-3 py-1 bg-white border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-medium"
            >
              Previous
            </button>
            <button 
              @click="changePage(page + 1)" 
              :disabled="page * pageLength >= totalCount"
              class="px-3 py-1 bg-white border border-slate-200 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-medium"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div class="bg-white rounded-xl max-w-xl w-full p-6 shadow-xl border border-slate-200 space-y-5 my-8">
        <div class="flex justify-between items-center border-b pb-3">
          <div>
            <h3 class="text-lg font-bold text-slate-800">Create Native Frappe User</h3>
            <p class="text-xs text-slate-500 mt-0.5">User will be created in native Frappe User DocType & sent a secure password setup link</p>
          </div>
          <button @click="showCreateModal = false" class="text-slate-400 hover:text-slate-600 text-lg font-bold">✕</button>
        </div>

        <form @submit.prevent="handleCreateUser" class="space-y-4 text-sm">
          <!-- Email (Primary Identity) -->
          <div>
            <label class="block font-medium text-slate-700 mb-1">Email Address (User Identity) *</label>
            <input 
              v-model="newUser.email"
              type="email"
              required
              placeholder="user@example.com"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
            <p class="text-xs text-slate-400 mt-1">This email becomes the unique User.name in Frappe.</p>
          </div>

          <!-- Name fields -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label class="block font-medium text-slate-700 mb-1">First Name *</label>
              <input 
                v-model="newUser.first_name"
                type="text"
                required
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block font-medium text-slate-700 mb-1">Middle Name</label>
              <input 
                v-model="newUser.middle_name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block font-medium text-slate-700 mb-1">Last Name</label>
              <input 
                v-model="newUser.last_name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <!-- User Type & Enabled -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div>
              <label class="block font-medium text-slate-700 mb-1">User Type</label>
              <select v-model="newUser.user_type" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
                <option value="System User">System User</option>
                <option value="Website User">Website User</option>
              </select>
            </div>

            <div class="flex items-center gap-2 pt-6">
              <input v-model="newUser.enabled" type="checkbox" id="newUserEnabled" class="w-4 h-4 rounded text-indigo-600" />
              <label for="newUserEnabled" class="text-slate-700 font-medium cursor-pointer">Enable User Account</label>
            </div>
          </div>

          <!-- Roles selection -->
          <div class="border-t pt-3">
            <label class="block font-medium text-slate-700 mb-2">Assign Roles</label>
            <div class="max-h-40 overflow-y-auto border border-slate-200 rounded-lg p-3 grid grid-cols-1 md:grid-cols-2 gap-2 bg-slate-50">
              <label 
                v-for="r in availableRoles" 
                :key="r.name"
                class="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer hover:text-indigo-600"
              >
                <input 
                  type="checkbox" 
                  :value="r.name" 
                  v-model="selectedRoles"
                  class="rounded text-indigo-600"
                />
                {{ r.role_name || r.name }}
              </label>
            </div>
          </div>

          <div class="flex justify-end gap-3 border-t pt-4">
            <button type="button" @click="showCreateModal = false" class="px-4 py-2 border rounded-lg text-slate-600 hover:bg-slate-50 font-medium">Cancel</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium shadow-sm flex items-center gap-2">
              <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              {{ saving ? 'Creating User...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUsers, saveUser, getRoles } from '../../services/admin'
import { useNotificationStore } from '../../stores/notification'

const router = useRouter()
const notification = useNotificationStore()

const users = ref([])
const availableRoles = ref([])
const loading = ref(false)
const saving = ref(false)

// Pagination & filters
const page = ref(1)
const pageLength = ref(25)
const totalCount = ref(0)
const searchText = ref('')
const statusFilter = ref('')
const userTypeFilter = ref('')
const roleFilter = ref('')

const showCreateModal = ref(false)
const selectedRoles = ref([])

const newUser = ref({
  email: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  user_type: 'System User',
  enabled: true
})

let searchTimeout = null

function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchUsers()
  }, 300)
}

function applyFilters() {
  page.value = 1
  fetchUsers()
}

function changePage(newPage) {
  page.value = newPage
  fetchUsers()
}

function clearFilters() {
  searchText.value = ''
  statusFilter.value = ''
  userTypeFilter.value = ''
  roleFilter.value = ''
  page.value = 1
  fetchUsers()
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getUsers({
      page: page.value,
      page_length: pageLength.value,
      search: searchText.value,
      enabled: statusFilter.value,
      user_type: userTypeFilter.value,
      role: roleFilter.value
    })

    if (res && res.data) {
      users.value = res.data
      totalCount.value = res.total_count || res.data.length
    } else {
      users.value = res || []
      totalCount.value = users.value.length
    }
  } catch (err) {
    console.error('Error fetching users:', err)
    notification.showError('Error Loading Users', err.message || 'Failed to fetch user list')
  } finally {
    loading.value = false
  }
}

async function fetchAvailableRoles() {
  try {
    const res = await getRoles()
    availableRoles.value = res.data || res || []
  } catch (err) {
    console.error('Error fetching roles:', err)
  }
}

function openCreateModal() {
  newUser.value = {
    email: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    user_type: 'System User',
    enabled: true
  }
  selectedRoles.value = []
  showCreateModal.value = true
}

async function handleCreateUser() {
  if (!newUser.value.email || !newUser.value.first_name) {
    notification.showWarning('Required Fields Missing', 'Please enter email address and first name.')
    return
  }

  saving.value = true
  try {
    const res = await saveUser({
      email: newUser.value.email,
      first_name: newUser.value.first_name,
      middle_name: newUser.value.middle_name,
      last_name: newUser.value.last_name,
      user_type: newUser.value.user_type,
      enabled: newUser.value.enabled ? 1 : 0
    }, selectedRoles.value, true)

    showCreateModal.value = false

    if (res.email_sent) {
      notification.showSuccess(`User ${newUser.value.email} created successfully! Password setup email sent to ${newUser.value.email}.`, 'User Created')
    } else if (res.email_error) {
      notification.showWarning(
        'User Created (Email Warning)',
        `User created successfully, but the password setup email could not be sent. Error: ${res.email_error}`
      )
    } else {
      notification.showSuccess(`User ${newUser.value.email} created successfully in native Frappe User DocType.`, 'User Created')
    }

    fetchUsers()
  } catch (err) {
    if (err.response && err.response.status === 409) {
      const email = newUser.value.email
      showCreateModal.value = false
      notification.showWarning(
        'User Already Exists',
        `User "${email}" already exists in Frappe.`,
        {
          okText: 'Open User Detail',
          onConfirm: () => {
            router.push(`/portal/administration/users/${encodeURIComponent(email)}`)
          }
        }
      )
    } else {
      notification.showError('Error Creating User', err.message || 'Failed to create user')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchAvailableRoles()
})
</script>

