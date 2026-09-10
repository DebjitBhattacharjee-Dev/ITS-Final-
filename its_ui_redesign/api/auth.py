import frappe
from frappe import _
from frappe.auth import LoginManager

def get_safe_csrf_token():
    try:
        return frappe.sessions.get_csrf_token()
    except Exception:
        return getattr(frappe.local, "csrf_token", "") or ""

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    if frappe.session.user != "Guest":
        return get_logged_user()

    login_manager = LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()

    frappe.response["message"] = {
        "status": "Logged In",
        "user": frappe.session.user,
        "full_name": frappe.utils.get_fullname(frappe.session.user),
        "csrf_token": get_safe_csrf_token()
    }

@frappe.whitelist()
def logout():
    frappe.local.login_manager.logout()
    frappe.response["message"] = "Logged Out"

@frappe.whitelist()
def get_logged_user():
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)

    user = frappe.get_doc("User", frappe.session.user)
    roles = frappe.get_roles(frappe.session.user)
    
    return {
        "user": user.name,
        "email": user.email,
        "full_name": user.full_name,
        "user_image": user.user_image,
        "roles": roles,
        "csrf_token": get_safe_csrf_token()
    }
