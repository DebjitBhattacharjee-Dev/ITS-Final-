import { createRouter, createWebHistory } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import PortalLayout from '../layouts/PortalLayout.vue'
import PortalAccess from '../views/auth/PortalAccess.vue'
import Dashboard from '../views/WorkflowDashboard.vue'
import WorkspaceView from '../views/WorkspaceView.vue'
import ModuleDetailView from '../views/ModuleDetailView.vue'
import DocumentDetailView from '../views/DocumentDetailView.vue'
import NotFound from '../views/NotFound.vue'
import Forbidden from '../views/Forbidden.vue'
import SessionExpired from '../views/SessionExpired.vue'
import UserAdminView from '../views/admin/UserAdminView.vue'
import UserDetailView from '../views/admin/UserDetailView.vue'
import RoleAdminView from '../views/admin/RoleAdminView.vue'
import RolePermissionManagerView from '../views/admin/RolePermissionManagerView.vue'
import { setupGuards } from './guards'

const routes = [
  {
    path: '/',
    redirect: '/portal'
  },
  {
    path: '/portal-access',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'PortalAccess',
        component: PortalAccess
      }
    ]
  },
  {
    path: '/portal',
    component: PortalLayout,
    children: [
      {
        path: '',
        name: 'PortalHome',
        redirect: '/portal/project-management'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      // Workspace 01: Project Management
      {
        path: 'project-management',
        name: 'ProjectManagementWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/project-management',
        redirect: '/portal/project-management'
      },
      {
        path: 'project-management/:module',
        name: 'ProjectManagementModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'project-management/:module/:id',
        name: 'ProjectManagementDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/project-management/:module',
        redirect: to => `/portal/project-management/${to.params.module}`
      },

      // Workspace 02: Estimation and Cost Control
      {
        path: 'estimation-cost-control',
        name: 'EstimationCostControlWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/estimation-cost-control',
        redirect: '/portal/estimation-cost-control'
      },
      {
        path: 'workspaces/estimation-and-cost-control',
        redirect: '/portal/estimation-cost-control'
      },
      {
        path: 'estimation-cost-control/:module',
        name: 'EstimationCostControlModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'estimation-cost-control/:module/:id',
        name: 'EstimationCostControlDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/estimation-cost-control/:module',
        redirect: to => `/portal/estimation-cost-control/${to.params.module}`
      },
      {
        path: 'workspaces/estimation-and-cost-control/:module',
        redirect: to => `/portal/estimation-cost-control/${to.params.module}`
      },

      // Workspace 03: Planning
      {
        path: 'planning',
        name: 'PlanningWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/planning',
        redirect: '/portal/planning'
      },
      {
        path: 'planning/:module',
        name: 'PlanningModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'planning/:module/:id',
        name: 'PlanningDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/planning/:module',
        redirect: to => `/portal/planning/${to.params.module}`
      },

      // Workspace 04: Procurement and Subcontractors
      {
        path: 'procurement-subcontractors',
        name: 'ProcurementSubcontractorsWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/procurement-subcontractors',
        redirect: '/portal/procurement-subcontractors'
      },
      {
        path: 'workspaces/procurement-and-subcontractors',
        redirect: '/portal/procurement-subcontractors'
      },
      {
        path: 'procurement-subcontractors/:module',
        name: 'ProcurementSubcontractorsModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'procurement-subcontractors/:module/:id',
        name: 'ProcurementSubcontractorsDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/procurement-subcontractors/:module',
        redirect: to => `/portal/procurement-subcontractors/${to.params.module}`
      },

      // Workspace 05: Inventory Management
      {
        path: 'inventory-management',
        name: 'InventoryManagementWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/inventory-management',
        redirect: '/portal/inventory-management'
      },
      {
        path: 'inventory-management/:module',
        name: 'InventoryManagementModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'inventory-management/:module/:id',
        name: 'InventoryManagementDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/inventory-management/:module',
        redirect: to => `/portal/inventory-management/${to.params.module}`
      },

      // Workspace 06: HR and Manpower
      {
        path: 'hr-manpower',
        name: 'HRManpowerWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/hr-manpower',
        redirect: '/portal/hr-manpower'
      },
      {
        path: 'workspaces/hr-and-manpower',
        redirect: '/portal/hr-manpower'
      },
      {
        path: 'hr-manpower/:module',
        name: 'HRManpowerModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'hr-manpower/:module/:id',
        name: 'HRManpowerDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/hr-manpower/:module',
        redirect: to => `/portal/hr-manpower/${to.params.module}`
      },

      // Workspace 07: Fabrication, Assets, and Equipment Management
      {
        path: 'fabrication-assets-equipment',
        name: 'FabricationAssetsEquipmentWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/fabrication-assets-equipment',
        redirect: '/portal/fabrication-assets-equipment'
      },
      {
        path: 'workspaces/fabrication-assets-and-equipment',
        redirect: '/portal/fabrication-assets-equipment'
      },
      {
        path: 'fabrication-assets-equipment/:module',
        name: 'FabricationAssetsEquipmentModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'fabrication-assets-equipment/:module/:id',
        name: 'FabricationAssetsEquipmentDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/fabrication-assets-equipment/:module',
        redirect: to => `/portal/fabrication-assets-equipment/${to.params.module}`
      },

      // Workspace 08: Project Progress and Billing
      {
        path: 'project-progress-billing',
        name: 'ProjectProgressBillingWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/project-progress-billing',
        redirect: '/portal/project-progress-billing'
      },
      {
        path: 'workspaces/project-progress-and-billing',
        redirect: '/portal/project-progress-billing'
      },
      {
        path: 'project-progress-billing/:module',
        name: 'ProjectProgressBillingModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'project-progress-billing/:module/:id',
        name: 'ProjectProgressBillingDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/project-progress-billing/:module',
        redirect: to => `/portal/project-progress-billing/${to.params.module}`
      },

      // Workspace 09: Accounting and Finance
      {
        path: 'accounting-finance',
        name: 'AccountingFinanceWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/accounting-finance',
        redirect: '/portal/accounting-finance'
      },
      {
        path: 'workspaces/accounting-and-finance',
        redirect: '/portal/accounting-finance'
      },
      {
        path: 'accounting-finance/:module',
        name: 'AccountingFinanceModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'accounting-finance/:module/:id',
        name: 'AccountingFinanceDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/accounting-finance/:module',
        redirect: to => `/portal/accounting-finance/${to.params.module}`
      },

      // Workspace 10: Reporting
      {
        path: 'reporting',
        name: 'ReportingWorkspace',
        component: WorkspaceView
      },
      {
        path: 'workspaces/reporting',
        redirect: '/portal/reporting'
      },
      {
        path: 'reporting/:module',
        name: 'ReportingModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'reporting/:module/:id',
        name: 'ReportingDocumentDetail',
        component: DocumentDetailView
      },
      {
        path: 'workspaces/reporting/:module',
        redirect: to => `/portal/reporting/${to.params.module}`
      },

      // Administration Module Routes
      {
        path: 'administration/users',
        name: 'UserAdmin',
        component: UserAdminView
      },
      {
        path: 'administration/users/:id',
        name: 'UserDetailAdmin',
        component: UserDetailView
      },
      {
        path: 'administration/roles',
        name: 'RoleAdmin',
        component: RoleAdminView
      },
      {
        path: 'administration/role-permissions',
        name: 'RolePermissionManager',
        component: RolePermissionManagerView
      },

      // System Pages
      {
        path: '403',
        name: 'Forbidden',
        component: Forbidden
      },
      {
        path: 'session-expired',
        name: 'SessionExpired',
        component: SessionExpired
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

setupGuards(router)

export default router
