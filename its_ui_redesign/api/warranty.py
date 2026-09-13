import frappe

@frappe.whitelist()
def get_warranties(warranty_type=None, search=None):
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Unauthenticated"), frappe.AuthenticationError)

    if not frappe.db.exists("DocType", "Warranty Claim"):
        return []
    if not frappe.has_permission("Warranty Claim", "read"):
        return []

    claims = frappe.get_list(
        "Warranty Claim",
        fields=["name", "customer", "item_code", "status", "complaint", "resolution_date"],
        limit_page_length=20,
        ignore_permissions=False
    )
    return claims
