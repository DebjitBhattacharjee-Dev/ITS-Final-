import { createRouter, createWebHistory } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import PortalLayout from '../layouts/PortalLayout.vue'
import PortalAccess from '../views/auth/PortalAccess.vue'
import Dashboard from '../views/Dashboard.vue'
import WorkspaceView from '../views/WorkspaceView.vue'
import ModuleDetailView from '../views/ModuleDetailView.vue'
import NotFound from '../views/NotFound.vue'
import Forbidden from '../views/Forbidden.vue'
import SessionExpired from '../views/SessionExpired.vue'
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
        redirect: '/portal/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'projects',
        name: 'ProjectsWorkspace',
        component: WorkspaceView
      },
      {
        path: 'projects/:module',
        name: 'ProjectsModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'estimation',
        name: 'EstimationWorkspace',
        component: WorkspaceView
      },
      {
        path: 'estimation/:module',
        name: 'EstimationModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'planning',
        name: 'PlanningWorkspace',
        component: WorkspaceView
      },
      {
        path: 'planning/:module',
        name: 'PlanningModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'procurement',
        name: 'ProcurementWorkspace',
        component: WorkspaceView
      },
      {
        path: 'procurement/:module',
        name: 'ProcurementModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'inventory',
        name: 'InventoryWorkspace',
        component: WorkspaceView
      },
      {
        path: 'inventory/:module',
        name: 'InventoryModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'hr',
        name: 'HRWorkspace',
        component: WorkspaceView
      },
      {
        path: 'hr/:module',
        name: 'HRModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'fabrication',
        name: 'FabricationWorkspace',
        component: WorkspaceView
      },
      {
        path: 'fabrication/:module',
        name: 'FabricationModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'billing',
        name: 'BillingWorkspace',
        component: WorkspaceView
      },
      {
        path: 'billing/:module',
        name: 'BillingModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'accounting',
        name: 'AccountingWorkspace',
        component: WorkspaceView
      },
      {
        path: 'accounting/:module',
        name: 'AccountingModuleDetail',
        component: ModuleDetailView
      },
      {
        path: 'reporting',
        name: 'ReportingWorkspace',
        component: WorkspaceView
      },
      {
        path: 'reporting/:module',
        name: 'ReportingModuleDetail',
        component: ModuleDetailView
      },
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
