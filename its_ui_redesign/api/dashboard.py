import frappe
import json

@frappe.whitelist()
def get_workflow_summary():
    """
    Returns counts of actionable documents per workflow stage.
    Uses permission-aware frappe.get_list() so users only see counts of documents they have access to.
    """
    stages = [
        {
            "gate": "G0",
            "label": "Enquiry",
            "doctype": "Lead",
            "state_label": "Open",
            "filters": [["status", "=", "Open"]],
            "list_route": "/portal/project-management/leads"
        },
        {
            "gate": "G1",
            "label": "Opportunity",
            "doctype": "Opportunity",
            "state_label": "Open",
            "filters": [["status", "=", "Open"]],
            "list_route": "/portal/project-management/opportunities"
        },
        {
            "gate": "G2",
            "label": "Supplier Quote",
            "doctype": "Supplier Quotation",
            "state_label": "Pending Review",
            "filters": [["docstatus", "=", 0]],
            "list_route": "/portal/procurement-subcontractors/supplier-quotations"
        },
        {
            "gate": "G3",
            "label": "Customer Quote",
            "doctype": "Quotation",
            "state_label": "Draft",
            "filters": [["docstatus", "=", 0]],
            "list_route": "/portal/project-management/quotations"
        },
        {
            "gate": "G3.5",
            "label": "Contract",
            "doctype": "Project Contract",
            "state_label": "Active",
            "filters": [["status", "=", "Active"]],
            "list_route": "/portal/project-management/project-contracts"
        },
        {
            "gate": "G5.5",
            "label": "Sales Order",
            "doctype": "Sales Order",
            "state_label": "To Deliver and Bill",
            "filters": [["status", "=", "To Deliver and Bill"]],
            "list_route": "/portal/project-management/sales-orders"
        },
        {
            "gate": "G7",
            "label": "Purchase Order",
            "doctype": "Purchase Order",
            "state_label": "To Receive and Bill",
            "filters": [["status", "=", "To Receive and Bill"]],
            "list_route": "/portal/procurement-subcontractors/purchase-orders"
        },
        {
            "gate": "G8",
            "label": "Factory Acceptance Test",
            "doctype": "Factory Acceptance Test",
            "state_label": "Pending",
            "filters": [["status", "=", "Pending"]],
            "list_route": "/portal/fabrication-assets-equipment/factory-acceptance-tests"
        },
        {
            "gate": "G8",
            "label": "Integrated Factory Acceptance Test",
            "doctype": "Integrated Factory Acceptance Test",
            "state_label": "Pending",
            "filters": [["status", "=", "Pending"]],
            "list_route": "/portal/fabrication-assets-equipment/integrated-factory-acceptance-tests"
        },
        {
            "gate": "G8.5",
            "label": "Punch List",
            "doctype": "Snag List",
            "state_label": "Open",
            "filters": [["status", "=", "Open"]],
            "list_route": "/portal/project-management/snag-lists"
        },
        {
            "gate": "G9.5",
            "label": "Delivery Note",
            "doctype": "Delivery Note",
            "state_label": "To Bill",
            "filters": [["status", "=", "To Bill"]],
            "list_route": "/portal/inventory-management/delivery-notes"
        },
        {
            "gate": "G9.7",
            "label": "Handover",
            "doctype": "Project Handover",
            "state_label": "Pending",
            "filters": [["status", "=", "Pending"]],
            "list_route": "/portal/project-management/project-handovers"
        },
        {
            "gate": "G10.5",
            "label": "Sales Invoice",
            "doctype": "Sales Invoice",
            "state_label": "Unpaid",
            "filters": [["status", "=", "Unpaid"]],
            "list_route": "/portal/accounting-finance/sales-invoices"
        },
        {
            "gate": "G11",
            "label": "Warranty",
            "doctype": "Project Warranty",
            "state_label": "Active",
            "filters": [["status", "=", "Active"]],
            "list_route": "/portal/fabrication-assets-equipment/project-warranties"
        }
    ]

    summary = {}
    
    for stage in stages:
        gate = stage['gate']
        doctype = stage['doctype']
        filters = stage['filters']
        
        try:
            # Check if doctype exists to avoid errors on custom doctypes that might not be installed
            if frappe.db.exists("DocType", doctype):
                count = frappe.db.count(doctype, filters=filters)
                
                # We can construct a unique key using gate + doctype to handle G8 FAT and IFAT correctly
                key = f"{gate}_{doctype.replace(' ', '_')}"
                
                summary[key] = {
                    "gate": gate,
                    "label": stage['label'],
                    "doctype": doctype,
                    "state_label": stage['state_label'],
                    "count": count,
                    "filters": filters,
                    "list_route": stage['list_route']
                }
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Dashboard Count Error for {doctype}")
            pass

    return summary
