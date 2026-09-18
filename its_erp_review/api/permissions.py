import frappe
from frappe import _

@frappe.whitelist()
def get_user_permissions():
	"""
	Returns authentic user session information, native Frappe roles,
	and actual DocType permissions evaluated server-side.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles

	# Evaluate DocType capabilities using native Frappe permissions
	can_view_projects = bool(frappe.has_permission("ITS Review Project", "read") or frappe.has_permission("Project", "read"))
	can_create_projects = bool(frappe.has_permission("ITS Review Project", "create") or frappe.has_permission("Project", "create"))
	can_edit_projects = bool(frappe.has_permission("ITS Review Project", "write") or frappe.has_permission("Project", "write"))

	can_view_skids = bool(frappe.has_permission("ITS Review Skid", "read"))
	can_create_skids = bool(frappe.has_permission("ITS Review Skid", "create"))
	can_edit_skids = bool(frappe.has_permission("ITS Review Skid", "write"))

	can_view_documents = bool(frappe.has_permission("ITS Review Document", "read"))
	can_create_documents = bool(frappe.has_permission("ITS Review Document", "create"))
	can_edit_documents = bool(frappe.has_permission("ITS Review Document", "write"))

	can_view_punches = bool(frappe.has_permission("ITS Review Punch", "read"))
	can_create_punches = bool(frappe.has_permission("ITS Review Punch", "create"))

	can_view_parties = bool(frappe.has_permission("Customer", "read") or frappe.has_permission("Supplier", "read") or frappe.has_permission("ITS Review Party", "read"))
	can_view_materials = bool(frappe.has_permission("Item", "read") or frappe.has_permission("ITS Review Material", "read"))
	can_view_registers = bool(frappe.has_permission("ITS Review Register", "read"))

	# Map powerskid permissions
	powerskid_permissions = []
	if can_view_skids or can_view_projects:
		powerskid_permissions.append("powerskid.view")
	if can_create_projects or can_create_skids:
		powerskid_permissions.append("powerskid.create")
	if can_edit_projects or can_edit_skids:
		powerskid_permissions.append("powerskid.edit")
	if can_view_documents:
		powerskid_permissions.append("powerskid.engineering")
	if can_view_punches:
		powerskid_permissions.append("powerskid.punch")
	if is_admin:
		powerskid_permissions.extend(["powerskid.admin", "powerskid.fat", "powerskid.ifat", "powerskid.commissioning", "powerskid.handover"])

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"user": user,
		"roles": roles,
		"is_admin": is_admin,
		"permissions": powerskid_permissions,
		"capabilities": {
			"projects": {"read": can_view_projects, "create": can_create_projects, "write": can_edit_projects},
			"skids": {"read": can_view_skids, "create": can_create_skids, "write": can_edit_skids},
			"documents": {"read": can_view_documents, "create": can_create_documents, "write": can_edit_documents},
			"punches": {"read": can_view_punches, "create": can_create_punches},
			"parties": {"read": can_view_parties},
			"materials": {"read": can_view_materials},
			"registers": {"read": can_view_registers}
		},
		"token": token
	}
