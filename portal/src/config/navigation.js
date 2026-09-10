export const workspaces = [
  {
    id: 'project-management',
    number: '01',
    label: 'Project Management',
    description: 'Manage the project from contract award to handover.',
    route: '/portal/projects',
    icon: 'FolderKanban',
    required_roles: ['Projects User', 'Project Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Project Setup',
        items: [
          { label: 'Dashboard', route: '/portal/projects/dashboard', docType: 'Project' },
          { label: 'Project Register', route: '/portal/projects/register', docType: 'Project' },
          { label: 'Client and Consultant Directory', route: '/portal/projects/directory', docType: 'Customer' },
          { label: 'Project Contracts', route: '/portal/projects/contracts', docType: 'Sales Order' },
          { label: 'Project Team and Responsibilities', route: '/portal/projects/team', docType: 'User' },
          { label: 'Project Scope and Deliverables', route: '/portal/projects/scope', docType: 'Project' },
          { label: 'Work Breakdown Structure (WBS)', route: '/portal/projects/wbs', docType: 'Task' },
        ]
      },
      {
        title: 'Documents and Coordination',
        items: [
          { label: 'Project Documents and Drawings', route: '/portal/projects/documents', docType: 'File' },
          { label: 'Requests for Information (RFIs)', route: '/portal/projects/rfis', docType: 'Issue' },
          { label: 'Material and Technical Submittals', route: '/portal/projects/submittals', docType: 'Issue' },
          { label: 'Meeting Minutes and Action Items', route: '/portal/projects/meetings', docType: 'Issue' },
        ]
      },
      {
        title: 'Controls and Quality',
        items: [
          { label: 'Risks and Issues', route: '/portal/projects/risks', docType: 'Issue' },
          { label: 'Change and Variation Register', route: '/portal/projects/variations', docType: 'Project' },
          { label: 'Quality Inspections and Nonconformances', route: '/portal/projects/quality', docType: 'Quality Inspection' },
        ]
      },
      {
        title: 'Handover',
        items: [
          { label: 'Snag and Punch Lists', route: '/portal/projects/snags', docType: 'Task' },
          { label: 'Project Handover and Closeout', route: '/portal/projects/handover', docType: 'Project' },
        ]
      },
      {
        title: 'Project Warranties and Defects Liability',
        items: [
          { label: 'Project Warranty Register', route: '/portal/projects/warranties', docType: 'Warranty Claim' },
          { label: 'Workmanship and Installation Warranties', route: '/portal/projects/workmanship-warranties', docType: 'Warranty Claim' },
          { label: 'Warranty Certificates', route: '/portal/projects/warranty-certificates', docType: 'Warranty Claim' },
          { label: 'Defects Liability Periods', route: '/portal/projects/defects-liability', docType: 'Warranty Claim' },
          { label: 'Defect Notices and Rectification', route: '/portal/projects/defect-notices', docType: 'Warranty Claim' },
          { label: 'Warranty and Defects Liability Closeout', route: '/portal/projects/warranty-closeout', docType: 'Warranty Claim' },
        ]
      }
    ]
  },
  {
    id: 'estimation',
    number: '02',
    label: 'Estimation and Cost Control',
    description: 'Control project tendering, BOQ, rate analysis, and budget monitoring.',
    route: '/portal/estimation',
    icon: 'Calculator',
    required_roles: ['Accounts User', 'Estimation Engineer', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Estimation Setup',
        items: [
          { label: 'Material and Service Items', route: '/portal/estimation/items', docType: 'Item' },
          { label: 'Units of Measure', route: '/portal/estimation/uom', docType: 'UOM' },
          { label: 'Price Lists and Item Rates', route: '/portal/estimation/price-lists', docType: 'Item Price' },
          { label: 'Cost Code Structure', route: '/portal/estimation/cost-codes', docType: 'Cost Center' },
          { label: 'Labour and Equipment Rate Library', route: '/portal/estimation/rate-library', docType: 'Item' },
        ]
      },
      {
        title: 'Tendering and Estimates',
        items: [
          { label: 'Tender Register', route: '/portal/estimation/tenders', docType: 'Quotation' },
          { label: 'Bill of Quantities (BOQ)', route: '/portal/estimation/boq', docType: 'Quotation' },
          { label: 'Detailed Rate Analysis', route: '/portal/estimation/rate-analysis', docType: 'Item' },
          { label: 'Estimate Versions', route: '/portal/estimation/versions', docType: 'Quotation' },
          { label: 'Markup and Contingency Analysis', route: '/portal/estimation/contingency', docType: 'Quotation' },
          { label: 'Client Quotations', route: '/portal/estimation/quotations', docType: 'Quotation' },
        ]
      },
      {
        title: 'Budget Control',
        items: [
          { label: 'Project Budgets', route: '/portal/estimation/budgets', docType: 'Budget' },
          { label: 'Cost Centers', route: '/portal/estimation/cost-centers', docType: 'Cost Center' },
          { label: 'BOQ-to-Budget Allocation', route: '/portal/estimation/budget-allocations', docType: 'Budget' },
          { label: 'Budget Revisions and Transfers', route: '/portal/estimation/budget-revisions', docType: 'Budget' },
          { label: 'Budget Approval Register', route: '/portal/estimation/budget-approvals', docType: 'Budget' },
        ]
      },
      {
        title: 'Cost Monitoring',
        items: [
          { label: 'Budget Variance', route: '/portal/estimation/variance', docType: 'Budget' },
          { label: 'Actual Cost Ledger', route: '/portal/estimation/actual-costs', docType: 'GL Entry' },
          { label: 'Committed Cost Report', route: '/portal/estimation/committed-costs', docType: 'Purchase Order' },
          { label: 'Cost by BOQ and Cost Code', route: '/portal/estimation/cost-by-boq', docType: 'Cost Center' },
          { label: 'Variation Cost Analysis', route: '/portal/estimation/variation-costs', docType: 'Project' },
          { label: 'Forecast Cost to Complete', route: '/portal/estimation/cost-to-complete', docType: 'Project' },
          { label: 'Forecast Final Cost and Margin', route: '/portal/estimation/final-margin', docType: 'Project' },
          { label: 'Warranty and Defect Rectification Costs', route: '/portal/estimation/warranty-costs', docType: 'Warranty Claim' },
        ]
      }
    ]
  },
  {
    id: 'planning',
    number: '03',
    label: 'Planning',
    description: 'Schedule project programmes, Gantt charts, and resource loading.',
    route: '/portal/planning',
    icon: 'Calendar',
    required_roles: ['Projects User', 'Planning Engineer', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Planning Setup',
        items: [
          { label: 'Project Activities', route: '/portal/planning/activities', docType: 'Task' },
          { label: 'Activity Templates', route: '/portal/planning/activity-templates', docType: 'Task' },
          { label: 'Task Dependencies', route: '/portal/planning/dependencies', docType: 'Task' },
          { label: 'Project Working Calendars', route: '/portal/planning/calendars', docType: 'Holiday List' },
        ]
      },
      {
        title: 'Programme Management',
        items: [
          { label: 'Task Gantt View', route: '/portal/planning/gantt', docType: 'Task' },
          { label: 'Baseline Programme and Revisions', route: '/portal/planning/baselines', docType: 'Project' },
          { label: 'Milestone Register', route: '/portal/planning/milestones', docType: 'Task' },
          { label: 'Weekly and Monthly Look-Ahead Plans', route: '/portal/planning/look-ahead', docType: 'Task' },
          { label: 'Programme Update Register', route: '/portal/planning/programme-updates', docType: 'Project' },
        ]
      },
      {
        title: 'Resource Planning',
        items: [
          { label: 'Manpower Requirements', route: '/portal/planning/manpower-req', docType: 'Task' },
          { label: 'Material Requirements Schedule', route: '/portal/planning/material-req', docType: 'Material Request' },
          { label: 'Equipment Requirements', route: '/portal/planning/equipment-req', docType: 'Task' },
          { label: 'Procurement Schedule', route: '/portal/planning/procurement-schedule', docType: 'Material Request' },
          { label: 'Fabrication and Delivery Schedule', route: '/portal/planning/fabrication-schedule', docType: 'Work Order' },
        ]
      },
      {
        title: 'Planning Reports',
        items: [
          { label: 'Planned vs Actual Progress', route: '/portal/planning/progress-report', docType: 'Project' },
          { label: 'Progress S-Curves', route: '/portal/planning/s-curves', docType: 'Project' },
          { label: 'Resource Histograms', route: '/portal/planning/resource-histograms', docType: 'Task' },
          { label: 'Delay Register', route: '/portal/planning/delays', docType: 'Issue' },
          { label: 'Recovery Plans', route: '/portal/planning/recovery-plans', docType: 'Project' },
        ]
      }
    ]
  },
  {
    id: 'procurement',
    number: '04',
    label: 'Procurement and Subcontractors',
    description: 'Manage material requisitions, RFQs, subcontracts, and supplier warranties.',
    route: '/portal/procurement',
    icon: 'ShoppingCart',
    required_roles: ['Purchase User', 'Procurement Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Supplier and Subcontractor Setup',
        items: [
          { label: 'Supplier Directory', route: '/portal/procurement/suppliers', docType: 'Supplier' },
          { label: 'Subcontractor Directory', route: '/portal/procurement/subcontractors', docType: 'Supplier' },
          { label: 'Supplier Groups', route: '/portal/procurement/supplier-groups', docType: 'Supplier Group' },
          { label: 'Contacts and Addresses', route: '/portal/procurement/contacts', docType: 'Contact' },
          { label: 'Prequalification and Document Expiry', route: '/portal/procurement/prequalifications', docType: 'Supplier' },
        ]
      },
      {
        title: 'Requisitions and Sourcing',
        items: [
          { label: 'Material and Service Requests', route: '/portal/procurement/requests', docType: 'Material Request' },
          { label: 'Requests for Quotation', route: '/portal/procurement/rfqs', docType: 'Request for Quotation' },
          { label: 'Supplier Quotations', route: '/portal/procurement/quotations', docType: 'Supplier Quotation' },
          { label: 'Supplier Quotation Comparison', route: '/portal/procurement/comparison', docType: 'Supplier Quotation' },
          { label: 'Technical and Commercial Evaluation', route: '/portal/procurement/evaluations', docType: 'Supplier Quotation' },
        ]
      },
      {
        title: 'Purchasing',
        items: [
          { label: 'Purchase Orders', route: '/portal/procurement/orders', docType: 'Purchase Order' },
          { label: 'Purchase Receipts', route: '/portal/procurement/receipts', docType: 'Purchase Receipt' },
          { label: 'Purchase Returns', route: '/portal/procurement/returns', docType: 'Purchase Receipt' },
          { label: 'Delivery Expediting Register', route: '/portal/procurement/expediting', docType: 'Purchase Order' },
          { label: 'Service Completion Acceptance', route: '/portal/procurement/service-acceptances', docType: 'Purchase Receipt' },
        ]
      },
      {
        title: 'Construction Subcontracts',
        items: [
          { label: 'Subcontract Agreements and BOQ', route: '/portal/procurement/subcontracts', docType: 'Purchase Order' },
          { label: 'Subcontract Work Orders', route: '/portal/procurement/subcontract-work-orders', docType: 'Purchase Order' },
          { label: 'Subcontract Variations', route: '/portal/procurement/subcontract-variations', docType: 'Purchase Order' },
          { label: 'Subcontractor Measurements', route: '/portal/procurement/measurements', docType: 'Purchase Order' },
          { label: 'Subcontractor Progress Claims', route: '/portal/procurement/subcontract-claims', docType: 'Purchase Invoice' },
          { label: 'Subcontractor Payment Certificates', route: '/portal/procurement/payment-certificates', docType: 'Payment Entry' },
          { label: 'Retention and Advance Recovery', route: '/portal/procurement/retention-recovery', docType: 'Purchase Invoice' },
          { label: 'Subcontract Final Accounts', route: '/portal/procurement/final-accounts', docType: 'Purchase Invoice' },
        ]
      },
      {
        title: 'Supplier and Subcontractor Warranties',
        items: [
          { label: 'Supplier Warranty Register', route: '/portal/procurement/supplier-warranties', docType: 'Warranty Claim' },
          { label: 'Manufacturer Warranty Certificates', route: '/portal/procurement/manufacturer-certificates', docType: 'Warranty Claim' },
          { label: 'Subcontractor Workmanship Warranties', route: '/portal/procurement/subcontractor-warranties', docType: 'Warranty Claim' },
          { label: 'Warranty Claims Against Suppliers', route: '/portal/procurement/supplier-claims', docType: 'Warranty Claim' },
          { label: 'Repair and Replacement Follow-Up', route: '/portal/procurement/repair-followup', docType: 'Warranty Claim' },
          { label: 'Warranty Cost Recovery', route: '/portal/procurement/warranty-recovery', docType: 'Warranty Claim' },
        ]
      }
    ]
  },
  {
    id: 'inventory',
    number: '05',
    label: 'Inventory Management',
    description: 'Track materials, site stores, stock balances, and product warranties.',
    route: '/portal/inventory',
    icon: 'Boxes',
    required_roles: ['Stock User', 'Store Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Inventory Setup',
        items: [
          { label: 'Item Catalog', route: '/portal/inventory/items', docType: 'Item' },
          { label: 'Item Groups', route: '/portal/inventory/item-groups', docType: 'Item Group' },
          { label: 'Units of Measure', route: '/portal/inventory/uom', docType: 'UOM' },
          { label: 'Warehouses and Project Stores', route: '/portal/inventory/warehouses', docType: 'Warehouse' },
          { label: 'Reorder Settings', route: '/portal/inventory/reorder-settings', docType: 'Item' },
        ]
      },
      {
        title: 'Material Transactions',
        items: [
          { label: 'Material Requests', route: '/portal/inventory/material-requests', docType: 'Material Request' },
          { label: 'Goods Received', route: '/portal/inventory/goods-received', docType: 'Purchase Receipt' },
          { label: 'Material Issues', route: '/portal/inventory/material-issues', docType: 'Stock Entry' },
          { label: 'Store Transfers', route: '/portal/inventory/store-transfers', docType: 'Stock Entry' },
          { label: 'Other Material Receipts', route: '/portal/inventory/other-receipts', docType: 'Stock Entry' },
          { label: 'Returns to Suppliers', route: '/portal/inventory/supplier-returns', docType: 'Purchase Receipt' },
          { label: 'Site Return Approval and Tracking', route: '/portal/inventory/site-returns', docType: 'Stock Entry' },
        ]
      },
      {
        title: 'Stock Control',
        items: [
          { label: 'Stock Reconciliation', route: '/portal/inventory/reconciliation', docType: 'Stock Reconciliation' },
          { label: 'Batch Records', route: '/portal/inventory/batches', docType: 'Batch' },
          { label: 'Serial Number Records', route: '/portal/inventory/serials', docType: 'Serial No' },
          { label: 'Project Material Reservations', route: '/portal/inventory/reservations', docType: 'Stock Entry' },
          { label: 'Scrap and Damage Approval Register', route: '/portal/inventory/scrap-approvals', docType: 'Stock Entry' },
        ]
      },
      {
        title: 'Product Warranty and After-Sales Service',
        items: [
          { label: 'Product Warranty Details', route: '/portal/inventory/warranties', docType: 'Warranty Claim' },
          { label: 'Warranty and AMC Expiry Dates', route: '/portal/inventory/warranty-expiries', docType: 'Warranty Claim' },
          { label: 'Customer Warranty Claims', route: '/portal/inventory/customer-claims', docType: 'Warranty Claim' },
          { label: 'Claim Status and Resolution', route: '/portal/inventory/claim-status', docType: 'Warranty Claim' },
          { label: 'Maintenance Visits', route: '/portal/inventory/maintenance-visits', docType: 'Warranty Claim' },
          { label: 'Product Warranty Certificates', route: '/portal/inventory/certificates', docType: 'Warranty Claim' },
          { label: 'Warranty Expiry Alerts', route: '/portal/inventory/expiry-alerts', docType: 'Warranty Claim' },
          { label: 'Supplier Warranty Register', route: '/portal/inventory/supplier-register', docType: 'Warranty Claim' },
        ]
      },
      {
        title: 'Inventory Reports',
        items: [
          { label: 'Stock Balance', route: '/portal/inventory/stock-balance', docType: 'Stock Ledger Entry' },
          { label: 'Stock Ledger', route: '/portal/inventory/stock-ledger', docType: 'Stock Ledger Entry' },
          { label: 'Stock Ageing', route: '/portal/inventory/stock-ageing', docType: 'Stock Ledger Entry' },
          { label: 'Project Material Consumption', route: '/portal/inventory/consumption', docType: 'Stock Entry' },
          { label: 'Material Issued vs BOQ Allowance', route: '/portal/inventory/issued-vs-boq', docType: 'Stock Entry' },
        ]
      }
    ]
  },
  {
    id: 'hr',
    number: '06',
    label: 'HR and Manpower',
    description: 'Manage workforce deployment, timesheets, site attendance, and payroll.',
    route: '/portal/hr',
    icon: 'Users',
    required_roles: ['HR User', 'HR Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Employee Setup',
        items: [
          { label: 'Employee Directory', route: '/portal/hr/employees', docType: 'Employee' },
          { label: 'Departments and Designations', route: '/portal/hr/departments', docType: 'Department' },
          { label: 'Employment Types and Grades', route: '/portal/hr/grades', docType: 'Employee Grade' },
          { label: 'Employee Onboarding', route: '/portal/hr/onboarding', docType: 'Employee Onboarding' },
          { label: 'Visa, Permit, and Certificate Expiry Register', route: '/portal/hr/expiries', docType: 'Employee' },
        ]
      },
      {
        title: 'Manpower Deployment',
        items: [
          { label: 'Site and Project Assignments', route: '/portal/hr/site-assignments', docType: 'Employee' },
          { label: 'Crew and Gang Register', route: '/portal/hr/crews', docType: 'Employee' },
          { label: 'Manpower Transfer Requests', route: '/portal/hr/transfers', docType: 'Employee' },
          { label: 'Daily Site Manpower Register', route: '/portal/hr/daily-register', docType: 'Attendance' },
        ]
      },
      {
        title: 'Attendance and Leave',
        items: [
          { label: 'Shift Types and Assignments', route: '/portal/hr/shifts', docType: 'Shift Type' },
          { label: 'Employee Check-ins', route: '/portal/hr/checkins', docType: 'Employee Checkin' },
          { label: 'Attendance', route: '/portal/hr/attendance', docType: 'Attendance' },
          { label: 'Leave Applications and Allocations', route: '/portal/hr/leaves', docType: 'Leave Application' },
          { label: 'Holiday Lists', route: '/portal/hr/holidays', docType: 'Holiday List' },
          { label: 'Project Timesheets', route: '/portal/hr/timesheets', docType: 'Timesheet' },
          { label: 'Site Overtime Approval', route: '/portal/hr/overtime', docType: 'Attendance' },
        ]
      },
      {
        title: 'Payroll and Employee Expenses',
        items: [
          { label: 'Salary Components', route: '/portal/hr/salary-components', docType: 'Salary Component' },
          { label: 'Salary Structures and Assignments', route: '/portal/hr/salary-structures', docType: 'Salary Structure' },
          { label: 'Additional Salary', route: '/portal/hr/additional-salary', docType: 'Additional Salary' },
          { label: 'Payroll Entries', route: '/portal/hr/payroll-entries', docType: 'Payroll Entry' },
          { label: 'Salary Slips', route: '/portal/hr/salary-slips', docType: 'Salary Slip' },
          { label: 'Employee Advances', route: '/portal/hr/advances', docType: 'Employee Advance' },
          { label: 'Expense Claims', route: '/portal/hr/expenses', docType: 'Expense Claim' },
        ]
      },
      {
        title: 'Employee Services and Reports',
        items: [
          { label: 'Training Events', route: '/portal/hr/trainings', docType: 'Training Event' },
          { label: 'Employee Separation', route: '/portal/hr/separations', docType: 'Employee Separation' },
          { label: 'Attendance Reports', route: '/portal/hr/attendance-reports', docType: 'Attendance' },
          { label: 'Salary Register', route: '/portal/hr/salary-register', docType: 'Salary Slip' },
          { label: 'Project Manpower and Labour Cost Report', route: '/portal/hr/manpower-costs', docType: 'Timesheet' },
          { label: 'Final Settlement Calculation and Approval', route: '/portal/hr/final-settlements', docType: 'Employee Separation' },
        ]
      }
    ]
  },
  {
    id: 'fabrication',
    number: '07',
    label: 'Fabrication, Assets, and Equipment Management',
    description: 'Track plant assets, equipment usage logs, shop fabrication, and machinery warranties.',
    route: '/portal/fabrication',
    icon: 'Factory',
    required_roles: ['Manufacturing User', 'Fabrication Manager', 'Equipment Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Fabrication Setup',
        items: [
          { label: 'Fabricated Items', route: '/portal/fabrication/items', docType: 'Item' },
          { label: 'Bills of Materials', route: '/portal/fabrication/bom', docType: 'BOM' },
          { label: 'Operations', route: '/portal/fabrication/operations', docType: 'Operation' },
          { label: 'Workstations', route: '/portal/fabrication/workstations', docType: 'Workstation' },
          { label: 'Routings', route: '/portal/fabrication/routings', docType: 'BOM' },
          { label: 'Shop Drawing and Revision Register', route: '/portal/fabrication/drawings', docType: 'File' },
        ]
      },
      {
        title: 'Fabrication Execution',
        items: [
          { label: 'Production Plans', route: '/portal/fabrication/production-plans', docType: 'Production Plan' },
          { label: 'Fabrication Orders', route: '/portal/fabrication/work-orders', docType: 'Work Order' },
          { label: 'Job Cards', route: '/portal/fabrication/job-cards', docType: 'Job Card' },
          { label: 'Material Transfers to Production', route: '/portal/fabrication/material-transfers', docType: 'Stock Entry' },
          { label: 'Material Consumption', route: '/portal/fabrication/consumption', docType: 'Stock Entry' },
          { label: 'Finished Goods Receipt', route: '/portal/fabrication/finished-goods', docType: 'Stock Entry' },
          { label: 'Quality Inspections', route: '/portal/fabrication/inspections', docType: 'Quality Inspection' },
          { label: 'Internal Dispatch to Site', route: '/portal/fabrication/site-dispatch', docType: 'Stock Entry' },
          { label: 'Fabrication Progress by Project and Drawing', route: '/portal/fabrication/progress', docType: 'Work Order' },
        ]
      },
      {
        title: 'Asset Management',
        items: [
          { label: 'Asset Register', route: '/portal/fabrication/assets', docType: 'Asset' },
          { label: 'Asset Categories', route: '/portal/fabrication/asset-categories', docType: 'Asset Category' },
          { label: 'Asset Locations', route: '/portal/fabrication/asset-locations', docType: 'Location' },
          { label: 'Asset Capitalization', route: '/portal/fabrication/capitalization', docType: 'Asset' },
          { label: 'Asset Movement and Custody', route: '/portal/fabrication/asset-movements', docType: 'Asset Movement' },
          { label: 'Asset Depreciation', route: '/portal/fabrication/depreciation', docType: 'Asset' },
          { label: 'Asset Maintenance', route: '/portal/fabrication/asset-maintenance', docType: 'Asset Maintenance' },
          { label: 'Asset Repairs', route: '/portal/fabrication/asset-repairs', docType: 'Asset Repair' },
          { label: 'Asset Disposal', route: '/portal/fabrication/asset-disposal', docType: 'Asset' },
        ]
      },
      {
        title: 'Equipment Operations',
        items: [
          { label: 'Owned Equipment Register', route: '/portal/fabrication/owned-equipment', docType: 'Asset' },
          { label: 'Hired Equipment Register', route: '/portal/fabrication/hired-equipment', docType: 'Asset' },
          { label: 'Equipment Requests and Site Allocation', route: '/portal/fabrication/equipment-allocations', docType: 'Asset Movement' },
          { label: 'Mobilization and Demobilization', route: '/portal/fabrication/mobilizations', docType: 'Asset Movement' },
          { label: 'Operator Assignments', route: '/portal/fabrication/operator-assignments', docType: 'Asset' },
          { label: 'Daily Hours and Meter Readings', route: '/portal/fabrication/meter-readings', docType: 'Asset' },
          { label: 'Fuel and Lubricant Consumption', route: '/portal/fabrication/fuel-consumption', docType: 'Stock Entry' },
          { label: 'Equipment Inspection and Certificate Register', route: '/portal/fabrication/equipment-certificates', docType: 'Quality Inspection' },
          { label: 'Rental Charges and Project Allocation', route: '/portal/fabrication/rental-charges', docType: 'Purchase Invoice' },
          { label: 'Utilization, Downtime, and Operating Cost', route: '/portal/fabrication/operating-costs', docType: 'Asset' },
        ]
      },
      {
        title: 'Warranty and Service',
        items: [
          { label: 'Manufactured Product Warranty Claims', route: '/portal/fabrication/manufactured-claims', docType: 'Warranty Claim' },
          { label: 'Asset and Equipment Supplier Warranties', route: '/portal/fabrication/equipment-warranties', docType: 'Warranty Claim' },
          { label: 'Warranty Certificates', route: '/portal/fabrication/warranty-certificates', docType: 'Warranty Claim' },
          { label: 'Warranty Repair and Replacement Tracking', route: '/portal/fabrication/repair-tracking', docType: 'Warranty Claim' },
        ]
      }
    ]
  },
  {
    id: 'billing',
    number: '08',
    label: 'Project Progress and Billing',
    description: 'Process measurement sheets, client progress claims, retention, and final accounts.',
    route: '/portal/billing',
    icon: 'Receipt',
    required_roles: ['Accounts User', 'Projects User', 'Finance Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Contract and Billing Setup',
        items: [
          { label: 'Client Orders', route: '/portal/billing/client-orders', docType: 'Sales Order' },
          { label: 'Contract BOQ and Revisions', route: '/portal/billing/contract-boq', docType: 'Sales Order' },
          { label: 'Billing Milestones and Schedule', route: '/portal/billing/milestones', docType: 'Sales Order' },
          { label: 'Retention and Advance Recovery Rules', route: '/portal/billing/retention-rules', docType: 'Sales Order' },
        ]
      },
      {
        title: 'Site Progress',
        items: [
          { label: 'Daily Progress Reports', route: '/portal/billing/daily-progress', docType: 'Task' },
          { label: 'Site Measurement Sheets', route: '/portal/billing/measurements', docType: 'Task' },
          { label: 'Work Completion Records', route: '/portal/billing/completion-records', docType: 'Task' },
          { label: 'BOQ Quantity Progress', route: '/portal/billing/boq-progress', docType: 'Sales Order' },
          { label: 'Approved Variations', route: '/portal/billing/approved-variations', docType: 'Sales Order' },
        ]
      },
      {
        title: 'Claims and Certification',
        items: [
          { label: 'Client Progress Claims', route: '/portal/billing/client-claims', docType: 'Sales Invoice' },
          { label: 'Client Payment Certificates', route: '/portal/billing/payment-certificates', docType: 'Payment Entry' },
          { label: 'Advance Recovery Calculations', route: '/portal/billing/advance-recoveries', docType: 'Sales Invoice' },
          { label: 'Retention Calculations', route: '/portal/billing/retention-calculations', docType: 'Sales Invoice' },
          { label: 'Deductions and Adjustments', route: '/portal/billing/deductions', docType: 'Sales Invoice' },
        ]
      },
      {
        title: 'Invoicing and Closeout',
        items: [
          { label: 'Client Invoices', route: '/portal/billing/invoices', docType: 'Sales Invoice' },
          { label: 'Client Credit Notes', route: '/portal/billing/credit-notes', docType: 'Sales Invoice' },
          { label: 'Client Receipts', route: '/portal/billing/receipts', docType: 'Payment Entry' },
          { label: 'Receivables', route: '/portal/billing/receivables', docType: 'Sales Invoice' },
          { label: 'Unbilled and Uncertified Work', route: '/portal/billing/unbilled-work', docType: 'Sales Invoice' },
          { label: 'Retention Release Register', route: '/portal/billing/retention-releases', docType: 'Payment Entry' },
          { label: 'Handover and Defects Clearance for Retention Release', route: '/portal/billing/defects-clearance', docType: 'Warranty Claim' },
          { label: 'Project Final Account', route: '/portal/billing/final-account', docType: 'Sales Invoice' },
        ]
      }
    ]
  },
  {
    id: 'accounting',
    number: '09',
    label: 'Accounting and Finance',
    description: 'Manage general ledger, payables, receivables, cash flow, and period closing.',
    route: '/portal/accounting',
    icon: 'Landmark',
    required_roles: ['Accounts Manager', 'Accountant', 'Finance Manager', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Accounting Setup',
        items: [
          { label: 'Company', route: '/portal/accounting/company', docType: 'Company' },
          { label: 'Chart of Accounts', route: '/portal/accounting/coa', docType: 'Account' },
          { label: 'Cost Centers', route: '/portal/accounting/cost-centers', docType: 'Cost Center' },
          { label: 'Accounting Dimensions', route: '/portal/accounting/dimensions', docType: 'Accounting Dimension' },
          { label: 'Fiscal Years', route: '/portal/accounting/fiscal-years', docType: 'Fiscal Year' },
          { label: 'Bank Accounts and Modes of Payment', route: '/portal/accounting/banks', docType: 'Bank Account' },
          { label: 'Payment Terms', route: '/portal/accounting/payment-terms', docType: 'Payment Terms Template' },
          { label: 'Tax Templates', route: '/portal/accounting/taxes', docType: 'Sales Taxes and Charges Template' },
        ]
      },
      {
        title: 'Receivables',
        items: [
          { label: 'Customers', route: '/portal/accounting/customers', docType: 'Customer' },
          { label: 'Sales Invoices', route: '/portal/accounting/sales-invoices', docType: 'Sales Invoice' },
          { label: 'Credit Notes', route: '/portal/accounting/credit-notes', docType: 'Sales Invoice' },
          { label: 'Customer Receipts', route: '/portal/accounting/customer-receipts', docType: 'Payment Entry' },
          { label: 'Accounts Receivable', route: '/portal/accounting/ar', docType: 'Sales Invoice' },
        ]
      },
      {
        title: 'Payables',
        items: [
          { label: 'Suppliers', route: '/portal/accounting/suppliers', docType: 'Supplier' },
          { label: 'Purchase Invoices', route: '/portal/accounting/purchase-invoices', docType: 'Purchase Invoice' },
          { label: 'Debit Notes', route: '/portal/accounting/debit-notes', docType: 'Purchase Invoice' },
          { label: 'Supplier Payments', route: '/portal/accounting/supplier-payments', docType: 'Payment Entry' },
          { label: 'Accounts Payable', route: '/portal/accounting/ap', docType: 'Purchase Invoice' },
        ]
      },
      {
        title: 'Banking and General Accounting',
        items: [
          { label: 'Payment Entries', route: '/portal/accounting/payment-entries', docType: 'Payment Entry' },
          { label: 'Journal Entries', route: '/portal/accounting/journal-entries', docType: 'Journal Entry' },
          { label: 'Bank Transactions', route: '/portal/accounting/bank-transactions', docType: 'Bank Transaction' },
          { label: 'Bank Reconciliation', route: '/portal/accounting/bank-reconciliation', docType: 'Bank Clearance' },
          { label: 'Payment Reconciliation', route: '/portal/accounting/payment-reconciliation', docType: 'Payment Reconciliation' },
          { label: 'Petty Cash Entries', route: '/portal/accounting/petty-cash', docType: 'Journal Entry' },
          { label: 'Bank Guarantees', route: '/portal/accounting/bank-guarantees', docType: 'Journal Entry' },
        ]
      },
      {
        title: 'Construction Finance',
        items: [
          { label: 'Retention Receivable and Payable Schedule', route: '/portal/accounting/retention-schedule', docType: 'GL Entry' },
          { label: 'Advance Recovery Schedule', route: '/portal/accounting/advance-schedule', docType: 'GL Entry' },
          { label: 'Project Accrual and WIP Review', route: '/portal/accounting/wip-review', docType: 'GL Entry' },
          { label: 'Project Cash Flow Forecast', route: '/portal/accounting/cash-flow-forecast', docType: 'GL Entry' },
          { label: 'Warranty Costs and Supplier Recoveries', route: '/portal/accounting/warranty-finance', docType: 'Warranty Claim' },
        ]
      },
      {
        title: 'Financial Reports and Closing',
        items: [
          { label: 'General Ledger', route: '/portal/accounting/gl', docType: 'GL Entry' },
          { label: 'Trial Balance', route: '/portal/accounting/tb', docType: 'GL Entry' },
          { label: 'Profit and Loss Statement', route: '/portal/accounting/pnl', docType: 'GL Entry' },
          { label: 'Balance Sheet', route: '/portal/accounting/bs', docType: 'GL Entry' },
          { label: 'Cash Flow Statement', route: '/portal/accounting/cash-flow', docType: 'GL Entry' },
          { label: 'Period Closing Voucher', route: '/portal/accounting/period-closing', docType: 'Period Closing Voucher' },
        ]
      }
    ]
  },
  {
    id: 'reporting',
    number: '10',
    label: 'Reporting',
    description: 'Executive dashboards, cost analytics, procurement metrics, and financial statements.',
    route: '/portal/reporting',
    icon: 'BarChart3',
    required_roles: ['Projects User', 'Accounts User', 'Management Viewer', 'Portal Administrator', 'System Manager'],
    sections: [
      {
        title: 'Management',
        items: [
          { label: 'Company Performance Dashboard', route: '/portal/reporting/company-dashboard', docType: 'Project' },
          { label: 'Project Portfolio Dashboard', route: '/portal/reporting/portfolio-dashboard', docType: 'Project' },
          { label: 'Project Profitability Summary', route: '/portal/reporting/profitability-summary', docType: 'Project' },
          { label: 'Approvals and Exceptions Dashboard', route: '/portal/reporting/approvals-dashboard', docType: 'Project' },
        ]
      },
      {
        title: 'Estimation and Cost',
        items: [
          { label: 'Budget Variance Report', route: '/portal/reporting/budget-variance', docType: 'Budget' },
          { label: 'Estimate vs Budget vs Actual', route: '/portal/reporting/estimate-vs-budget', docType: 'Budget' },
          { label: 'Committed and Forecast Costs', route: '/portal/reporting/forecast-costs', docType: 'Purchase Order' },
          { label: 'Variation Summary', route: '/portal/reporting/variation-summary', docType: 'Project' },
        ]
      },
      {
        title: 'Procurement and Inventory',
        items: [
          { label: 'Stock Balance', route: '/portal/reporting/stock-balance-report', docType: 'Stock Ledger Entry' },
          { label: 'Stock Ledger', route: '/portal/reporting/stock-ledger-report', docType: 'Stock Ledger Entry' },
          { label: 'Stock Ageing', route: '/portal/reporting/stock-ageing-report', docType: 'Stock Ledger Entry' },
          { label: 'Procurement Status by Project', route: '/portal/reporting/procurement-status', docType: 'Purchase Order' },
          { label: 'Subcontract Commitment and Payment Summary', route: '/portal/reporting/subcontract-summary', docType: 'Purchase Order' },
          { label: 'Material Consumption vs BOQ', route: '/portal/reporting/material-consumption', docType: 'Stock Entry' },
        ]
      },
      {
        title: 'Planning and Billing',
        items: [
          { label: 'Planned vs Actual Progress', route: '/portal/reporting/planned-vs-actual', docType: 'Project' },
          { label: 'Project S-Curves', route: '/portal/reporting/s-curves-report', docType: 'Project' },
          { label: 'Claimed vs Certified vs Invoiced', route: '/portal/reporting/billing-comparison', docType: 'Sales Invoice' },
          { label: 'Collections and Retention Summary', route: '/portal/reporting/retention-summary', docType: 'Sales Invoice' },
          { label: 'Unbilled Work Summary', route: '/portal/reporting/unbilled-summary', docType: 'Sales Invoice' },
        ]
      },
      {
        title: 'People, Fabrication, and Equipment',
        items: [
          { label: 'Attendance Reports', route: '/portal/reporting/attendance-summary', docType: 'Attendance' },
          { label: 'Salary Register', route: '/portal/reporting/salary-summary', docType: 'Salary Slip' },
          { label: 'Manpower and Productivity', route: '/portal/reporting/productivity-report', docType: 'Timesheet' },
          { label: 'Fabrication Progress', route: '/portal/reporting/fabrication-progress', docType: 'Work Order' },
          { label: 'Equipment Utilization and Cost', route: '/portal/reporting/equipment-utilization', docType: 'Asset' },
        ]
      },
      {
        title: 'Warranty and Defects Liability',
        items: [
          { label: 'Active and Expiring Product Warranties', route: '/portal/reporting/active-warranties', docType: 'Warranty Claim' },
          { label: 'Open and Overdue Warranty Claims', route: '/portal/reporting/overdue-warranties', docType: 'Warranty Claim' },
          { label: 'Supplier Warranty Claims and Recoveries', route: '/portal/reporting/supplier-warranty-recoveries', docType: 'Warranty Claim' },
          { label: 'Project Warranty and Defects Liability Expiry', route: '/portal/reporting/defects-expiry', docType: 'Warranty Claim' },
          { label: 'Outstanding Defect Rectifications', route: '/portal/reporting/outstanding-defects', docType: 'Warranty Claim' },
          { label: 'Warranty Costs by Project and Product', route: '/portal/reporting/warranty-costs', docType: 'Warranty Claim' },
        ]
      },
      {
        title: 'Financial Statements',
        items: [
          { label: 'General Ledger', route: '/portal/reporting/gl-report', docType: 'GL Entry' },
          { label: 'Trial Balance', route: '/portal/reporting/tb-report', docType: 'GL Entry' },
          { label: 'Accounts Receivable', route: '/portal/reporting/ar-report', docType: 'Sales Invoice' },
          { label: 'Accounts Payable', route: '/portal/reporting/ap-report', docType: 'Purchase Invoice' },
          { label: 'Profit and Loss Statement', route: '/portal/reporting/pnl-report', docType: 'GL Entry' },
          { label: 'Balance Sheet', route: '/portal/reporting/bs-report', docType: 'GL Entry' },
          { label: 'Cash Flow Statement', route: '/portal/reporting/cashflow-report', docType: 'GL Entry' },
        ]
      }
    ]
  }
]
