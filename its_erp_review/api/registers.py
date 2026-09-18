import frappe
from frappe import _

@frappe.whitelist()
def get_registers(kind=None):
	"""
	Returns company register items (services, legal, products).
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	filters = {}
	if kind:
		filters["kind"] = kind

	registers = frappe.get_list(
		"ITS Review Register",
		filters=filters,
		fields=["name as id", "kind", "code", "register_name as name", "category", "brand", "supplier", "unit", "unit_price as unitPrice", "currency", "reference", "issuer", "issue_date as issueDate", "expiry_date as expiryDate", "owner", "description", "status", "notes"],
		order_by="creation asc"
	)

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"rows": registers,
		"token": token
	}

@frappe.whitelist()
def save_register(kind=None, record=None):
	"""
	Creates or updates a Company Register record (legal document, service, product).
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if isinstance(record, str):
		record = frappe.parse_json(record)

	if not record or not record.get("id") or not record.get("name"):
		frappe.throw(_("Record ID and name are required."))

	rec_id = record.get("id")
	target_kind = kind or record.get("kind") or "legal"

	if frappe.db.exists("ITS Review Register", rec_id):
		doc = frappe.get_doc("ITS Review Register", rec_id)
		if doc.kind != target_kind:
			frappe.throw(_("Register category cannot be changed."))
		doc.register_name = record.get("name")
		doc.code = record.get("code")
		doc.category = record.get("category")
		doc.brand = record.get("brand")
		doc.supplier = record.get("supplier")
		doc.unit = record.get("unit")
		doc.unit_price = float(record.get("unitPrice", 0)) if record.get("unitPrice") is not None else 0.0
		doc.currency = record.get("currency", "AED")
		doc.reference = record.get("reference")
		doc.issuer = record.get("issuer")
		doc.issue_date = record.get("issueDate")
		doc.expiry_date = record.get("expiryDate")
		doc.owner = record.get("owner")
		doc.description = record.get("description")
		doc.status = record.get("status", "Active")
		doc.notes = record.get("notes")
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({
			"doctype": "ITS Review Register",
			"name": rec_id,
			"kind": target_kind,
			"code": record.get("code"),
			"register_name": record.get("name"),
			"category": record.get("category"),
			"brand": record.get("brand"),
			"supplier": record.get("supplier"),
			"unit": record.get("unit"),
			"unit_price": float(record.get("unitPrice", 0)) if record.get("unitPrice") is not None else 0.0,
			"currency": record.get("currency", "AED"),
			"reference": record.get("reference"),
			"issuer": record.get("issuer"),
			"issue_date": record.get("issueDate"),
			"expiry_date": record.get("expiryDate"),
			"owner": record.get("owner"),
			"description": record.get("description"),
			"status": record.get("status", "Active"),
			"notes": record.get("notes")
		})
		doc.insert(ignore_permissions=True)

	frappe.db.commit()

	return {"record": record}

