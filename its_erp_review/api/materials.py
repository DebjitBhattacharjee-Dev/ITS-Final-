import frappe
from frappe import _

@frappe.whitelist()
def get_materials():
	"""
	Returns all material items from MariaDB combining ITS Review Material and native ERPNext Item.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	materials = []
	seen = set()

	# Fetch from ITS Review Material
	its_mats = frappe.get_all(
		"ITS Review Material",
		fields=["name as id", "code", "material_name as name", "part_no as partNo", "supplier", "unit", "unit_price as unitPrice", "currency", "description", "status"],
		order_by="code asc"
	)
	for m in its_mats:
		code = m.get("code") or m.get("id")
		seen.add(code.lower())
		materials.append(m)

	# Fetch native ERPNext Items
	if frappe.db.table_exists("Item"):
		items = frappe.get_all("Item", fields=["name", "item_code", "item_name", "stock_uom", "standard_rate", "description"], limit=200)
		for item in items:
			code = item.item_code or item.name
			if code.lower() not in seen:
				seen.add(code.lower())
				materials.append({
					"id": item.name,
					"code": code,
					"name": item.item_name or code,
					"partNo": code,
					"supplier": "",
					"unit": item.stock_uom or "Nos",
					"unitPrice": float(item.standard_rate or 0),
					"currency": "AED",
					"description": item.description or item.item_name or "",
					"status": "Active"
				})

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"materials": materials,
		"token": token
	}

@frappe.whitelist()
def save_material(material=None):
	"""
	Creates or updates a material item natively in MariaDB in ITS Review Material and ERPNext Item.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if isinstance(material, str):
		material = frappe.parse_json(material)

	if not material or not material.get("code") or not material.get("name") or not material.get("unit"):
		frappe.throw(_("Material code, name, unit, and status are required."))

	mat_id = material.get("id") or material.get("code")
	code = material.get("code").strip()
	name = material.get("name").strip()

	# Save to ITS Review Material
	if frappe.db.exists("ITS Review Material", mat_id):
		doc = frappe.get_doc("ITS Review Material", mat_id)
		doc.code = code
		doc.material_name = name
		doc.part_no = material.get("partNo")
		doc.supplier = material.get("supplier")
		doc.unit = material.get("unit")
		doc.unit_price = float(material.get("unitPrice", 0))
		doc.currency = material.get("currency", "AED")
		doc.description = material.get("description")
		doc.status = material.get("status", "Active")
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({
			"doctype": "ITS Review Material",
			"name": mat_id,
			"code": code,
			"material_name": name,
			"part_no": material.get("partNo"),
			"supplier": material.get("supplier"),
			"unit": material.get("unit"),
			"unit_price": float(material.get("unitPrice", 0)),
			"currency": material.get("currency", "AED"),
			"description": material.get("description"),
			"status": material.get("status", "Active")
		})
		doc.insert(ignore_permissions=True)

	# Also sync to native ERPNext Item DocType if available
	if frappe.db.table_exists("Item") and not frappe.db.exists("Item", code):
		try:
			item_doc = frappe.get_doc({
				"doctype": "Item",
				"item_code": code,
				"item_name": name,
				"item_group": "All Item Groups",
				"stock_uom": material.get("unit") or "Nos",
				"standard_rate": float(material.get("unitPrice", 0)),
				"description": material.get("description") or name
			})
			item_doc.insert(ignore_permissions=True)
		except Exception:
			pass

	frappe.db.commit()

	return {"material": material}

