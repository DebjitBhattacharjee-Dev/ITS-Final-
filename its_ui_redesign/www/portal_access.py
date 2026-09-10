import frappe

def get_context(context):
    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/portal"
        raise frappe.Redirect

    context.csrf_token = frappe.sessions.get_csrf_token()
    context.boot = frappe.sessions.get()
    context.title = "ITS Project Operations - Sign In"
    context.no_cache = 1
