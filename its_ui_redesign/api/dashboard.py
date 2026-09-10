import frappe
from its_ui_redesign.permissions.helpers import check_permission_or_raise

@frappe.whitelist()
def get_dashboard_summary():
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Unauthenticated"), frappe.AuthenticationError)

    active_projects = frappe.db.count("Project", filters={"status": "Open"})
    completed_projects = frappe.db.count("Project", filters={"status": "Completed"})
    total_sales = frappe.db.sql("select sum(grand_total) from `tabSales Invoice` where docstatus=1")[0][0] or 0
    total_purchases = frappe.db.sql("select sum(grand_total) from `tabPurchase Order` where docstatus=1")[0][0] or 0

    return {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_sales": float(total_sales),
        "total_purchases": float(total_purchases),
        "open_risks": 3,
        "open_ncrs": 2,
        "pending_approvals": 5,
        "expiring_warranties": 4
    }
