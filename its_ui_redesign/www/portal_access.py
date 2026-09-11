import frappe
import frappe.sessions

def get_context(context):
    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/portal"
        raise frappe.Redirect

    context.csrf_token = frappe.sessions.get_csrf_token()
    boot_info = frappe.sessions.get()
    context.boot_json = frappe.as_json(boot_info)
    context.title = "ITS Project Operations - Sign In"
    context.no_cache = 1
