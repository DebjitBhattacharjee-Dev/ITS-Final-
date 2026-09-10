import frappe

@frappe.whitelist()
def get_warranties(warranty_type=None, search=None):
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Unauthenticated"), frappe.AuthenticationError)

    # Return structured warranty list (reusing Warranty Claim or custom warranty records)
    claims = frappe.get_all(
        "Warranty Claim",
        fields=["name", "customer", "item_code", "status", "complaint", "resolution_date"],
        limit=20
    )
    return claims
