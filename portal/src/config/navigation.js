export const WORKSPACES = [
  {
    "id": "project-management",
    "number": "01",
    "label": "Project Management",
    "description": "Project register, deliverables, RFIs, quality inspections, snag lists, and defect liability.",
    "route": "/portal/project-management",
    "icon": "FolderKanban",
    "required_roles": [
      "Projects User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Project Setup",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/project-management/dashboard",
            "docType": "Project",
            "viewType": "dashboard"
          },
          {
            "label": "Project Register",
            "route": "/portal/project-management/project-register",
            "docType": "Project"
          },
          {
            "label": "Client & Consultant Directory",
            "route": "/portal/project-management/client-consultant-directory",
            "docType": "Customer"
          },
          {
            "label": "Project Contracts",
            "route": "/portal/project-management/project-contracts",
            "docType": "BOQ"
          },
          {
            "label": "Project Team & Responsibilities",
            "route": "/portal/project-management/project-team",
            "docType": "Project User"
          },
          {
            "label": "Project Scope & Deliverables",
            "route": "/portal/project-management/project-scope",
            "docType": "Task"
          },
          {
            "label": "Work Breakdown Structure (WBS)",
            "route": "/portal/project-management/wbs",
            "docType": "Task"
          }
        ]
      },
      {
        "title": "Documents and Coordination",
        "items": [
          {
            "label": "Project Documents & Drawings",
            "route": "/portal/project-management/documents-drawings",
            "docType": "File"
          },
          {
            "label": "Requests for Information (RFIs)",
            "route": "/portal/project-management/rfis",
            "docType": "Request for Information"
          },
          {
            "label": "Material & Technical Submittals",
            "route": "/portal/project-management/submittals",
            "docType": "Technical Submittal"
          },
          {
            "label": "Meeting Minutes & Action Items",
            "route": "/portal/project-management/meeting-minutes",
            "docType": "Communication"
          }
        ]
      },
      {
        "title": "Controls and Quality",
        "items": [
          {
            "label": "Risks & Issues",
            "route": "/portal/project-management/risks-issues",
            "docType": "Issue"
          },
          {
            "label": "Change & Variation Register",
            "route": "/portal/project-management/variation-register",
            "docType": "Project Variation"
          },
          {
            "label": "Quality Inspections & NCRs",
            "route": "/portal/project-management/quality-inspections",
            "docType": "Quality Inspection"
          }
        ]
      },
      {
        "title": "Handover",
        "items": [
          {
            "label": "Snag & Punch Lists",
            "route": "/portal/project-management/snag-lists",
            "docType": "Snag List"
          },
          {
            "label": "Project Handover & Closeout",
            "route": "/portal/project-management/project-handover",
            "docType": "Project Handover"
          }
        ]
      },
      {
        "title": "Project Warranties and Defects Liability",
        "items": [
          {
            "label": "Project Warranty Register",
            "route": "/portal/project-management/warranty-register",
            "docType": "Project Warranty"
          },
          {
            "label": "Workmanship Warranties",
            "route": "/portal/project-management/workmanship-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Certificates",
            "route": "/portal/project-management/warranty-certificates",
            "docType": "Warranty Register"
          },
          {
            "label": "Defects Liability Periods",
            "route": "/portal/project-management/defects-liability-periods",
            "docType": "Project Warranty"
          },
          {
            "label": "Defect Notices & Rectification",
            "route": "/portal/project-management/defect-notices",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Closeout",
            "route": "/portal/project-management/warranty-closeout",
            "docType": "Project Warranty"
          }
        ]
      }
    ]
  },
  {
    "id": "estimation-cost-control",
    "number": "02",
    "label": "Estimation and Cost Control",
    "description": "Control project tendering, BOQ, rate analysis, and budget monitoring.",
    "route": "/portal/estimation-cost-control",
    "icon": "Calculator",
    "required_roles": [
      "Projects User",
      "Accounts User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Rates and Estimates",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/estimation-cost-control/dashboard",
            "docType": "Budget",
            "viewType": "dashboard"
          },
          {
            "label": "Cost Codes & Cost Centers",
            "route": "/portal/estimation-cost-control/cost-codes",
            "docType": "Cost Center"
          },
          {
            "label": "Material & Labour Rates",
            "route": "/portal/estimation-cost-control/rates",
            "docType": "Item Price"
          },
          {
            "label": "Bill of Quantities (BOQ)",
            "route": "/portal/estimation-cost-control/boq",
            "docType": "BOQ"
          },
          {
            "label": "Rate Analysis",
            "route": "/portal/estimation-cost-control/rate-analysis",
            "docType": "Item"
          },
          {
            "label": "Customer Quotations (Estimates)",
            "route": "/portal/estimation-cost-control/project-estimates",
            "docType": "Quotation"
          },
          {
            "label": "Customer Quotations (Tender Pricing)",
            "route": "/portal/estimation-cost-control/tender-pricing",
            "docType": "Quotation"
          }
        ]
      },
      {
        "title": "Budget Control",
        "items": [
          {
            "label": "Project Budget",
            "route": "/portal/estimation-cost-control/project-budget",
            "docType": "Budget"
          },
          {
            "label": "Budget Revisions & Transfers",
            "route": "/portal/estimation-cost-control/budget-revisions",
            "docType": "Budget"
          },
          {
            "label": "Committed Costs",
            "route": "/portal/estimation-cost-control/committed-costs",
            "docType": "Finance Commitment"
          },
          {
            "label": "Actual Costs (GL)",
            "route": "/portal/estimation-cost-control/actual-costs",
            "docType": "GL Entry"
          }
        ]
      },
      {
        "title": "Analysis and Forecasts",
        "items": [
          {
            "label": "Budget vs. Actual",
            "route": "/portal/estimation-cost-control/budget-vs-actual",
            "docType": "Budget"
          },
          {
            "label": "Cost Forecast & Cost to Complete",
            "route": "/portal/estimation-cost-control/cost-forecast",
            "docType": "Project"
          },
          {
            "label": "Variation Cost Analysis",
            "route": "/portal/estimation-cost-control/variation-cost-analysis",
            "docType": "Project Variation"
          },
          {
            "label": "Warranty & Defect Costs",
            "route": "/portal/estimation-cost-control/warranty-costs",
            "docType": "Warranty Claim"
          }
        ]
      }
    ]
  },
  {
    "id": "planning",
    "number": "03",
    "label": "Planning",
    "description": "Baseline programmes, look-ahead plans, resource requirements, and progress curves.",
    "route": "/portal/planning",
    "icon": "Calendar",
    "required_roles": [
      "Projects User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Programme Setup",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/planning/dashboard",
            "docType": "Project",
            "viewType": "dashboard"
          },
          {
            "label": "Working Calendars",
            "route": "/portal/planning/working-calendars",
            "docType": "Task"
          },
          {
            "label": "Activities & Dependencies",
            "route": "/portal/planning/activities-dependencies",
            "docType": "Task"
          },
          {
            "label": "Baseline Programme",
            "route": "/portal/planning/baseline-programme",
            "docType": "Project"
          },
          {
            "label": "Milestones",
            "route": "/portal/planning/milestones",
            "docType": "Task"
          }
        ]
      },
      {
        "title": "Schedules and Resources",
        "items": [
          {
            "label": "Current Programme & Updates",
            "route": "/portal/planning/current-programme",
            "docType": "Project"
          },
          {
            "label": "Look-Ahead Plans",
            "route": "/portal/planning/look-ahead-plans",
            "docType": "Task"
          },
          {
            "label": "Manpower Planning",
            "route": "/portal/planning/manpower-planning",
            "docType": "Daily Manpower Register"
          },
          {
            "label": "Material Requirements (MRP)",
            "route": "/portal/planning/mrp",
            "docType": "Material Request"
          },
          {
            "label": "Equipment Requirements",
            "route": "/portal/planning/equipment-planning",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Procurement Schedule",
            "route": "/portal/planning/procurement-schedule",
            "docType": "Purchase Order"
          },
          {
            "label": "Fabrication & Delivery Schedule",
            "route": "/portal/planning/fabrication-schedule",
            "docType": "Work Order"
          }
        ]
      },
      {
        "title": "Progress Analysis",
        "items": [
          {
            "label": "Planned vs. Actual Progress",
            "route": "/portal/planning/planned-vs-actual-progress",
            "docType": "Project"
          },
          {
            "label": "Progress Curves",
            "route": "/portal/planning/progress-curves",
            "docType": "Project"
          },
          {
            "label": "Delay & Recovery Plans",
            "route": "/portal/planning/delay-recovery-plans",
            "docType": "Task"
          }
        ]
      }
    ]
  },
  {
    "id": "procurement-subcontractors",
    "number": "04",
    "label": "Procurement and Subcontractors",
    "description": "Supplier directories, RFQs, purchase orders, subcontractor progress claims, and warranties.",
    "route": "/portal/procurement-subcontractors",
    "icon": "ShoppingCart",
    "required_roles": [
      "Stock User",
      "Purchase User",
      "Accounts User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Partners and Sourcing",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/procurement-subcontractors/dashboard",
            "docType": "Purchase Order",
            "viewType": "dashboard"
          },
          {
            "label": "Supplier & Subcontractor Directory",
            "route": "/portal/procurement-subcontractors/supplier-directory",
            "docType": "Supplier"
          },
          {
            "label": "Supplier Prequalification",
            "route": "/portal/procurement-subcontractors/prequalification",
            "docType": "Supplier"
          },
          {
            "label": "Material Requisitions",
            "route": "/portal/procurement-subcontractors/requisitions",
            "docType": "Material Request"
          },
          {
            "label": "Requests for Quotation (RFQs)",
            "route": "/portal/procurement-subcontractors/rfqs",
            "docType": "Request for Quotation"
          },
          {
            "label": "Supplier Quotation",
            "route": "/portal/procurement-subcontractors/supplier-quotations",
            "docType": "Supplier Quotation"
          },
          {
            "label": "Quotation Comparison",
            "route": "/portal/procurement-subcontractors/quotation-comparison",
            "docType": "Supplier Quotation"
          }
        ]
      },
      {
        "title": "Orders and Deliveries",
        "items": [
          {
            "label": "Purchase Orders",
            "route": "/portal/procurement-subcontractors/purchase-orders",
            "docType": "Purchase Order"
          },
          {
            "label": "Subcontract Agreements",
            "route": "/portal/procurement-subcontractors/subcontract-agreements",
            "docType": "Subcontract Agreement"
          },
          {
            "label": "Delivery & Expediting Schedule",
            "route": "/portal/procurement-subcontractors/delivery-schedule",
            "docType": "Purchase Receipt"
          },
          {
            "label": "Goods & Service Acceptance",
            "route": "/portal/procurement-subcontractors/goods-acceptance",
            "docType": "Purchase Receipt"
          },
          {
            "label": "Purchase Returns",
            "route": "/portal/procurement-subcontractors/purchase-returns",
            "docType": "Purchase Receipt"
          }
        ]
      },
      {
        "title": "Subcontract Control",
        "items": [
          {
            "label": "Subcontractor Progress Claims",
            "route": "/portal/procurement-subcontractors/progress-claims",
            "docType": "Subcontract Progress Claim"
          },
          {
            "label": "Subcontractor Payment Certificates",
            "route": "/portal/procurement-subcontractors/payment-certificates",
            "docType": "Payment Certificate"
          },
          {
            "label": "Subcontract Variations",
            "route": "/portal/procurement-subcontractors/subcontract-variations",
            "docType": "Subcontract Progress Claim"
          },
          {
            "label": "Supplier Performance",
            "route": "/portal/procurement-subcontractors/supplier-performance",
            "docType": "Supplier"
          }
        ]
      },
      {
        "title": "Supplier and Subcontractor Warranties",
        "items": [
          {
            "label": "Supplier Warranty Register",
            "route": "/portal/procurement-subcontractors/supplier-warranty-register",
            "docType": "Warranty Register"
          },
          {
            "label": "Manufacturer Warranty Certificates",
            "route": "/portal/procurement-subcontractors/manufacturer-certificates",
            "docType": "File"
          },
          {
            "label": "Subcontractor Workmanship Warranties",
            "route": "/portal/procurement-subcontractors/subcontractor-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Claims Against Suppliers",
            "route": "/portal/procurement-subcontractors/warranty-claims-suppliers",
            "docType": "Warranty Claim"
          },
          {
            "label": "Repair & Replacement Follow-Up",
            "route": "/portal/procurement-subcontractors/repair-followup",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Cost Recovery",
            "route": "/portal/procurement-subcontractors/warranty-cost-recovery",
            "docType": "Warranty Claim"
          }
        ]
      }
    ]
  },
  {
    "id": "inventory-management",
    "number": "05",
    "label": "Inventory Management",
    "description": "Warehouse stores, material movements, physical counts, stock valuation, and product warranties.",
    "route": "/portal/inventory-management",
    "icon": "Boxes",
    "required_roles": [
      "Stock User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Inventory Setup",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/inventory-management/dashboard",
            "docType": "Stock Entry",
            "viewType": "dashboard"
          },
          {
            "label": "Item Catalog",
            "route": "/portal/inventory-management/item-catalog",
            "docType": "Item"
          },
          {
            "label": "Item Categories & UOM",
            "route": "/portal/inventory-management/categories-uom",
            "docType": "Item Group"
          },
          {
            "label": "Warehouses & Project Stores",
            "route": "/portal/inventory-management/warehouses",
            "docType": "Warehouse"
          },
          {
            "label": "Reorder Levels",
            "route": "/portal/inventory-management/reorder-levels",
            "docType": "Item"
          }
        ]
      },
      {
        "title": "Material Movements",
        "items": [
          {
            "label": "Material Receipts",
            "route": "/portal/inventory-management/material-receipts",
            "docType": "Purchase Receipt"
          },
          {
            "label": "Material Issues to Projects",
            "route": "/portal/inventory-management/material-issues",
            "docType": "Stock Entry"
          },
          {
            "label": "Material Transfers",
            "route": "/portal/inventory-management/material-transfers",
            "docType": "Stock Entry"
          },
          {
            "label": "Material Returns",
            "route": "/portal/inventory-management/material-returns",
            "docType": "Stock Entry"
          },
          {
            "label": "Stock Reservations",
            "route": "/portal/inventory-management/stock-reservations",
            "docType": "Material Request"
          }
        ]
      },
      {
        "title": "Stock Control",
        "items": [
          {
            "label": "Stock Adjustments",
            "route": "/portal/inventory-management/stock-adjustments",
            "docType": "Stock Reconciliation"
          },
          {
            "label": "Physical Stock Count",
            "route": "/portal/inventory-management/physical-stock-count",
            "docType": "Stock Reconciliation"
          },
          {
            "label": "Batch & Serial Number Tracking",
            "route": "/portal/inventory-management/batch-serial-tracking",
            "docType": "Batch"
          },
          {
            "label": "Scrap & Damaged Materials",
            "route": "/portal/inventory-management/scrap-damaged-materials",
            "docType": "Stock Entry"
          },
          {
            "label": "Stock Balance & Valuation",
            "route": "/portal/inventory-management/stock-balance-valuation",
            "docType": "Stock Ledger Entry"
          }
        ]
      },
      {
        "title": "Product Warranty and After-Sales Service",
        "items": [
          {
            "label": "Product Warranty Details",
            "route": "/portal/inventory-management/product-warranty-details",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty & AMC Expiry Dates",
            "route": "/portal/inventory-management/warranty-expiry-dates",
            "docType": "Warranty Claim"
          },
          {
            "label": "Customer Warranty Claims",
            "route": "/portal/inventory-management/customer-warranty-claims",
            "docType": "Warranty Claim"
          },
          {
            "label": "Maintenance Visits",
            "route": "/portal/inventory-management/maintenance-visits",
            "docType": "Warranty Claim"
          },
          {
            "label": "Product Warranty Certificates",
            "route": "/portal/inventory-management/product-warranty-certificates",
            "docType": "File"
          },
          {
            "label": "Warranty Expiry Alerts",
            "route": "/portal/inventory-management/warranty-expiry-alerts",
            "docType": "Warranty Claim"
          },
          {
            "label": "Supplier Warranty Register",
            "route": "/portal/inventory-management/supplier-warranty-reg",
            "docType": "Warranty Register"
          }
        ]
      }
    ]
  },
  {
    "id": "hr-manpower",
    "number": "06",
    "label": "HR and Manpower",
    "description": "Employee directory, site deployments, attendance, timesheets, and payroll.",
    "route": "/portal/hr-manpower",
    "icon": "Users",
    "required_roles": [
      "HR User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Employee Records",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/hr-manpower/dashboard",
            "docType": "Employee",
            "viewType": "dashboard"
          },
          {
            "label": "Employee Directory",
            "route": "/portal/hr-manpower/employee-directory",
            "docType": "Employee"
          },
          {
            "label": "Departments & Designations",
            "route": "/portal/hr-manpower/departments-designations",
            "docType": "Department"
          },
          {
            "label": "Employment Contracts",
            "route": "/portal/hr-manpower/employment-contracts",
            "docType": "Employee"
          },
          {
            "label": "Recruitment & Onboarding",
            "route": "/portal/hr-manpower/recruitment-onboarding",
            "docType": "Employee"
          }
        ]
      },
      {
        "title": "Deployment and Time",
        "items": [
          {
            "label": "Project & Site Assignments",
            "route": "/portal/hr-manpower/site-assignments",
            "docType": "Employee"
          },
          {
            "label": "Shifts & Rosters",
            "route": "/portal/hr-manpower/shifts-rosters",
            "docType": "Attendance"
          },
          {
            "label": "Attendance",
            "route": "/portal/hr-manpower/attendance",
            "docType": "Attendance"
          },
          {
            "label": "Timesheets",
            "route": "/portal/hr-manpower/timesheets",
            "docType": "Timesheet"
          },
          {
            "label": "Overtime",
            "route": "/portal/hr-manpower/overtime",
            "docType": "Timesheet"
          },
          {
            "label": "Leave Management",
            "route": "/portal/hr-manpower/leave-management",
            "docType": "Leave Application"
          }
        ]
      },
      {
        "title": "Pay and Employee Services",
        "items": [
          {
            "label": "Payroll",
            "route": "/portal/hr-manpower/payroll",
            "docType": "Salary Slip"
          },
          {
            "label": "Employee Loans & Advances",
            "route": "/portal/hr-manpower/employee-advances",
            "docType": "Expense Claim"
          },
          {
            "label": "Document Expiry Tracking",
            "route": "/portal/hr-manpower/document-expiry",
            "docType": "Employee"
          },
          {
            "label": "Training & Certifications",
            "route": "/portal/hr-manpower/training-certifications",
            "docType": "Employee"
          },
          {
            "label": "Employee Exit & Settlement",
            "route": "/portal/hr-manpower/employee-exit",
            "docType": "Employee"
          }
        ]
      },
      {
        "title": "User Access & Permissions",
        "admin_only": true,
        "items": [
          {
            "label": "User Management & User Creation",
            "route": "/portal/administration/users",
            "docType": "User"
          },
          {
            "label": "Role Permission Manager",
            "route": "/portal/administration/role-permissions",
            "docType": "Custom DocPerm"
          }
        ]
      }
    ]
  },
  {
    "id": "fabrication-assets-equipment",
    "number": "07",
    "label": "Fabrication, Assets, and Equipment Management",
    "description": "Shop drawings, BOMs, work orders, site assets, plant machinery, and equipment usage.",
    "route": "/portal/fabrication-assets-equipment",
    "icon": "Factory",
    "required_roles": [
      "Manufacturing User",
      "Stock User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Fabrication Setup",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/fabrication-assets-equipment/dashboard",
            "docType": "Work Order",
            "viewType": "dashboard"
          },
          {
            "label": "Fabrication Job Register",
            "route": "/portal/fabrication-assets-equipment/job-register",
            "docType": "PSS Skid Tracker"
          },
          {
            "label": "Shop Drawings & Revisions",
            "route": "/portal/fabrication-assets-equipment/shop-drawings",
            "docType": "File"
          },
          {
            "label": "Bills of Materials (BOM)",
            "route": "/portal/fabrication-assets-equipment/boms",
            "docType": "BOM"
          },
          {
            "label": "Production Routes & Operations",
            "route": "/portal/fabrication-assets-equipment/production-routes",
            "docType": "Work Order"
          },
          {
            "label": "Fabrication Work Orders",
            "route": "/portal/fabrication-assets-equipment/work-orders",
            "docType": "Work Order"
          }
        ]
      },
      {
        "title": "Production and Dispatch",
        "items": [
          {
            "label": "Material Requests & Consumption",
            "route": "/portal/fabrication-assets-equipment/material-requests-consumption",
            "docType": "Material Request"
          },
          {
            "label": "Production Planning",
            "route": "/portal/fabrication-assets-equipment/production-planning",
            "docType": "Work Order"
          },
          {
            "label": "Daily Production & Labour Recording",
            "route": "/portal/fabrication-assets-equipment/daily-production-recording",
            "docType": "Job Card"
          },
          {
            "label": "Quality Inspections & Rework",
            "route": "/portal/fabrication-assets-equipment/quality-inspections-rework",
            "docType": "Quality Inspection"
          },
          {
            "label": "Factory Acceptance Test (FAT)",
            "route": "/portal/fabrication-assets-equipment/fat",
            "docType": "Factory Acceptance Test"
          },
          {
            "label": "Integrated Factory Acceptance Test (IFAT)",
            "route": "/portal/fabrication-assets-equipment/ifat",
            "docType": "Integrated Factory Acceptance Test"
          },
          {
            "label": "Finished Goods",
            "route": "/portal/fabrication-assets-equipment/finished-goods",
            "docType": "Stock Entry"
          },
          {
            "label": "Dispatch to Site",
            "route": "/portal/fabrication-assets-equipment/dispatch-to-site",
            "docType": "Stock Entry"
          }
        ]
      },
      {
        "title": "Assets",
        "items": [
          {
            "label": "Asset Register & Categories",
            "route": "/portal/fabrication-assets-equipment/asset-register",
            "docType": "Asset"
          },
          {
            "label": "Asset Acquisition & Capitalization",
            "route": "/portal/fabrication-assets-equipment/asset-acquisition",
            "docType": "Asset"
          },
          {
            "label": "Asset Assignment & Custody",
            "route": "/portal/fabrication-assets-equipment/asset-assignment",
            "docType": "Asset Movement"
          },
          {
            "label": "Asset Transfers",
            "route": "/portal/fabrication-assets-equipment/asset-transfers",
            "docType": "Asset Movement"
          },
          {
            "label": "Depreciation Schedule",
            "route": "/portal/fabrication-assets-equipment/asset-depreciation",
            "docType": "Asset"
          },
          {
            "label": "Asset Disposal",
            "route": "/portal/fabrication-assets-equipment/asset-disposal",
            "docType": "Asset"
          }
        ]
      },
      {
        "title": "Equipment",
        "items": [
          {
            "label": "Equipment Register",
            "route": "/portal/fabrication-assets-equipment/equipment-register",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Equipment Allocation & Mobilization",
            "route": "/portal/fabrication-assets-equipment/equipment-allocation",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Equipment Hire & Rental",
            "route": "/portal/fabrication-assets-equipment/equipment-hire",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Operator Assignments",
            "route": "/portal/fabrication-assets-equipment/operator-assignments",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Daily Usage & Meter Readings",
            "route": "/portal/fabrication-assets-equipment/daily-usage",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Fuel Consumption Log",
            "route": "/portal/fabrication-assets-equipment/fuel-consumption",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Preventive Maintenance",
            "route": "/portal/fabrication-assets-equipment/preventive-maintenance",
            "docType": "Asset Maintenance"
          },
          {
            "label": "Breakdowns & Repairs",
            "route": "/portal/fabrication-assets-equipment/breakdowns-repairs",
            "docType": "Asset Maintenance"
          },
          {
            "label": "Inspections & Certificate Expiry",
            "route": "/portal/fabrication-assets-equipment/inspections-certificate-expiry",
            "docType": "Equipment Usage Log"
          },
          {
            "label": "Utilization & Operating Costs",
            "route": "/portal/fabrication-assets-equipment/utilization-operating-costs",
            "docType": "Equipment Usage Log"
          }
        ]
      },
      {
        "title": "Warranty and Service",
        "items": [
          {
            "label": "Manufactured Product Warranty Claims",
            "route": "/portal/fabrication-assets-equipment/mfg-warranty-claims",
            "docType": "Warranty Claim"
          },
          {
            "label": "Asset & Equipment Warranties",
            "route": "/portal/fabrication-assets-equipment/asset-supplier-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Certificates",
            "route": "/portal/fabrication-assets-equipment/equipment-warranty-certs",
            "docType": "File"
          },
          {
            "label": "Warranty Repair Tracking",
            "route": "/portal/fabrication-assets-equipment/warranty-repair-tracking",
            "docType": "Warranty Claim"
          }
        ]
      }
    ]
  },
  {
    "id": "project-progress-billing",
    "number": "08",
    "label": "Project Progress and Billing",
    "description": "Site measurements, progress certificates, advance recovery, retention release, and invoicing.",
    "route": "/portal/project-progress-billing",
    "icon": "Receipt",
    "required_roles": [
      "Projects User",
      "Accounts User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Measurement and Progress",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/project-progress-billing/dashboard",
            "docType": "Sales Invoice",
            "viewType": "dashboard"
          },
          {
            "label": "Contract BOQ & Billing Schedule",
            "route": "/portal/project-progress-billing/contract-boq-schedule",
            "docType": "BOQ"
          },
          {
            "label": "Site Measurements",
            "route": "/portal/project-progress-billing/site-measurements",
            "docType": "Site Measurement Item"
          },
          {
            "label": "Work Completion Records",
            "route": "/portal/project-progress-billing/work-completion-records",
            "docType": "Task"
          },
          {
            "label": "Progress Quantities & Percentages",
            "route": "/portal/project-progress-billing/progress-quantities-percentages",
            "docType": "Progress Claim"
          }
        ]
      },
      {
        "title": "Claims and Certification",
        "items": [
          {
            "label": "Client Progress Claims",
            "route": "/portal/project-progress-billing/client-progress-claims",
            "docType": "Progress Claim"
          },
          {
            "label": "Client Payment Certificates",
            "route": "/portal/project-progress-billing/client-payment-certificates",
            "docType": "Payment Certificate"
          },
          {
            "label": "Approved Variations for Billing",
            "route": "/portal/project-progress-billing/approved-variations-billing",
            "docType": "Project Variation"
          }
        ]
      },
      {
        "title": "Adjustments",
        "items": [
          {
            "label": "Advance Recovery",
            "route": "/portal/project-progress-billing/advance-recovery",
            "docType": "Sales Invoice"
          },
          {
            "label": "Retention Calculation & Release",
            "route": "/portal/project-progress-billing/retention-calculation-release",
            "docType": "Sales Invoice"
          },
          {
            "label": "Deductions & Adjustments",
            "route": "/portal/project-progress-billing/deductions-adjustments",
            "docType": "Sales Invoice"
          }
        ]
      },
      {
        "title": "Billing and Closeout",
        "items": [
          {
            "label": "Invoice Preparation & Dossier",
            "route": "/portal/project-progress-billing/invoice-preparation",
            "docType": "Invoice Dossier"
          },
          {
            "label": "Unbilled Work",
            "route": "/portal/project-progress-billing/unbilled-work",
            "docType": "Sales Invoice"
          },
          {
            "label": "Billing & Collection Status",
            "route": "/portal/project-progress-billing/billing-collection-status",
            "docType": "Sales Invoice"
          },
          {
            "label": "Final Account",
            "route": "/portal/project-progress-billing/final-account",
            "docType": "Sales Invoice"
          },
          {
            "label": "Handover & Defects Clearance",
            "route": "/portal/project-progress-billing/defects-clearance-retention",
            "docType": "Project Handover"
          }
        ]
      }
    ]
  },
  {
    "id": "accounting-finance",
    "number": "09",
    "label": "Accounting and Finance",
    "description": "Chart of accounts, sales & supplier invoices, payments, journal entries, and financial statements.",
    "route": "/portal/accounting-finance",
    "icon": "Landmark",
    "required_roles": [
      "Accounts User",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Finance Setup",
        "items": [
          {
            "label": "Dashboard",
            "route": "/portal/accounting-finance/dashboard",
            "docType": "Sales Invoice",
            "viewType": "dashboard"
          },
          {
            "label": "Chart of Accounts",
            "route": "/portal/accounting-finance/chart-of-accounts",
            "docType": "Account"
          },
          {
            "label": "Cost Centers",
            "route": "/portal/accounting-finance/cost-centers",
            "docType": "Cost Center"
          },
          {
            "label": "Customers",
            "route": "/portal/accounting-finance/customers",
            "docType": "Customer"
          },
          {
            "label": "Bank & Cash Accounts",
            "route": "/portal/accounting-finance/bank-cash-accounts",
            "docType": "Account"
          },
          {
            "label": "Taxes & Templates",
            "route": "/portal/accounting-finance/taxes",
            "docType": "Account"
          }
        ]
      },
      {
        "title": "Invoices and Payments",
        "items": [
          {
            "label": "Sales Invoices & Credit Notes",
            "route": "/portal/accounting-finance/sales-invoices-credit-notes",
            "docType": "Sales Invoice"
          },
          {
            "label": "Supplier Invoices & Debit Notes",
            "route": "/portal/accounting-finance/supplier-invoices-debit-notes",
            "docType": "Purchase Invoice"
          },
          {
            "label": "Payment Requests",
            "route": "/portal/accounting-finance/payment-requests",
            "docType": "Payment Request"
          },
          {
            "label": "Payments & Receipts",
            "route": "/portal/accounting-finance/payments-receipts",
            "docType": "Payment Entry"
          },
          {
            "label": "Employee Expenses & Advances",
            "route": "/portal/accounting-finance/employee-expenses-advances",
            "docType": "Expense Claim"
          },
          {
            "label": "Petty Cash Journal Entries",
            "route": "/portal/accounting-finance/petty-cash",
            "docType": "Journal Entry"
          }
        ]
      },
      {
        "title": "Accounting and Reconciliation",
        "items": [
          {
            "label": "Journal Entries",
            "route": "/portal/accounting-finance/journal-entries",
            "docType": "Journal Entry"
          },
          {
            "label": "Bank Reconciliation",
            "route": "/portal/accounting-finance/bank-reconciliation",
            "docType": "Journal Entry"
          },
          {
            "label": "Accounts Receivable & Payable",
            "route": "/portal/accounting-finance/ar-ap",
            "docType": "GL Entry"
          },
          {
            "label": "Retention & Advance Balances",
            "route": "/portal/accounting-finance/retention-advance-balances",
            "docType": "GL Entry"
          }
        ]
      },
      {
        "title": "Reporting and Closing",
        "items": [
          {
            "label": "Financial Statements",
            "route": "/portal/accounting-finance/financial-statements",
            "docType": "GL Entry"
          },
          {
            "label": "Period Closing Vouchers",
            "route": "/portal/accounting-finance/period-closing",
            "docType": "Period Closing Voucher"
          }
        ]
      },
      {
        "title": "Construction Finance",
        "items": [
          {
            "label": "Retention Receivable/Payable Schedule",
            "route": "/portal/accounting-finance/retention-receivable-payable-schedule",
            "docType": "GL Entry"
          },
          {
            "label": "Advance Recovery Schedule",
            "route": "/portal/accounting-finance/advance-recovery-schedule",
            "docType": "GL Entry"
          },
          {
            "label": "Project Accrual & WIP Review",
            "route": "/portal/accounting-finance/project-accrual-wip-review",
            "docType": "GL Entry"
          },
          {
            "label": "Project Cash Flow Forecast",
            "route": "/portal/accounting-finance/project-cash-flow-forecast",
            "docType": "GL Entry"
          },
          {
            "label": "Warranty Costs & Recoveries",
            "route": "/portal/accounting-finance/warranty-costs-supplier-recoveries",
            "docType": "Warranty Claim"
          }
        ]
      }
    ]
  },
  {
    "id": "reporting",
    "number": "10",
    "label": "Reporting",
    "description": "Executive dashboards, cost analytics, procurement metrics, and financial statements.",
    "route": "/portal/reporting",
    "icon": "BarChart3",
    "required_roles": [
      "Projects User",
      "Accounts User",
      "Management Viewer",
      "Portal Administrator",
      "System Manager"
    ],
    "sections": [
      {
        "title": "Management",
        "items": [
          {
            "label": "Management Dashboard",
            "route": "/portal/reporting/management-dashboard",
            "docType": "Project",
            "viewType": "dashboard"
          },
          {
            "label": "Project Performance Summary",
            "route": "/portal/reporting/project-performance-summary",
            "docType": "Project"
          },
          {
            "label": "Financial Reports",
            "route": "/portal/reporting/financial-reports",
            "docType": "GL Entry"
          },
          {
            "label": "Cash Flow Reports",
            "route": "/portal/reporting/cash-flow-reports",
            "docType": "GL Entry"
          }
        ]
      },
      {
        "title": "Projects and Commercial",
        "items": [
          {
            "label": "Budget & Cost Reports",
            "route": "/portal/reporting/budget-cost-reports",
            "docType": "Budget"
          },
          {
            "label": "Progress & Productivity Reports",
            "route": "/portal/reporting/progress-productivity-reports",
            "docType": "Task"
          },
          {
            "label": "Billing & Collection Reports",
            "route": "/portal/reporting/billing-collection-reports",
            "docType": "Sales Invoice"
          }
        ]
      },
      {
        "title": "Operations and Resources",
        "items": [
          {
            "label": "Procurement & Subcontractor Reports",
            "route": "/portal/reporting/procurement-subcontractor-reports",
            "docType": "Purchase Order"
          },
          {
            "label": "Inventory Reports",
            "route": "/portal/reporting/inventory-reports",
            "docType": "Stock Ledger Entry"
          },
          {
            "label": "HR & Manpower Reports",
            "route": "/portal/reporting/hr-manpower-reports",
            "docType": "Attendance"
          },
          {
            "label": "Fabrication Reports",
            "route": "/portal/reporting/fabrication-reports",
            "docType": "Work Order"
          },
          {
            "label": "Asset & Equipment Reports",
            "route": "/portal/reporting/asset-equipment-reports",
            "docType": "Asset"
          },
          {
            "label": "Custom Reports",
            "route": "/portal/reporting/custom-reports",
            "docType": "Project"
          }
        ]
      },
      {
        "title": "Warranty and Defects Liability",
        "items": [
          {
            "label": "Active & Expiring Warranties",
            "route": "/portal/reporting/active-expiring-product-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Open & Overdue Claims",
            "route": "/portal/reporting/open-overdue-warranty-claims",
            "docType": "Warranty Claim"
          },
          {
            "label": "Supplier Warranty Claims",
            "route": "/portal/reporting/supplier-warranty-claims-recoveries",
            "docType": "Warranty Claim"
          },
          {
            "label": "Project Warranty Expiry",
            "route": "/portal/reporting/project-warranty-defects-liability-expiry",
            "docType": "Warranty Claim"
          },
          {
            "label": "Defect Rectifications Log",
            "route": "/portal/reporting/outstanding-defect-rectifications",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Costs by Project",
            "route": "/portal/reporting/warranty-costs-by-project-product",
            "docType": "Warranty Claim"
          }
        ]
      }
    ]
  }
];

export function getWorkspaceById(id) {
  return WORKSPACES.find(w => w.id === id);
}

export function getAllWorkspaceRoutes() {
  const routes = [];
  WORKSPACES.forEach(w => {
    routes.push({ path: w.route, workspaceId: w.id });
    w.sections.forEach(s => {
      s.items.forEach(item => {
        routes.push({
          path: item.route,
          workspaceId: w.id,
          label: item.label,
          docType: item.docType,
          viewType: item.viewType || 'list'
        });
      });
    });
  });
  return routes;
}

export const workspaces = WORKSPACES;

export function getNavigationByDocType(docType) {
  for (const ws of WORKSPACES) {
    for (const sec of ws.sections || []) {
      for (const item of sec.items || []) {
        if (item.docType === docType && item.route && item.viewType !== 'dashboard') {
          return {
            workspaceId: ws.id,
            workspaceRoute: ws.route,
            moduleRoute: item.route,
            label: item.label,
            docType: item.docType
          };
        }
      }
    }
  }
  return null;
}

export function openDocument(docType, name, router, currentRoutePath = '') {

  const encodedName = encodeURIComponent(name);

  if (currentRoutePath && currentRoutePath.startsWith('/portal/')) {
    const cleanPath = currentRoutePath.split('?')[0].replace(/\/$/, '');
    const parts = cleanPath.split('/');
    if (parts.length === 4) {
      router.push();
      return;
    }
  }

  const navInfo = getNavigationByDocType(docType);
  if (navInfo && navInfo.moduleRoute) {
    router.push();
    return;
  }

  const fallbackMod = docType.toLowerCase().replace(/ /g, '-');
  router.push();
}
