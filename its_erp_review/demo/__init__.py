import frappe
from frappe import _

@frappe.whitelist()
def setup_demo():
    """Whitelisted endpoint to seed or refresh the complete ITS client demo dataset."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required to seed demo data"), frappe.PermissionError)
    from its_erp_review.demo.demo_setup import run_setup
    return run_setup()

@frappe.whitelist()
def reset_demo(confirm=False):
    """Whitelisted endpoint to cleanly reset demo dataset with explicit confirmation."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required to reset demo data"), frappe.PermissionError)
    if not frappe.utils.cint(confirm):
        frappe.throw(_("Explicit confirmation required: pass confirm=1 to reset demo data."), frappe.ValidationError)
    from its_erp_review.demo.demo_reset import run_cleanup
    return run_cleanup()
