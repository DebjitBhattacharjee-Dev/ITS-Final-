import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_summary(workspace_id=None):
    """
    Universal Operational Dashboard Aggregator.
    Queries real-time Frappe/ERPNext database records for all 10 workspaces.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)

    # 1. Project Management
    active_projects = frappe.db.count("Project", filters={"status": ["in", ["Open", "In Progress", "Started"]]}) or 0
    completed_projects = frappe.db.count("Project", filters={"status": ["in", ["Completed", "Closed"]]}) or 0
    open_rfis = frappe.db.count("Request for Information", filters={"status": "Open"}) if frappe.db.exists("DocType", "Request for Information") else 0
    open_ncrs = frappe.db.count("Nonconformance Report", filters={"docstatus": 0}) if frappe.db.exists("DocType", "Nonconformance Report") else 0
    open_snags = frappe.db.count("Snag List", filters={"status": "Open"}) if frappe.db.exists("DocType", "Snag List") else 0

    # 2. Financial & Invoicing
    total_sales_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE docstatus=1")
    total_sales = float(total_sales_res[0][0] or 0) if total_sales_res else 0.0

    total_purchases_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Order` WHERE docstatus=1")
    total_purchases = float(total_purchases_res[0][0] or 0) if total_purchases_res else 0.0

    # 3. CRM & Estimation
    active_opportunities = frappe.db.count("Opportunity", filters={"status": ["in", ["Open", "Quoted"]]}) or 0
    active_quotations_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabQuotation` WHERE docstatus=1")
    quotation_value = float(active_quotations_res[0][0] or 0) if active_quotations_res else 0.0

    # 4. Inventory
    stock_value_res = frappe.db.sql("SELECT SUM(stock_value) FROM `tabBin`")
    total_stock_value = float(stock_value_res[0][0] or 0) if stock_value_res else 0.0

    # 5. HR & Manpower
    total_employees = frappe.db.count("Employee", filters={"status": "Active"}) or 0

    # 6. Production & Assets
    active_work_orders = frappe.db.count("Work Order", filters={"status": ["in", ["Submitted", "In Process"]]}) or 0
    total_assets = frappe.db.count("Asset", filters={"docstatus": 1}) or 0

    # 7. Warranties
    expiring_warranties = 0
    if frappe.db.exists("DocType", "Project Warranty"):
        expiring_warranties = frappe.db.count("Project Warranty", filters={"docstatus": 1}) or 0

    return {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "open_rfis": open_rfis,
        "open_ncrs": open_ncrs,
        "open_snags": open_snags,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "active_opportunities": active_opportunities,
        "quotation_value": quotation_value,
        "total_stock_value": total_stock_value,
        "total_employees": total_employees,
        "active_work_orders": active_work_orders,
        "total_assets": total_assets,
        "expiring_warranties": expiring_warranties
    }

