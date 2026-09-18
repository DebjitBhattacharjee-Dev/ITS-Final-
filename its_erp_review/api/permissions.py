import frappe
from frappe import _

PERSONA_ROLES = {
	"Administrator": {
		"label": "Administrator (Full Access)",
		"department": "All",
		"can_approve": ["all"],
		"modules": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	},
	"Commercial": {
		"label": "Commercial Manager",
		"department": "Commercial",
		"can_approve": ["Quotation", "Sales Order", "Opportunity", "inquiry", "quotation", "order"],
		"modules": [0]
	},
	"Projects": {
		"label": "Project Manager",
		"department": "Projects",
		"can_approve": ["Project", "plan", "engineering", "ITS Review Project", "ITS Review Skid", "ITS Review Activity"],
		"modules": [1]
	},
	"Estimation": {
		"label": "Estimation Engineer",
		"department": "Estimation",
		"can_approve": ["estimation", "Material Request", "material"],
		"modules": [2]
	},
	"Procurement": {
		"label": "Procurement / Purchase Lead",
		"department": "Procurement",
		"can_approve": ["Purchase Order", "Material Request", "material", "purchase", "Supplier"],
		"modules": [3]
	},
	"Logistics": {
		"label": "Logistics & Warehouse Manager",
		"department": "Logistics",
		"can_approve": ["Delivery Note", "Purchase Receipt", "shipment", "delivery"],
		"modules": [4]
	},
	"Quality": {
		"label": "QA/QC Manager",
		"department": "Quality",
		"can_approve": ["Quality Inspection", "ITS Review Punch", "inspection", "commission", "punch"],
		"modules": [5]
	},
	"HR & Access": {
		"label": "HR & Site Access Manager",
		"department": "HR & Access",
		"can_approve": ["Employee", "Timesheet", "access", "timesheet"],
		"modules": [6]
	},
	"Service & Workshop": {
		"label": "Workshop & Fabrication Manager",
		"department": "Service & Workshop",
		"can_approve": ["fabrication", "service", "Work Order"],
		"modules": [7]
	},
	"Finance": {
		"label": "Finance Controller",
		"department": "Finance",
		"can_approve": ["Sales Invoice", "Purchase Invoice", "invoice", "payment", "statement"],
		"modules": [8]
	},
	"Management": {
		"label": "Executive Management",
		"department": "Management",
		"can_approve": ["all"],
		"modules": [9, 0, 1, 3, 5, 8]
	},
	"Contracts": {
		"label": "Contracts & Legal Counsel",
		"department": "Contracts",
		"can_approve": ["Contract", "contract", "tender"],
		"modules": [10]
	}
}

@frappe.whitelist(allow_guest=True)
def get_user_permissions(active_persona=None):
	"""
	Returns user session information, native Frappe roles, capabilities matrix,
	and available departmental personas with approval authority.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "ITS Admin" in roles

	# Resolve active persona (stored in session or passed in)
	session_persona = frappe.cache().hget("its_review_active_persona", user) or "Administrator"
	if active_persona and (is_admin or active_persona in PERSONA_ROLES):
		session_persona = active_persona
		frappe.cache().hset("its_review_active_persona", user, active_persona)

	persona_info = PERSONA_ROLES.get(session_persona, PERSONA_ROLES["Administrator"])

	# Evaluate DocType capabilities
	can_view_projects = frappe.has_permission("ITS Review Project", "read") or frappe.has_permission("Project", "read")
	can_create_projects = frappe.has_permission("ITS Review Project", "create") or frappe.has_permission("Project", "create")
	can_edit_projects = frappe.has_permission("ITS Review Project", "write") or frappe.has_permission("Project", "write")

	can_view_skids = frappe.has_permission("ITS Review Skid", "read")
	can_create_skids = frappe.has_permission("ITS Review Skid", "create")
	can_edit_skids = frappe.has_permission("ITS Review Skid", "write")

	can_view_documents = frappe.has_permission("ITS Review Document", "read")
	can_create_documents = frappe.has_permission("ITS Review Document", "create")
	can_edit_documents = frappe.has_permission("ITS Review Document", "write")

	can_view_punches = frappe.has_permission("ITS Review Punch", "read")
	can_create_punches = frappe.has_permission("ITS Review Punch", "create")

	can_view_parties = frappe.has_permission("Customer", "read") or frappe.has_permission("Supplier", "read") or frappe.has_permission("ITS Review Party", "read")
	can_view_materials = frappe.has_permission("Item", "read") or frappe.has_permission("ITS Review Material", "read")
	can_view_registers = frappe.has_permission("ITS Review Register", "read")

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
	if is_admin or session_persona in ["Management", "Administrator"]:
		powerskid_permissions.extend(["powerskid.admin", "powerskid.fat", "powerskid.ifat", "powerskid.commissioning", "powerskid.handover"])

	# List personas user can switch to
	available_personas = []
	for p_key, p_val in PERSONA_ROLES.items():
		available_personas.append({
			"id": p_key,
			"label": p_val["label"],
			"department": p_val["department"]
		})

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"user": user,
		"roles": roles,
		"is_admin": is_admin,
		"active_persona": session_persona,
		"persona_label": persona_info["label"],
		"persona_department": persona_info["department"],
		"can_approve_doctypes": persona_info["can_approve"],
		"available_personas": available_personas,
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

@frappe.whitelist(allow_guest=True)
def set_active_persona(persona=None):
	"""
	Sets the active persona for the current user session.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if persona and persona in PERSONA_ROLES:
		frappe.cache().hset("its_review_active_persona", user, persona)
		return {"status": "ok", "active_persona": persona, "label": PERSONA_ROLES[persona]["label"]}

	frappe.cache().hset("its_review_active_persona", user, "Administrator")
	return {"status": "ok", "active_persona": "Administrator", "label": PERSONA_ROLES["Administrator"]["label"]}
