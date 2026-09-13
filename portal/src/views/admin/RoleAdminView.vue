<template>
  <div class="role-admin-container p-6 space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
          <span class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </span>
          Role Administration
        </h1>
        <p class="text-sm text-slate-500 mt-1">Manage native Frappe System and Portal Roles</p>
      </div>

      <div class="flex items-center gap-3">
        <router-link to="/portal/administration/role-permissions" class="px-4 py-2.5 border border-slate-200 hover:bg-slate-50 text-slate-700 font-medium text-sm rounded-lg transition-colors">
          Role Permission Manager
        </router-link>
        <button @click="showCreateModal = true" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg transition-colors">
          + New Role
        </button>
      </div>
    </div>

    <!-- Role List Table -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-50 border-b text-xs font-semibold text-slate-600 uppercase">
            <th class="py-3.5 px-4">Role Name</th>
            <th class="py-3.5 px-4">Desk Access</th>
            <th class="py-3.5 px-4">Custom Role</th>
            <th class="py-3.5 px-4">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="r in roles" :key="r.name" class="hover:bg-slate-50 transition-colors">
            <td class="py-3.5 px-4 font-medium text-slate-800">{{ r.role_name }}</td>
            <td class="py-3.5 px-4">
              <span :class="r.desk_access ? 'bg-indigo-50 text-indigo-700' : 'bg-slate-100 text-slate-600'" class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ r.desk_access ? 'Desk & Portal' : 'Portal Only' }}
              </span>
            </td>
            <td class="py-3.5 px-4 text-xs text-slate-500">{{ r.is_custom ? 'Custom' : 'Standard' }}</td>
            <td class="py-3.5 px-4">
              <span :class="!r.disabled ? 'text-emerald-600' : 'text-slate-400'" class="font-medium text-xs">
                {{ !r.disabled ? 'Active' : 'Disabled' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- New Role Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl max-w-md w-full p-6 shadow-xl space-y-4 border">
        <h3 class="text-base font-bold text-slate-800 border-b pb-2">Create Native Frappe Role</h3>
        <div>
          <label class="block font-medium text-slate-700 text-sm mb-1">Role Name *</label>
          <input v-model="newRoleName" type="text" placeholder="e.g. Site Supervisor" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm" />
        </div>

        <div class="flex items-center gap-2 pt-1 text-sm">
          <input v-model="newRoleDeskAccess" type="checkbox" id="deskAccessCheck" class="rounded text-indigo-600" />
          <label for="deskAccessCheck" class="text-slate-700">Allow ERPNext Desk Access</label>
        </div>

        <div class="flex justify-end gap-3 border-t pt-3">
          <button @click="showCreateModal = false" class="px-4 py-2 border rounded-lg text-slate-600 text-sm">Cancel</button>
          <button @click="handleCreateRole" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium text-sm">Create Role</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRoles, saveRole } from '../../services/admin'

const roles = ref([])
const showCreateModal = ref(false)
const newRoleName = ref('')
const newRoleDeskAccess = ref(true)

async function fetchRoles() {
  try {
    const res = await getRoles()
    roles.value = res.data || res || []
  } catch (err) {
    console.error('Error fetching roles:', err)
  }
}

async function handleCreateRole() {
  if (!newRoleName.value) return
  try {
    await saveRole(newRoleName.value, newRoleDeskAccess.value ? 1 : 0)
    showCreateModal.value = false
    newRoleName.value = ''
    fetchRoles()
  } catch (err) {
    alert(err.message || 'Error creating role')
  }
}

onMounted(() => {
  fetchRoles()
})
</script>
