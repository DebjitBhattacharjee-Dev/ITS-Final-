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
            "label": "Client and Consultant Directory",
            "route": "/portal/project-management/client-consultant-directory",
            "docType": "Customer"
          },
          {
            "label": "Project Contracts",
            "route": "/portal/project-management/project-contracts",
            "docType": "Project Contract BOQ"
          },
          {
            "label": "Project Team and Responsibilities",
            "route": "/portal/project-management/project-team",
            "docType": "Project User"
          },
          {
            "label": "Project Scope and Deliverables",
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
            "label": "Project Documents and Drawings",
            "route": "/portal/project-management/documents-drawings",
            "docType": "File"
          },
          {
            "label": "Requests for Information (RFIs)",
            "route": "/portal/project-management/rfis",
            "docType": "Issue"
          },
          {
            "label": "Material and Technical Submittals",
            "route": "/portal/project-management/submittals",
            "docType": "Item"
          },
          {
            "label": "Meeting Minutes and Action Items",
            "route": "/portal/project-management/meeting-minutes",
            "docType": "Communication"
          }
        ]
      },
      {
        "title": "Controls and Quality",
        "items": [
          {
            "label": "Risks and Issues",
            "route": "/portal/project-management/risks-issues",
            "docType": "Issue"
          },
          {
            "label": "Change and Variation Register",
            "route": "/portal/project-management/variation-register",
            "docType": "Task"
          },
          {
            "label": "Quality Inspections and Nonconformances",
            "route": "/portal/project-management/quality-inspections",
            "docType": "Quality Inspection"
          }
        ]
      },
      {
        "title": "Handover",
        "items": [
          {
            "label": "Snag and Punch Lists",
            "route": "/portal/project-management/snag-lists",
            "docType": "Issue"
          },
          {
            "label": "Project Handover and Closeout",
            "route": "/portal/project-management/project-handover",
            "docType": "Project"
          }
        ]
      },
      {
        "title": "Project Warranties and Defects Liability",
        "items": [
          {
            "label": "Project Warranty Register",
            "route": "/portal/project-management/warranty-register",
            "docType": "Warranty Claim"
          },
          {
            "label": "Workmanship and Installation Warranties",
            "route": "/portal/project-management/workmanship-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Certificates",
            "route": "/portal/project-management/warranty-certificates",
            "docType": "File"
          },
          {
            "label": "Defects Liability Periods",
            "route": "/portal/project-management/defects-liability-periods",
            "docType": "Project"
          },
          {
            "label": "Defect Notices and Rectification",
            "route": "/portal/project-management/defect-notices",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Closeout",
            "route": "/portal/project-management/warranty-closeout",
            "docType": "Warranty Claim"
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
            "label": "Cost Codes and Cost Categories",
            "route": "/portal/estimation-cost-control/cost-codes",
            "docType": "Cost Center"
          },
          {
            "label": "Material, Labour, and Equipment Rates",
            "route": "/portal/estimation-cost-control/rates",
            "docType": "Item Price"
          },
          {
            "label": "Bill of Quantities (BOQ)",
            "route": "/portal/estimation-cost-control/boq",
            "docType": "Project Contract BOQ"
          },
          {
            "label": "Rate Analysis",
            "route": "/portal/estimation-cost-control/rate-analysis",
            "docType": "Item"
          },
          {
            "label": "Project Estimates",
            "route": "/portal/estimation-cost-control/project-estimates",
            "docType": "Quotation"
          },
          {
            "label": "Tender Pricing and Quotations",
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
            "label": "Budget Revisions and Transfers",
            "route": "/portal/estimation-cost-control/budget-revisions",
            "docType": "Budget"
          },
          {
            "label": "Committed Costs",
            "route": "/portal/estimation-cost-control/committed-costs",
            "docType": "Purchase Order"
          },
          {
            "label": "Actual Costs",
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
            "label": "Cost Forecast and Cost to Complete",
            "route": "/portal/estimation-cost-control/cost-forecast",
            "docType": "Project"
          },
          {
            "label": "Variation Cost Analysis",
            "route": "/portal/estimation-cost-control/variation-cost-analysis",
            "docType": "Project"
          },
          {
            "label": "Warranty and Defect Rectification Costs",
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
            "label": "Activities and Dependencies",
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
            "label": "Current Programme and Updates",
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
            "docType": "Employee"
          },
          {
            "label": "Material Requirements Planning",
            "route": "/portal/planning/mrp",
            "docType": "Material Request"
          },
          {
            "label": "Equipment Requirements Planning",
            "route": "/portal/planning/equipment-planning",
            "docType": "Equipment Register"
          },
          {
            "label": "Procurement Schedule",
            "route": "/portal/planning/procurement-schedule",
            "docType": "Purchase Order"
          },
          {
            "label": "Fabrication and Delivery Schedule",
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
            "label": "Delay and Recovery Plans",
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
            "label": "Supplier and Subcontractor Directory",
            "route": "/portal/procurement-subcontractors/supplier-directory",
            "docType": "Supplier"
          },
          {
            "label": "Supplier and Subcontractor Prequalification",
            "route": "/portal/procurement-subcontractors/prequalification",
            "docType": "Supplier"
          },
          {
            "label": "Material and Service Requisitions",
            "route": "/portal/procurement-subcontractors/requisitions",
            "docType": "Material Request"
          },
          {
            "label": "Requests for Quotation",
            "route": "/portal/procurement-subcontractors/rfqs",
            "docType": "Request for Quotation"
          },
          {
            "label": "Supplier and Subcontractor Quotations",
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
            "label": "Subcontract Agreements and Work Orders",
            "route": "/portal/procurement-subcontractors/subcontract-agreements",
            "docType": "Purchase Order"
          },
          {
            "label": "Delivery and Expediting Schedule",
            "route": "/portal/procurement-subcontractors/delivery-schedule",
            "docType": "Purchase Receipt"
          },
          {
            "label": "Goods and Service Acceptance",
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
            "docType": "Subcontractor Progress Claim"
          },
          {
            "label": "Subcontractor Payment Certificates",
            "route": "/portal/procurement-subcontractors/payment-certificates",
            "docType": "Subcontractor Progress Claim"
          },
          {
            "label": "Subcontract Variations",
            "route": "/portal/procurement-subcontractors/subcontract-variations",
            "docType": "Purchase Order"
          },
          {
            "label": "Supplier and Subcontractor Performance",
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
            "docType": "Warranty Claim"
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
            "label": "Repair and Replacement Follow-Up",
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
            "label": "Item Categories and Units of Measure",
            "route": "/portal/inventory-management/categories-uom",
            "docType": "Item Group"
          },
          {
            "label": "Warehouses and Project Stores",
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
            "label": "Batch and Serial Number Tracking",
            "route": "/portal/inventory-management/batch-serial-tracking",
            "docType": "Batch"
          },
          {
            "label": "Scrap and Damaged Materials",
            "route": "/portal/inventory-management/scrap-damaged-materials",
            "docType": "Stock Entry"
          },
          {
            "label": "Stock Balance and Valuation",
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
            "label": "Warranty and AMC Expiry Dates",
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
            "docType": "Warranty Claim"
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
            "label": "Departments and Designations",
            "route": "/portal/hr-manpower/departments-designations",
            "docType": "Department"
          },
          {
            "label": "Employment Contracts and Documents",
            "route": "/portal/hr-manpower/employment-contracts",
            "docType": "Employee"
          },
          {
            "label": "Recruitment and Onboarding",
            "route": "/portal/hr-manpower/recruitment-onboarding",
            "docType": "Employee"
          }
        ]
      },
      {
        "title": "Deployment and Time",
        "items": [
          {
            "label": "Project and Site Assignments",
            "route": "/portal/hr-manpower/site-assignments",
            "docType": "Employee"
          },
          {
            "label": "Shifts and Rosters",
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
            "label": "Employee Loans and Advances",
            "route": "/portal/hr-manpower/employee-advances",
            "docType": "Expense Claim"
          },
          {
            "label": "Document Expiry Tracking",
            "route": "/portal/hr-manpower/document-expiry",
            "docType": "Employee"
          },
          {
            "label": "Training and Certifications",
            "route": "/portal/hr-manpower/training-certifications",
            "docType": "Employee"
          },
          {
            "label": "Employee Exit and Final Settlement",
            "route": "/portal/hr-manpower/employee-exit",
            "docType": "Employee"
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
            "docType": "Work Order"
          },
          {
            "label": "Shop Drawings and Revisions",
            "route": "/portal/fabrication-assets-equipment/shop-drawings",
            "docType": "File"
          },
          {
            "label": "Bills of Materials",
            "route": "/portal/fabrication-assets-equipment/boms",
            "docType": "BOM"
          },
          {
            "label": "Production Routes and Operations",
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
            "label": "Material Requests and Consumption",
            "route": "/portal/fabrication-assets-equipment/material-requests-consumption",
            "docType": "Material Request"
          },
          {
            "label": "Production Planning",
            "route": "/portal/fabrication-assets-equipment/production-planning",
            "docType": "Work Order"
          },
          {
            "label": "Daily Production and Labour Recording",
            "route": "/portal/fabrication-assets-equipment/daily-production-recording",
            "docType": "Job Card"
          },
          {
            "label": "Quality Inspections and Rework",
            "route": "/portal/fabrication-assets-equipment/quality-inspections-rework",
            "docType": "Quality Inspection"
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
            "label": "Asset Register and Categories",
            "route": "/portal/fabrication-assets-equipment/asset-register",
            "docType": "Asset"
          },
          {
            "label": "Asset Acquisition and Capitalization",
            "route": "/portal/fabrication-assets-equipment/asset-acquisition",
            "docType": "Asset"
          },
          {
            "label": "Asset Assignment and Custody",
            "route": "/portal/fabrication-assets-equipment/asset-assignment",
            "docType": "Asset Movement"
          },
          {
            "label": "Asset Transfers",
            "route": "/portal/fabrication-assets-equipment/asset-transfers",
            "docType": "Asset Movement"
          },
          {
            "label": "Depreciation",
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
            "docType": "Equipment Register"
          },
          {
            "label": "Equipment Allocation and Mobilization",
            "route": "/portal/fabrication-assets-equipment/equipment-allocation",
            "docType": "Equipment Register"
          },
          {
            "label": "Equipment Hire and Rental",
            "route": "/portal/fabrication-assets-equipment/equipment-hire",
            "docType": "Equipment Register"
          },
          {
            "label": "Operator Assignments",
            "route": "/portal/fabrication-assets-equipment/operator-assignments",
            "docType": "Equipment Register"
          },
          {
            "label": "Daily Usage and Meter Readings",
            "route": "/portal/fabrication-assets-equipment/daily-usage",
            "docType": "Equipment Register"
          },
          {
            "label": "Fuel Consumption",
            "route": "/portal/fabrication-assets-equipment/fuel-consumption",
            "docType": "Equipment Register"
          },
          {
            "label": "Preventive Maintenance",
            "route": "/portal/fabrication-assets-equipment/preventive-maintenance",
            "docType": "Asset Maintenance"
          },
          {
            "label": "Breakdowns and Repairs",
            "route": "/portal/fabrication-assets-equipment/breakdowns-repairs",
            "docType": "Asset Maintenance"
          },
          {
            "label": "Inspections and Certificate Expiry",
            "route": "/portal/fabrication-assets-equipment/inspections-certificate-expiry",
            "docType": "Equipment Register"
          },
          {
            "label": "Utilization and Operating Costs",
            "route": "/portal/fabrication-assets-equipment/utilization-operating-costs",
            "docType": "Equipment Register"
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
            "label": "Asset and Equipment Supplier Warranties",
            "route": "/portal/fabrication-assets-equipment/asset-supplier-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Certificates",
            "route": "/portal/fabrication-assets-equipment/equipment-warranty-certs",
            "docType": "File"
          },
          {
            "label": "Warranty Repair and Replacement Tracking",
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
            "label": "Contract BOQ and Billing Schedule",
            "route": "/portal/project-progress-billing/contract-boq-schedule",
            "docType": "Project Contract BOQ"
          },
          {
            "label": "Site Measurements",
            "route": "/portal/project-progress-billing/site-measurements",
            "docType": "Site Measurement"
          },
          {
            "label": "Work Completion Records",
            "route": "/portal/project-progress-billing/work-completion-records",
            "docType": "Task"
          },
          {
            "label": "Progress Quantities and Percentages",
            "route": "/portal/project-progress-billing/progress-quantities-percentages",
            "docType": "Project"
          }
        ]
      },
      {
        "title": "Claims and Certification",
        "items": [
          {
            "label": "Client Progress Claims",
            "route": "/portal/project-progress-billing/client-progress-claims",
            "docType": "Sales Order"
          },
          {
            "label": "Client Payment Certificates",
            "route": "/portal/project-progress-billing/client-payment-certificates",
            "docType": "Sales Order"
          },
          {
            "label": "Approved Variations for Billing",
            "route": "/portal/project-progress-billing/approved-variations-billing",
            "docType": "Project"
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
            "label": "Retention Calculation and Release",
            "route": "/portal/project-progress-billing/retention-calculation-release",
            "docType": "Sales Invoice"
          },
          {
            "label": "Deductions and Adjustments",
            "route": "/portal/project-progress-billing/deductions-adjustments",
            "docType": "Sales Invoice"
          }
        ]
      },
      {
        "title": "Billing and Closeout",
        "items": [
          {
            "label": "Invoice Preparation",
            "route": "/portal/project-progress-billing/invoice-preparation",
            "docType": "Sales Invoice"
          },
          {
            "label": "Unbilled Work",
            "route": "/portal/project-progress-billing/unbilled-work",
            "docType": "Sales Invoice"
          },
          {
            "label": "Billing and Collection Status",
            "route": "/portal/project-progress-billing/billing-collection-status",
            "docType": "Sales Invoice"
          },
          {
            "label": "Final Account",
            "route": "/portal/project-progress-billing/final-account",
            "docType": "Sales Invoice"
          },
          {
            "label": "Handover and Defects Clearance for Retention Release",
            "route": "/portal/project-progress-billing/defects-clearance-retention",
            "docType": "Project"
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
            "label": "Bank and Cash Accounts",
            "route": "/portal/accounting-finance/bank-cash-accounts",
            "docType": "Account"
          },
          {
            "label": "Taxes",
            "route": "/portal/accounting-finance/taxes",
            "docType": "Account"
          }
        ]
      },
      {
        "title": "Invoices and Payments",
        "items": [
          {
            "label": "Sales Invoices and Credit Notes",
            "route": "/portal/accounting-finance/sales-invoices-credit-notes",
            "docType": "Sales Invoice"
          },
          {
            "label": "Supplier Invoices and Debit Notes",
            "route": "/portal/accounting-finance/supplier-invoices-debit-notes",
            "docType": "Purchase Invoice"
          },
          {
            "label": "Payment Requests",
            "route": "/portal/accounting-finance/payment-requests",
            "docType": "Payment Entry"
          },
          {
            "label": "Payments and Receipts",
            "route": "/portal/accounting-finance/payments-receipts",
            "docType": "Payment Entry"
          },
          {
            "label": "Employee Expenses and Advances",
            "route": "/portal/accounting-finance/employee-expenses-advances",
            "docType": "Expense Claim"
          },
          {
            "label": "Petty Cash",
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
            "label": "Accounts Receivable and Payable",
            "route": "/portal/accounting-finance/ar-ap",
            "docType": "GL Entry"
          },
          {
            "label": "Retention and Advance Balances",
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
            "label": "Period Closing",
            "route": "/portal/accounting-finance/period-closing",
            "docType": "Period Closing Voucher"
          }
        ]
      },
      {
        "title": "Construction Finance",
        "items": [
          {
            "label": "Retention Receivable and Payable Schedule",
            "route": "/portal/accounting-finance/retention-receivable-payable-schedule",
            "docType": "GL Entry"
          },
          {
            "label": "Advance Recovery Schedule",
            "route": "/portal/accounting-finance/advance-recovery-schedule",
            "docType": "GL Entry"
          },
          {
            "label": "Project Accrual and WIP Review",
            "route": "/portal/accounting-finance/project-accrual-wip-review",
            "docType": "GL Entry"
          },
          {
            "label": "Project Cash Flow Forecast",
            "route": "/portal/accounting-finance/project-cash-flow-forecast",
            "docType": "GL Entry"
          },
          {
            "label": "Warranty Costs and Supplier Recoveries",
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
            "label": "Budget and Cost Reports",
            "route": "/portal/reporting/budget-cost-reports",
            "docType": "Budget"
          },
          {
            "label": "Progress and Productivity Reports",
            "route": "/portal/reporting/progress-productivity-reports",
            "docType": "Task"
          },
          {
            "label": "Billing and Collection Reports",
            "route": "/portal/reporting/billing-collection-reports",
            "docType": "Sales Invoice"
          }
        ]
      },
      {
        "title": "Operations and Resources",
        "items": [
          {
            "label": "Procurement and Subcontractor Reports",
            "route": "/portal/reporting/procurement-subcontractor-reports",
            "docType": "Purchase Order"
          },
          {
            "label": "Inventory Reports",
            "route": "/portal/reporting/inventory-reports",
            "docType": "Stock Ledger Entry"
          },
          {
            "label": "HR and Manpower Reports",
            "route": "/portal/reporting/hr-manpower-reports",
            "docType": "Attendance"
          },
          {
            "label": "Fabrication Reports",
            "route": "/portal/reporting/fabrication-reports",
            "docType": "Work Order"
          },
          {
            "label": "Asset and Equipment Reports",
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
            "label": "Active and Expiring Product Warranties",
            "route": "/portal/reporting/active-expiring-product-warranties",
            "docType": "Warranty Claim"
          },
          {
            "label": "Open and Overdue Warranty Claims",
            "route": "/portal/reporting/open-overdue-warranty-claims",
            "docType": "Warranty Claim"
          },
          {
            "label": "Supplier Warranty Claims and Recoveries",
            "route": "/portal/reporting/supplier-warranty-claims-recoveries",
            "docType": "Warranty Claim"
          },
          {
            "label": "Project Warranty and Defects Liability Expiry",
            "route": "/portal/reporting/project-warranty-defects-liability-expiry",
            "docType": "Warranty Claim"
          },
          {
            "label": "Outstanding Defect Rectifications",
            "route": "/portal/reporting/outstanding-defect-rectifications",
            "docType": "Warranty Claim"
          },
          {
            "label": "Warranty Costs by Project and Product",
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
  if (!docType) return null;
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
  if (!docType || !name || !router) return;

  const encodedName = encodeURIComponent(name);

  // If currently on a list page matching currentRoutePath, append name
  if (currentRoutePath && currentRoutePath.startsWith('/portal/')) {
    const cleanPath = currentRoutePath.split('?')[0].replace(/\/$/, '');
    const parts = cleanPath.split('/');
    if (parts.length === 4) {
      router.push(`${cleanPath}/${encodedName}`);
      return;
    }
  }

  // Lookup in WORKSPACES
  const navInfo = getNavigationByDocType(docType);
  if (navInfo && navInfo.moduleRoute) {
    router.push(`${navInfo.moduleRoute}/${encodedName}`);
    return;
  }

  // Fallback route
  const fallbackMod = docType.toLowerCase().replace(/ /g, '-');
  router.push(`/portal/project-management/${fallbackMod}/${encodedName}`);
}
