import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_summary():
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)

    # Real database aggregations across ERPNext & custom DocTypes
    active_projects = frappe.db.count("Project", filters={"status": ["in", ["Open", "In Progress", "Started"]]}) or 0
    completed_projects = frappe.db.count("Project", filters={"status": ["in", ["Completed", "Closed"]]}) or 0
    
    total_sales_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE docstatus=1")
    total_sales = float(total_sales_res[0][0] or 0) if total_sales_res else 0.0

    total_purchases_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Order` WHERE docstatus=1")
    total_purchases = float(total_purchases_res[0][0] or 0) if total_purchases_res else 0.0

    # Custom DocTypes counts
    open_risks = frappe.db.count("Issue", filters={"status": ["in", ["Open", "Replied"]]}) or 0
    
    open_ncrs = 0
    if frappe.db.exists("DocType", "Nonconformance Report"):
        open_ncrs = frappe.db.count("Nonconformance Report", filters={"docstatus": 0}) or 0
    
    pending_approvals = frappe.db.count("ToDo", filters={"status": "Open", "allocated_to": frappe.session.user}) or 0
    
    expiring_warranties = 0
    if frappe.db.exists("DocType", "Project Warranty"):
        expiring_warranties = frappe.db.count("Project Warranty", filters={"docstatus": 1}) or 0

    return {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "open_risks": open_risks,
        "open_ncrs": open_ncrs,
        "pending_approvals": pending_approvals,
        "expiring_warranties": expiring_warranties
    }
