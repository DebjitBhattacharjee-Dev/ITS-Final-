import frappe
import frappe.sessions

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/portal-access"
        raise frappe.Redirect

    import time
    context.csrf_token = frappe.sessions.get_csrf_token()
    boot_info = frappe.sessions.get()
    context.boot_json = frappe.as_json(boot_info)
    context.title = "ITS Project Operations"
    context.ver = str(int(time.time()))
    context.no_cache = 1

    # Clear default preloaded web assets so standard frappe web bundles don't emit unused preload warnings
    if hasattr(frappe.local, "preload_assets"):
        frappe.local.preload_assets = {"script": [], "style": [], "icons": []}


