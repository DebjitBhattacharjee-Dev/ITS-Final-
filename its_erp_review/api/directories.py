import frappe
from frappe import _

@frappe.whitelist()
def get_parties():
	"""
	Returns active Customer and Supplier directory records from MariaDB.
	Integrates native ERPNext Customer & Supplier DocTypes with ITS Review Party.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	parties = []
	seen = set()

	# Fetch from ITS Review Party
	its_parties = frappe.get_all(
		"ITS Review Party",
		fields=["name as id", "kind", "party_name as name", "contact", "email", "phone", "country", "address", "tax_id as taxId", "payment_terms as paymentTerms", "status", "notes"],
		order_by="party_name asc"
	)
	for p in its_parties:
		key = f"{p.get('kind')}:{p.get('name', '').lower()}"
		seen.add(key)
		parties.append(p)

	# Fetch native ERPNext Customers
	if frappe.db.table_exists("Customer"):
		customers = frappe.get_all("Customer", fields=["name", "customer_name", "tax_id", "territory"], limit=200)
		for c in customers:
			key = f"Customer:{c.get('customer_name', c.name).lower()}"
			if key not in seen:
				seen.add(key)
				parties.append({
					"id": c.name,
					"kind": "Customer",
					"name": c.customer_name or c.name,
					"contact": "",
					"email": "",
					"phone": "",
					"country": c.territory or "UAE",
					"address": "",
					"taxId": c.tax_id or "",
					"paymentTerms": "30 Days",
					"status": "Active",
					"notes": "Active Customer"
				})

	# Fetch native ERPNext Suppliers
	if frappe.db.table_exists("Supplier"):
		suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name", "tax_id", "country"], limit=200)
		for s in suppliers:
			key = f"Supplier:{s.get('supplier_name', s.name).lower()}"
			if key not in seen:
				seen.add(key)
				parties.append({
					"id": s.name,
					"kind": "Supplier",
					"name": s.supplier_name or s.name,
					"contact": "",
					"email": "",
					"phone": "",
					"country": s.country or "UAE",
					"address": "",
					"taxId": s.tax_id or "",
					"paymentTerms": "30 Days",
					"status": "Active",
					"notes": "Active Supplier"
				})

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"parties": parties,
		"token": token
	}

@frappe.whitelist()
def save_party(party=None):
	"""
	Creates or updates a Customer/Supplier record natively in MariaDB across both ITS Review Party and ERPNext Customer/Supplier.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if isinstance(party, str):
		party = frappe.parse_json(party)

	if not party or not party.get("id") or not party.get("name") or not party.get("kind"):
		frappe.throw(_("Company name, directory type, and status are required."))

	if party["kind"] not in ["Customer", "Supplier"]:
		frappe.throw(_("Invalid directory type."))

	party_id = party.get("id")
	party_name = party.get("name").strip()

	# Save/Update ITS Review Party
	if frappe.db.exists("ITS Review Party", party_id):
		doc = frappe.get_doc("ITS Review Party", party_id)
		if doc.kind != party["kind"]:
			frappe.throw(_("Directory type cannot be changed."))
		doc.party_name = party_name
		doc.contact = party.get("contact")
		doc.email = party.get("email")
		doc.phone = party.get("phone")
		doc.country = party.get("country")
		doc.address = party.get("address")
		doc.tax_id = party.get("taxId")
		doc.payment_terms = party.get("paymentTerms")
		doc.status = party.get("status", "Active")
		doc.notes = party.get("notes")
		doc.save()
	else:
		doc = frappe.get_doc({
			"doctype": "ITS Review Party",
			"name": party_id,
			"kind": party["kind"],
			"party_name": party_name,
			"contact": party.get("contact"),
			"email": party.get("email"),
			"phone": party.get("phone"),
			"country": party.get("country"),
			"address": party.get("address"),
			"tax_id": party.get("taxId"),
			"payment_terms": party.get("paymentTerms"),
			"status": party.get("status", "Active"),
			"notes": party.get("notes")
		})
		doc.insert()

	# Also sync to native ERPNext Customer or Supplier DocType if available
	if party["kind"] == "Customer" and frappe.db.table_exists("Customer"):
		if not frappe.db.exists("Customer", party_name):
			try:
				c_doc = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": party_name,
					"customer_group": "All Customer Groups",
					"territory": party.get("country") or "All Territories",
					"tax_id": party.get("taxId")
				})
				c_doc.insert()
			except Exception:
				pass

	elif party["kind"] == "Supplier" and frappe.db.table_exists("Supplier"):
		if not frappe.db.exists("Supplier", party_name):
			try:
				s_doc = frappe.get_doc({
					"doctype": "Supplier",
					"supplier_name": party_name,
					"supplier_group": "All Supplier Groups",
					"country": party.get("country") or "United Arab Emirates",
					"tax_id": party.get("taxId")
				})
				s_doc.insert()
			except Exception:
				pass

	frappe.db.commit()

	return {"party": party}

