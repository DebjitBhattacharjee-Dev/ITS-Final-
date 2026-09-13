import frappe

@frappe.whitelist()
def get_projects(status=None, search=None):
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Unauthenticated"), frappe.AuthenticationError)

    filters = {}
    if status:
        filters["status"] = status
    if search:
        filters["project_name"] = ["like", f"%{search}%"]

    projects = frappe.get_list(
        "Project",
        fields=["name", "project_name", "status", "percent_complete", "expected_end_date", "company"],
        filters=filters,
        order_by="creation desc",
        limit_page_length=50,
        ignore_permissions=False
    )
    return projects
