import frappe

def get_user_roles(user=None):
    if not user:
        user = frappe.session.user
    return frappe.get_roles(user)

def check_permission_or_raise(doctype, ptype="read"):
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Authentication required"), frappe.AuthenticationError)
    if not frappe.has_permission(doctype, ptype):
        frappe.throw(frappe._("Access denied for {0} on {1}").format(ptype, doctype), frappe.PermissionError)
