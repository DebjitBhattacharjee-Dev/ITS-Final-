import frappe

@frappe.whitelist()
def get_user_permissions():
	"""
	Returns the authorization matrix and permissions for the currently authenticated user session.
	Uses native Frappe session and permission check APIs.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Authentication required", frappe.AuthenticationError)

	roles = frappe.get_roles(user)
	
	# Evaluate permission access across DocTypes using native frappe.has_permission
	can_view_projects = frappe.has_permission("ITS Review Project", "read") or frappe.has_permission("Project", "read")
	can_create_projects = frappe.has_permission("ITS Review Project", "create") or frappe.has_permission("Project", "create")
	can_edit_projects = frappe.has_permission("ITS Review Project", "write") or frappe.has_permission("Project", "write")
	
	can_view_skids = frappe.has_permission("ITS Review Skid", "read")
	can_create_skids = frappe.has_permission("ITS Review Skid", "create")
	can_edit_skids = frappe.has_permission("ITS Review Skid", "write")

	can_view_documents = frappe.has_permission("ITS Review Document", "read")
	can_create_documents = frappe.has_permission("ITS Review Document", "create")
	
	can_view_punches = frappe.has_permission("ITS Review Punch", "read")
	can_create_punches = frappe.has_permission("ITS Review Punch", "create")

	can_view_parties = frappe.has_permission("Customer", "read") or frappe.has_permission("Supplier", "read") or frappe.has_permission("ITS Review Party", "read")
	can_view_materials = frappe.has_permission("Item", "read") or frappe.has_permission("ITS Review Material", "read")
	can_view_registers = frappe.has_permission("ITS Review Register", "read")

	is_admin = "System Manager" in roles or "Administrator" in roles or "ITS Admin" in roles

	# Map powerskid permissions dynamically
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

	return {
		"user": user,
		"roles": roles,
		"is_admin": is_admin,
		"permissions": powerskid_permissions,
		"capabilities": {
			"projects": {"read": can_view_projects, "create": can_create_projects, "write": can_edit_projects},
			"skids": {"read": can_view_skids, "create": can_create_skids, "write": can_edit_skids},
			"documents": {"read": can_view_documents, "create": can_create_documents},
			"punches": {"read": can_view_punches, "create": can_create_punches},
			"parties": {"read": can_view_parties},
			"materials": {"read": can_view_materials},
			"registers": {"read": can_view_registers}
		}
	}
