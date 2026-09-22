import frappe
import json
from frappe import _
from its_erp_review.api.gates import validate_document_gates

if not hasattr(frappe, "ConcurrencyError"):
	class ConcurrencyError(frappe.ValidationError):
		pass
	frappe.ConcurrencyError = ConcurrencyError

# Standard domain workflow definitions
DEFAULT_WORKFLOWS = {
	"TRADING": [
		"Customer Requirement", "Quotation", "Customer PO / Order",
		"Purchase from Supplier", "Material Receipt", "Delivery",
		"Sales / Invoice", "Project Closure"
	],
	"POWERSKID": [
		"Project Award", "Engineering", "Document Submission / Approval",
		"Procurement", "Material Receipt", "Integration", "Internal Testing",
		"FAT Preparation", "FAT", "FAT Punch Closure", "IFAT Preparation",
		"IFAT", "IFAT Punch Closure", "Delivery", "Site Readiness",
		"SAT", "Commissioning", "Commissioning Punch Closure",
		"Handover / CEP", "Project Completion"
	]
}

@frappe.whitelist()
def get_workspace():
	"""
	Returns the complete workspace state (projects, skids, events, punches, commissioning,
	documents, activities, handovers, history, workflows) filtered by user permissions.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	# Fetch accessible projects from ITS Review Project
	projects = frappe.get_list(
		"ITS Review Project",
		fields=["name as id", "project_name as name", "customer", "project_type", "status", "contract_no", "po_no"],
		order_by="creation asc"
	)
	existing_pids = {p["id"] for p in projects}

	# Also include any ERPNext projects not already in ITS Review Project
	erp_projects = frappe.get_list(
		"Project",
		fields=["name as id", "project_name as name", "customer", "status"],
		order_by="creation asc"
	)
	for ep in erp_projects:
		if ep["id"] not in existing_pids:
			is_skid = "skid" in (ep.get("name") or "").lower() or "pss" in (ep.get("name") or "").lower()
			projects.append({
				"id": ep["id"],
				"name": ep.get("name") or ep["id"],
				"customer": ep.get("customer") or "ITS Client Corp",
				"project_type": "POWERSKID" if is_skid else "TRADING",
				"status": ep.get("status") or "Active",
				"contract_no": ep["id"],
				"po_no": ep["id"]
			})
			existing_pids.add(ep["id"])

	# Ensure all projects have contract & PO numbers populated
	for p in projects:
		if not p.get("contract_no"):
			p["contract_no"] = f"CTR-{p['id']}"
		if not p.get("po_no"):
			p["po_no"] = f"PO-{p['id']}"

	skids = frappe.get_list(
		"ITS Review Skid",
		fields=["name as id", "project_id as projectId", "skid_number as number", "well_number as well", "serial_number as serial", "skid_type as skidType", "rating", "location", "status"],
		order_by="creation asc"
	)

	events = frappe.get_list(
		"ITS Review Event",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "test", "planned_date as plannedDate", "actual_date as actualDate", "location", "witness", "status", "result", "remarks"],
		order_by="creation asc"
	)

	punches_raw = frappe.get_list(
		"ITS Review Punch",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "source", "category", "description", "responsible", "assigned", "raised_date as raisedDate", "target_date as targetDate", "priority", "status", "closure_remarks as closureRemarks", "evidence", "closed_date as closedDate"],
		order_by="creation asc"
	)
	VALID_PUNCH_SOURCES = {"FAT", "IFAT", "SAT", "Commissioning", "Client Inspection", "Other"}
	punches = []
	for punch in punches_raw:
		p = dict(punch)
		if p.get("source") not in VALID_PUNCH_SOURCES:
			p["source"] = "FAT"
		p["description"] = p.get("description") or "Inspection item"
		p["responsible"] = p.get("responsible") or "ITS Quality Lead"
		p["assigned"] = p.get("assigned") or "ITS Engineer"
		p["raisedDate"] = str(p.get("raisedDate") or frappe.utils.today())
		p["targetDate"] = str(p.get("targetDate") or frappe.utils.add_days(frappe.utils.today(), 14))
		p["status"] = p.get("status") or "Open"
		punches.append(p)

	commissioning = frappe.get_list(
		"ITS Review Commissioning",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "status", "planned_date as plannedDate", "commissioning_date as commissioningDate", "engineer", "remarks"],
		order_by="creation asc"
	)

	DOC_CATEGORIES = {
		'Personnel Documents', 'Vehicle Documents', 'Drawings', 'Datasheets',
		'Control Narrative', 'Cause & Effect', 'PLC Documents', 'VFD Documents',
		'Transformer Documents', 'Switchgear Documents', 'UPS Documents',
		'F&G Documents', 'HVAC Documents', 'FAT Documents', 'IFAT Documents',
		'SAT Documents', 'Commissioning Documents', 'Punch Closure Documents',
		'As-Built Documents', 'Handover Documents', 'RCA / Technical Reports'
	}
	raw_documents = frappe.get_list(
		"ITS Review Document",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "title", "category", "reference", "revision", "status", "discipline", "transmittal", "owner", "submitted_date as submittedDate", "review_due as reviewDue", "review_comments as reviewComments", "previous_revision_id as previousRevisionId"],
		order_by="creation asc"
	)
	documents = []
	for doc in raw_documents:
		d = dict(doc)
		cat = d.get("category") or "Drawings"
		if cat == "Engineering Drawing":
			cat = "Drawings"
		if cat in DOC_CATEGORIES:
			d["category"] = cat
			documents.append(d)

	activities = frappe.get_list(
		"ITS Review Activity",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "stage", "title", "owner", "planned_date as plannedDate", "actual_date as actualDate", "status", "remarks"],
		order_by="creation asc"
	)

	handovers = frappe.get_list(
		"ITS Review Handover",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "status", "cep", "date", "remarks"],
		order_by="creation asc"
	)

	# Get revision meta
	revision = frappe.db.get_single_value("ITS Review Settings", "workspace_revision") or 1

	state = {
		"projects": projects,
		"skids": skids,
		"equipment": [],
		"events": events,
		"punches": punches,
		"commissioning": commissioning,
		"documents": documents,
		"activities": activities,
		"handovers": handovers,
		"workflows": DEFAULT_WORKFLOWS,
		"history": []
	}

	from its_erp_review.api.permissions import get_user_permissions
	user_info = get_user_permissions()
	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"state": state,
		"revision": revision,
		"permissions": user_info.get("permissions", []),
		"token": token
	}

@frappe.whitelist()
def save_workspace(state, revision=None):
	"""
	Saves the workspace state into native Frappe DocTypes in MariaDB with permission and business rule validations.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if isinstance(state, str):
		state = json.loads(state)

	# Fetch current revision for optimistic locking
	current_revision = frappe.db.get_single_value("ITS Review Settings", "workspace_revision") or 1
	if revision is not None and int(revision) != current_revision:
		frappe.throw(_("Workspace changed elsewhere. Reload before saving."), frappe.ConcurrencyError)

	# Process projects
	for p in state.get("projects", []):
		if not frappe.db.exists("ITS Review Project", p["id"]):
			doc = frappe.get_doc({
				"doctype": "ITS Review Project",
				"name": p["id"],
				"project_name": p.get("name"),
				"customer": p.get("customer"),
				"project_type": p.get("project_type", "TRADING"),
				"status": p.get("status", "Active"),
				"contract_no": p.get("contract_no"),
				"po_no": p.get("po_no")
			})
			doc.insert()
		else:
			doc = frappe.get_doc("ITS Review Project", p["id"])
			doc.project_name = p.get("name")
			doc.customer = p.get("customer")
			doc.status = p.get("status", "Active")
			doc.contract_no = p.get("contract_no")
			doc.po_no = p.get("po_no")
			doc.save()

	# Process skids
	for s in state.get("skids", []):
		if not frappe.db.exists("ITS Review Skid", s["id"]):
			doc = frappe.get_doc({
				"doctype": "ITS Review Skid",
				"name": s["id"],
				"project_id": s.get("projectId"),
				"skid_number": s.get("number"),
				"well_number": s.get("well"),
				"serial_number": s.get("serial"),
				"skid_type": s.get("skidType"),
				"rating": s.get("rating"),
				"location": s.get("location"),
				"status": s.get("status", "Not Started")
			})
			doc.insert()
		else:
			doc = frappe.get_doc("ITS Review Skid", s["id"])
			doc.skid_number = s.get("number")
			doc.well_number = s.get("well")
			doc.serial_number = s.get("serial")
			doc.skid_type = s.get("skidType")
			doc.rating = s.get("rating")
			doc.location = s.get("location")
			doc.status = s.get("status")
			doc.save()

	# Incremental revision bump
	new_revision = current_revision + 1
	frappe.db.set_single_value("ITS Review Settings", "workspace_revision", new_revision)

	return {"revision": new_revision}

@frappe.whitelist()
def get_records():
	"""
	Returns shared business records stored in MariaDB for persistence adapter.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	_ensure_initial_db_setup()

	documents = frappe.get_all(
		"ITS Review Document",
		fields=["name", "project_id", "title", "category", "status", "review_comments"]
	)

	records = []
	for doc in documents:
		if doc.review_comments:
			try:
				rec_data = json.loads(doc.review_comments)
				if isinstance(rec_data, dict):
					records.append(rec_data)
					continue
			except Exception:
				pass
		records.append({
			"id": doc.name,
			"type": doc.category or "engineering",
			"project": doc.project_id or "ITS-024",
			"title": doc.title,
			"status": doc.status or "Draft",
			"owner": "Commercial",
			"due": frappe.utils.today(),
			"priority": "Normal",
			"fields": {},
			"lines": [],
			"docs": [],
			"history": []
		})

	revision = frappe.db.get_single_value("ITS Review Settings", "shared_revision") or 1
	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"records": records,
		"revision": revision,
		"token": token
	}

@frappe.whitelist()
def save_records(records=None, revision=None):
	"""
	Saves or updates shared business records in MariaDB tabITS Review Document.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if isinstance(records, str):
		records = json.loads(records)

	if not isinstance(records, list):
		records = []

	current_revision = frappe.db.get_single_value("ITS Review Settings", "shared_revision") or 1
	if revision is not None and int(revision) != current_revision:
		frappe.throw(_("Records modified elsewhere. Please refresh before saving."), frappe.ConcurrencyError)

	_ensure_initial_db_setup()

	for rec in records:
		rec_id = rec.get("id")
		if not rec_id:
			continue

		proj_id = rec.get("project") or "ITS-024"
		if not frappe.db.exists("ITS Review Project", proj_id):
			proj_doc = frappe.get_doc({
				"doctype": "ITS Review Project",
				"name": proj_id,
				"project_name": "Project " + proj_id,
				"customer": rec.get("fields", {}).get("customer", "Client"),
				"project_type": "POWERSKID" if "SK" in proj_id else "TRADING",
				"status": "Active"
			})
			proj_doc.insert()

		title = rec.get("title") or "Document " + rec_id
		category = rec.get("type") or "engineering"
		status = rec.get("status") if rec.get("status") in ["Draft", "Submitted", "Approved", "Returned"] else "Draft"
		comments_json = json.dumps(rec)

		if frappe.db.exists("ITS Review Document", rec_id):
			doc = frappe.get_doc("ITS Review Document", rec_id)
			doc.project_id = proj_id
			doc.title = title
			doc.category = category
			doc.status = status
			doc.review_comments = comments_json
			doc.save()
		else:
			doc = frappe.get_doc({
				"doctype": "ITS Review Document",
				"name": rec_id,
				"project_id": proj_id,
				"title": title,
				"category": category,
				"reference": rec_id,
				"status": status,
				"owner": rec.get("owner", "Commercial"),
				"review_comments": comments_json
			})
			doc.insert()

	new_revision = current_revision + 1
	frappe.db.set_single_value("ITS Review Settings", "shared_revision", new_revision)

	return {"revision": new_revision}

def _ensure_initial_db_setup():
	"""
	Pre-populates MariaDB tables with baseline initial records if empty.
	"""
	if frappe.db.count("ITS Review Project") == 0:
		projects = [
			{"id": "ITS-024", "name": "PSS demonstration project", "customer": "Demo Energy Client", "project_type": "POWERSKID", "status": "Active"},
			{"id": "ITS-026", "name": "Metering package", "customer": "Demo EPC Client", "project_type": "TRADING", "status": "Active"}
		]
		for p in projects:
			if not frappe.db.exists("ITS Review Project", p["id"]):
				frappe.get_doc({
					"doctype": "ITS Review Project",
					"name": p["id"],
					"project_name": p["name"],
					"customer": p["customer"],
					"project_type": p["project_type"],
					"status": p["status"]
				}).insert()
		frappe.db.commit()

	if frappe.db.count("ITS Review Party") == 0:
		parties = [
			{"id": "CUST-001", "kind": "Customer", "party_name": "Demo Energy Client", "country": "UAE", "status": "Active"},
			{"id": "CUST-002", "kind": "Customer", "party_name": "Demo EPC Client", "country": "UAE", "status": "Active"},
			{"id": "SUPP-001", "kind": "Supplier", "party_name": "Demo Equipment Supplier", "country": "UAE", "status": "Active"},
			{"id": "SUPP-002", "kind": "Supplier", "party_name": "Demo Drives Supplier", "country": "UAE", "status": "Active"}
		]
		for party in parties:
			if not frappe.db.exists("ITS Review Party", party["id"]):
				frappe.get_doc({
					"doctype": "ITS Review Party",
					"name": party["id"],
					"kind": party["kind"],
					"party_name": party["party_name"],
					"country": party["country"],
					"status": party["status"]
				}).insert()
		frappe.db.commit()

	if frappe.db.count("ITS Review Material") == 0:
		materials = [
			{"id": "ITS-VSD-01", "code": "ITS-VSD-01", "material_name": "Variable speed drive package", "unit": "Set", "unit_price": 185000.0, "currency": "AED", "status": "Active"},
			{"id": "ITS-ENG-01", "code": "ITS-ENG-01", "material_name": "Engineering, testing and documentation", "unit": "Lot", "unit_price": 15000.0, "currency": "AED", "status": "Active"},
			{"id": "ITS-MTR-01", "code": "ITS-MTR-01", "material_name": "Metering instrument package", "unit": "Set", "unit_price": 45000.0, "currency": "AED", "status": "Active"}
		]
		for mat in materials:
			if not frappe.db.exists("ITS Review Material", mat["id"]):
				frappe.get_doc({
					"doctype": "ITS Review Material",
					"name": mat["id"],
					"code": mat["code"],
					"material_name": mat["material_name"],
					"unit": mat["unit"],
					"unit_price": mat["unit_price"],
					"currency": mat["currency"],
					"status": mat["status"]
				}).insert()
		frappe.db.commit()

	if frappe.db.count("ITS Review Skid") == 0:
		if not frappe.db.exists("ITS Review Skid", "SK-024"):
			frappe.get_doc({
				"doctype": "ITS Review Skid",
				"name": "SK-024",
				"project_id": "ITS-024",
				"skid_number": "SK-024",
				"well_number": "W-017",
				"serial_number": "ITS-DEMO-0024",
				"skid_type": "Variable Speed Drive Package",
				"rating": "800 kVA",
				"location": "ITS Workshop",
				"status": "In Progress"
			}).insert()
		frappe.db.commit()

	if frappe.db.count("ITS Review Document") == 0:
		docs_seed = [
			{"id": "RFQ-201", "type": "inquiry", "project": "ITS-024", "title": "Client inquiry", "status": "Approved", "owner": "Commercial", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "QUO-202", "type": "quotation", "project": "ITS-024", "title": "Quotation", "status": "Approved", "owner": "Commercial", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "SO-203", "type": "order", "project": "ITS-024", "title": "Sales order", "status": "Approved", "owner": "Commercial", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "PLN-204", "type": "plan", "project": "ITS-024", "title": "Project plan", "status": "Approved", "owner": "Projects", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "ENG-205", "type": "engineering", "project": "ITS-024", "title": "General arrangement drawing · Rev A", "status": "Approved", "owner": "Projects", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "MR-206", "type": "material", "project": "ITS-024", "title": "Material request", "status": "Approved", "owner": "Procurement", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "PO-207", "type": "purchase", "project": "ITS-024", "title": "Purchase order", "status": "Approved", "owner": "Procurement", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "WO-208", "type": "fabrication", "project": "ITS-024", "title": "Fabrication / work order", "status": "Approved", "owner": "Service & Workshop", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "TST-209", "type": "inspection", "project": "ITS-024", "title": "FAT · PSS demonstration project", "status": "Approved", "owner": "Quality", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "SHP-210", "type": "shipment", "project": "ITS-024", "title": "Shipment & customs", "status": "Approved", "owner": "Logistics", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "DN-211", "type": "delivery", "project": "ITS-024", "title": "Site delivery", "status": "Approved", "owner": "Logistics", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "COM-212", "type": "commission", "project": "ITS-024", "title": "Commissioning & acceptance", "status": "Approved", "owner": "Quality", "due": frappe.utils.add_days(frappe.utils.today(), 7)},
			{"id": "INV-213", "type": "invoice", "project": "ITS-024", "title": "Delivery milestone · Awaiting client SES", "status": "Draft", "owner": "Finance", "due": frappe.utils.add_days(frappe.utils.today(), 3)},
			{"id": "PCH-214", "type": "punch", "project": "ITS-026", "title": "Confirm instrument tag labels", "status": "Draft", "owner": "Quality", "due": frappe.utils.add_days(frappe.utils.today(), -1)}
		]
		for d in docs_seed:
			if not frappe.db.exists("ITS Review Document", d["id"]):
				full_rec = {
					"id": d["id"],
					"type": d["type"],
					"project": d["project"],
					"title": d["title"],
					"status": d["status"],
					"owner": d["owner"],
					"due": d["due"],
					"priority": "Normal",
					"source": None,
					"fields": {
						"customer": "Demo Energy Client" if d["project"] == "ITS-024" else "Demo EPC Client",
						"manager": "Project Manager",
						"site": "Demo Onshore Site" if d["project"] == "ITS-024" else "Demo Process Facility",
						"tag": "VSD-024" if d["project"] == "ITS-024" else "MTR-026",
						"serial": "ITS-DEMO-0024" if d["project"] == "ITS-024" else "ITS-DEMO-0026",
						"skid": "SK-024" if d["project"] == "ITS-024" else "SK-026",
						"well": "W-017" if d["project"] == "ITS-024" else "W-026"
					},
					"lines": [
						{"code": "ITS-VSD-01", "description": "Variable speed drive package", "qty": 1, "unit": "Set", "rate": 185000}
					] if d["project"] == "ITS-024" else [
						{"code": "ITS-MTR-01", "description": "Metering instrument package", "qty": 1, "unit": "Set", "rate": 45000}
					],
					"taxRate": 5 if d["type"] == "invoice" else 0,
					"notes": "",
					"docs": [
						{"label": "Client inquiry", "reference": "REF-" + d["id"], "state": "Accepted"}
					],
					"history": [
						{"time": frappe.utils.now(), "action": "Created and seeded into MariaDB", "actor": "Administrator"}
					],
					"revision": 1
				}
				frappe.get_doc({
					"doctype": "ITS Review Document",
					"name": d["id"],
					"project_id": d["project"],
					"title": d["title"],
					"category": d["type"],
					"reference": d["id"],
					"status": d["status"],
					"owner": d["owner"],
					"review_comments": json.dumps(full_rec)
				}).insert()
		frappe.db.commit()


TYPE_MAP = {
	"inquiry": "Opportunity",
	"quotation": "Quotation",
	"order": "Sales Order",
	"purchase": "Purchase Order",
	"invoice": "Sales Invoice",
	"delivery": "Delivery Note",
	"material": "Material Request",
	"inspection": "Quality Inspection",
	"shipment": "Purchase Receipt",
	"employee": "Employee",
	"timesheet": "Timesheet",
	"project": "Project",
	"customer": "Customer",
	"supplier": "Supplier",
	"contract": "Contract",
	"skid": "ITS Review Skid",
	"skids": "ITS Review Skid",
	"event": "ITS Review Event",
	"events": "ITS Review Event",
	"punch": "ITS Review Punch",
	"punches": "ITS Review Punch",
	"commissioning": "ITS Review Commissioning",
	"handover": "ITS Review Handover",
	"handovers": "ITS Review Handover",
	"document": "ITS Review Document",
	"documents": "ITS Review Document",
	"activity": "ITS Review Activity",
	"activities": "ITS Review Activity",
	"materials": "ITS Review Material",
	"material_item": "ITS Review Material",
	"equipment": "Item",
	"Item": "Item",
	"services": "ITS Review Register",
	"legal": "ITS Review Register",
	"products": "Item",
	"clients": "Customer",
	"suppliers": "Supplier",
	"orders": "Sales Order",
	"invoices": "Sales Invoice",
	"quotations": "Quotation",
	"purchases": "Purchase Order",
	"deliveries": "Delivery Note",
	"payment": "Payment Entry",
	"payments": "Payment Entry",
	"supplierInvoice": "Purchase Invoice",
	"supplierRFQ": "Request for Quotation",
	"Customer invoice": "Sales Invoice",
	"Sales order": "Sales Order",
	"Sales order & contract": "Sales Order",
	"Purchase order": "Purchase Order",
	"Site delivery": "Delivery Note",
	"Shipment & customs": "Purchase Receipt",
	"FAT / IFAT / SAT": "ITS Review Event",
	"SKID register & interfaces": "ITS Review Skid",
	"Engineering document": "ITS Review Document",
	"Punch point": "ITS Review Punch",
	"Commissioning & acceptance": "ITS Review Commissioning",
	"Supplier invoice match": "Purchase Invoice",
	"Contract obligation": "Contract",
	"Inquiry": "Opportunity",
	"Quotation": "Quotation",
	"Project plan": "Project",
	"Project task": "Project",
	"Estimate & budget": "Quotation",
	"Material request": "Material Request",
	"Supplier enquiry & comparison": "Request for Quotation",
	"Subcontract certificate": "Purchase Order",
	"Stock receipt / movement": "Stock Entry",
	"Employee & manpower": "Employee",
	"Timesheet": "Timesheet",
	"Site access & permits": "ITS Review Document",
	"Payroll review": "Payroll Entry",
	"Fabrication / work order": "Work Order",
	"Asset & equipment": "Asset",
	"Maintenance / calibration": "Maintenance Schedule",
	"Warranty / AMC ticket": "Issue",
	"Payment follow-up": "Payment Entry",
	"Retention & financial closure": "Sales Invoice",
	"Expense / reconciliation": "Journal Entry",
	"Management exception": "ITS Review Document",
	"Document template register": "ITS Review Document",
	"Approval matrix": "Workflow",
	"General inspection follow-up": "ITS Review Document",
	"Line Item Contract": "Contract",
	"RFI": "Opportunity",
	"Project closure": "Project"
}

def resolve_target_doctype(doctype, name):
	# 1. If doctype and name are given and record exists in doctype, return it
	if doctype and frappe.db.exists("DocType", doctype):
		if not name or frappe.db.exists(doctype, name):
			return doctype

	# 2. Check mapped type from TYPE_MAP
	if doctype and doctype in TYPE_MAP:
		mapped = TYPE_MAP[doctype]
		if frappe.db.exists("DocType", mapped):
			if not name or frappe.db.exists(mapped, name):
				return mapped

	# 3. Search candidate DocTypes where name actually exists in DB
	if name:
		candidates = [
			doctype,
			TYPE_MAP.get(doctype) if doctype else None,
			"Sales Order",
			"Quotation",
			"Purchase Order",
			"Delivery Note",
			"Sales Invoice",
			"Purchase Receipt",
			"Purchase Invoice",
			"Payment Entry",
			"Quality Inspection",
			"Material Request",
			"Opportunity",
			"Request for Quotation",
			"Supplier Quotation",
			"Stock Entry",
			"ITS Review Skid",
			"ITS Review Event",
			"ITS Review Punch",
			"ITS Review Commissioning",
			"ITS Review Handover",
			"ITS Review Document",
			"ITS Review Activity",
			"ITS Review Project",
			"ITS Review Material",
			"ITS Review Register",
			"ITS Review Party",
			"Customer",
			"Supplier",
			"Item",
			"Project",
			"Contract",
			"Project Contract",
			"Employee",
			"Timesheet",
			"Issue",
			"Work Order",
			"Asset"
		]
		for dt in candidates:
			if dt and frappe.db.exists("DocType", dt) and frappe.db.exists(dt, name):
				return dt

	return doctype or "ITS Review Document"

@frappe.whitelist()
def get_document_workflow_state(doctype=None, name=None):
	"""
	Returns the authoritative, dynamic workflow and submission progress model
	for a given document based strictly on native Frappe DocType metadata, active
	Workflow configurations, transition graphs, docstatus, and frappe.session.user permissions.
	
	Strictly implements the 3 categories:
	Category A: Document has an active Frappe Workflow -> returns real workflow states,
	            graph-derived progression steps, and user-permitted transitions.
	Category B: No Workflow, but DocType is submittable (is_submittable = 1) -> returns
	            exactly a 2-step progress model (Draft Created -> Submitted) using docstatus.
	Category C: Non-submittable (is_submittable = 0) and No Workflow -> progress_mode = "hidden",
	            steps = [], progress bar must be completely hidden.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name:
		frappe.throw(_("Document name/ID is required"))

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.db.exists(real_doctype, name):
		frappe.throw(_("Document {0} {1} not found").format(real_doctype, name), frappe.DoesNotExistError)

	# Permission check: Read permission is required to view document workflow
	if not frappe.has_permission(real_doctype, "read", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to view {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	meta = frappe.get_meta(real_doctype)
	is_submittable = bool(meta.is_submittable)

	# Check for active workflow in native Frappe
	workflow_name = frappe.model.workflow.get_workflow_name(real_doctype)

	can_edit = bool(doc.docstatus == 0 and frappe.has_permission(real_doctype, "write", doc=doc))
	can_submit = bool(is_submittable and doc.docstatus == 0 and frappe.has_permission(real_doctype, "submit", doc=doc))
	can_cancel = bool(is_submittable and doc.docstatus == 1 and frappe.has_permission(real_doctype, "cancel", doc=doc))

	# -------------------------------------------------------------------------
	# CATEGORY A: DOCUMENT HAS A FRAPPE WORKFLOW
	# -------------------------------------------------------------------------
	if workflow_name:
		workflow = frappe.get_doc("Workflow", workflow_name)
		state_field = workflow.workflow_state_field or "workflow_state"
		current_state = doc.get(state_field)
		if not current_state and workflow.states:
			current_state = workflow.states[0].state
			doc.set(state_field, current_state)
			if not frappe.db.get_value(real_doctype, name, state_field):
				frappe.db.set_value(real_doctype, name, state_field, current_state, update_modified=False)

		# Get user-permitted transitions via native Frappe API
		permitted_transitions_raw = frappe.model.workflow.get_transitions(doc, workflow=workflow)
		permitted_transitions = []
		for t in permitted_transitions_raw:
			permitted_transitions.append({
				"action": t.action,
				"label": t.action,
				"state": t.state,
				"next_state": t.next_state,
				"allowed": t.allowed
			})

		# Get all available transitions from current state
		available_transitions = []
		for t in workflow.transitions:
			if t.state == current_state:
				available_transitions.append({
					"action": t.action,
					"label": t.action,
					"state": t.state,
					"next_state": t.next_state,
					"allowed": t.allowed
				})

		# Fetch workflow audit trail from native Comments
		workflow_comments = frappe.get_all(
			"Comment",
			filters={
				"reference_doctype": real_doctype,
				"reference_name": name,
				"comment_type": "Workflow"
			},
			fields=["content", "creation", "comment_email"],
			order_by="creation asc"
		)
		
		# Build set of completed states from history
		completed_states = set()
		first_state = workflow.states[0].state if workflow.states else "Draft"
		if current_state != first_state:
			completed_states.add(first_state)

		for c in workflow_comments:
			if c.content and c.content != current_state:
				completed_states.add(c.content)

		# Build the workflow steps graph
		steps = []
		step_index = 1
		for s in workflow.states:
			state_name = s.state

			# Terminal rejection / cancellation states (doc_status == '2') are alternative branches:
			# Only show them if reached in history or currently active
			if s.doc_status == '2' and state_name != current_state and state_name not in completed_states:
				continue

			# Determine step status
			if state_name == current_state:
				if s.doc_status == '2':
					status = "cancelled"
				elif "Return" in state_name or "Reject" in state_name:
					status = "returned"
				elif s.doc_status == '1' and doc.docstatus == 1:
					status = "completed"
				else:
					status = "active"
			elif state_name in completed_states:
				status = "completed"
			else:
				status = "pending"

			is_current = (state_name == current_state)
			can_transition_to = any(t["next_state"] == state_name for t in permitted_transitions)
			step_actions = [t for t in permitted_transitions if t["next_state"] == state_name]

			steps.append({
				"index": step_index,
				"state": state_name,
				"label": state_name,
				"status": status,
				"doc_status": s.doc_status,
				"role": s.allow_edit or "",
				"is_current": is_current,
				"can_transition_to": can_transition_to,
				"permitted_actions": step_actions
			})
			step_index += 1

		current_step_obj = next((s for s in steps if s["is_current"]), None)
		completed_step_list = [s["state"] for s in steps if s["status"] == "completed"]
		pending_step_list = [s["state"] for s in steps if s["status"] == "pending"]

		return {
			"has_workflow": True,
			"is_submittable": is_submittable,
			"progress_mode": "workflow",
			"workflow_name": workflow_name,
			"state_field": state_field,
			"current_state": current_state,
			"current_docstatus": doc.docstatus,
			"steps": steps,
			"current_step": current_step_obj,
			"completed_steps": completed_step_list,
			"pending_steps": pending_step_list,
			"available_transitions": available_transitions,
			"permitted_transitions": permitted_transitions,
			"can_edit": can_edit,
			"can_submit": can_submit,
			"can_cancel": can_cancel
		}

	# -------------------------------------------------------------------------
	# CATEGORY B: NO WORKFLOW, BUT DOCTYPE IS SUBMITTABLE
	# -------------------------------------------------------------------------
	elif is_submittable:
		# Exactly 2 steps: Draft Created -> Submitted
		if doc.docstatus == 0:
			steps = [
				{"index": 1, "state": "Draft", "label": "Draft Created", "status": "active", "is_current": True, "docstatus": 0, "role": "Author"},
				{"index": 2, "state": "Submitted", "label": "Submitted", "status": "pending", "is_current": False, "docstatus": 1, "role": "Approver"}
			]
			current_state = "Draft"
		elif doc.docstatus == 1:
			steps = [
				{"index": 1, "state": "Draft", "label": "Draft Created", "status": "completed", "is_current": False, "docstatus": 0, "role": "Author"},
				{"index": 2, "state": "Submitted", "label": "Submitted", "status": "completed", "is_current": True, "docstatus": 1, "role": "Approver"}
			]
			current_state = "Submitted"
		else: # docstatus == 2 (Cancelled)
			steps = [
				{"index": 1, "state": "Draft", "label": "Draft Created", "status": "completed", "is_current": False, "docstatus": 0, "role": "Author"},
				{"index": 2, "state": "Cancelled", "label": "Cancelled", "status": "cancelled", "is_current": True, "docstatus": 2, "role": "Approver"}
			]
			current_state = "Cancelled"

		permitted_transitions = []
		if can_submit:
			permitted_transitions.append({
				"action": "Submit",
				"label": "Submit Document",
				"state": "Draft",
				"next_state": "Submitted",
				"is_primary": True
			})
		if can_cancel:
			permitted_transitions.append({
				"action": "Cancel",
				"label": "Cancel Document",
				"state": "Submitted",
				"next_state": "Cancelled",
				"is_danger": True
			})

		return {
			"has_workflow": False,
			"is_submittable": True,
			"progress_mode": "submission",
			"workflow_name": None,
			"state_field": "docstatus",
			"current_state": current_state,
			"current_docstatus": doc.docstatus,
			"steps": steps,
			"current_step": next((s for s in steps if s["is_current"]), None),
			"completed_steps": [s["state"] for s in steps if s["status"] == "completed"],
			"pending_steps": [s["state"] for s in steps if s["status"] == "pending"],
			"available_transitions": permitted_transitions,
			"permitted_transitions": permitted_transitions,
			"can_edit": can_edit,
			"can_submit": can_submit,
			"can_cancel": can_cancel
		}

	# -------------------------------------------------------------------------
	# CATEGORY C: NON-SUBMITTABLE AND NO WORKFLOW
	# -------------------------------------------------------------------------
	else:
		raw_status = getattr(doc, "status", None) or "Active"
		return {
			"has_workflow": False,
			"is_submittable": False,
			"progress_mode": "hidden",
			"workflow_name": None,
			"state_field": None,
			"current_state": raw_status,
			"current_docstatus": doc.docstatus,
			"steps": [],
			"current_step": None,
			"completed_steps": [],
			"pending_steps": [],
			"available_transitions": [],
			"permitted_transitions": [],
			"can_edit": can_edit,
			"can_submit": False,
			"can_cancel": False
		}

@frappe.whitelist()
def execute_document_workflow_action(doctype=None, name=None, action=None, expected_modified=None):
	"""
	Executes a workflow state transition or submission lifecycle action natively.
	- Validates frappe.session.user authentication
	- Checks read and operation permissions
	- Concurrency check: validates expected_modified against doc.modified
	- For Category A: executes frappe.model.workflow.apply_workflow
	- For Category B: executes native doc.submit() or doc.cancel()
	- Returns refreshed document detail and workflow state
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name or not action:
		frappe.throw(_("Document name and action are required"))

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.db.exists(real_doctype, name):
		frappe.throw(_("Document {0} {1} not found").format(real_doctype, name), frappe.DoesNotExistError)

	# Read permission
	if not frappe.has_permission(real_doctype, "read", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to view {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)

	# Concurrency check (stale document protection)
	if expected_modified and str(doc.modified) != str(expected_modified):
		frappe.throw(_("The document has been modified by another process (Current: {0}, Expected: {1}). Please refresh the page before proceeding.").format(
			doc.modified, expected_modified
		), frappe.ValidationError)

	workflow_name = frappe.model.workflow.get_workflow_name(real_doctype)

	if workflow_name:
		# CATEGORY A: Frappe native workflow execution
		workflow = frappe.get_doc("Workflow", workflow_name)
		state_field = workflow.workflow_state_field or "workflow_state"
		if not doc.get(state_field) and workflow.states:
			initial_state = workflow.states[0].state
			doc.set(state_field, initial_state)
			if not frappe.db.get_value(real_doctype, name, state_field):
				frappe.db.set_value(real_doctype, name, state_field, initial_state, update_modified=False)

		# Validate user has transition permission
		permitted_transitions = frappe.model.workflow.get_transitions(doc, workflow=workflow)
		matching = [t for t in permitted_transitions if t.action == action]
		if not matching:
			frappe.throw(_("Workflow action '{0}' is not permitted for your role or conditions are not satisfied on document {1}.").format(
				action, name
			), frappe.PermissionError)

		# Apply native workflow transition with BRD business gates
		validate_document_gates(doc, action)
		doc = frappe.model.workflow.apply_workflow(doc, action)
		frappe.db.commit()

	else:
		# CATEGORY B: Native DocType submission / cancellation
		meta = frappe.get_meta(real_doctype)
		if not meta.is_submittable:
			frappe.throw(_("Document type {0} is neither workflow-enabled nor submittable").format(real_doctype), frappe.ValidationError)

		if action == "Submit":
			if not frappe.has_permission(real_doctype, "submit", doc=doc):
				frappe.throw(_("Access Denied: You do not have permission to submit {0}").format(name), frappe.PermissionError)
			if doc.docstatus != 0:
				frappe.throw(_("Document {0} is not in Draft state (current docstatus: {1})").format(name, doc.docstatus))
			validate_document_gates(doc, action)
			doc.submit()
			doc.add_comment("Workflow", "Submitted")
			frappe.db.commit()

		elif action == "Cancel":
			if not frappe.has_permission(real_doctype, "cancel", doc=doc):
				frappe.throw(_("Access Denied: You do not have permission to cancel {0}").format(name), frappe.PermissionError)
			if doc.docstatus != 1:
				frappe.throw(_("Document {0} cannot be cancelled because it is not submitted (current docstatus: {1})").format(name, doc.docstatus))
			doc.cancel()
			doc.add_comment("Workflow", "Cancelled")
			frappe.db.commit()

		else:
			frappe.throw(_("Invalid submission action: '{0}'. Supported actions are 'Submit' and 'Cancel'.").format(action))

	return get_document_detail(real_doctype, name)

@frappe.whitelist()
def get_document_detail(doctype=None, name=None):
	"""
	Fetches a single real ERPNext/Frappe document with metadata, permissions matrix,
	child tables, attachments, activity history, and dynamic workflow/submission progress model.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name:
		frappe.throw(_("Document name/ID is required"))

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.db.exists(real_doctype, name):
		resolved_name = None
		if real_doctype == "Customer":
			resolved_name = frappe.db.get_value("Customer", {"customer_name": name}, "name")
		elif real_doctype == "Supplier":
			resolved_name = frappe.db.get_value("Supplier", {"supplier_name": name}, "name")
		elif real_doctype == "Item":
			resolved_name = frappe.db.get_value("Item", {"item_code": name}, "name")
		elif real_doctype == "ITS Review Material":
			resolved_name = frappe.db.get_value("ITS Review Material", {"code": name}, "name")
		elif real_doctype == "ITS Review Register":
			resolved_name = frappe.db.get_value("ITS Review Register", {"register_name": name}, "name") or frappe.db.get_value("ITS Review Register", {"code": name}, "name")
		elif real_doctype == "ITS Review Party":
			resolved_name = frappe.db.get_value("ITS Review Party", {"party_name": name}, "name")
		elif real_doctype == "ITS Review Skid":
			resolved_name = frappe.db.get_value("ITS Review Skid", {"skid_number": name}, "name")

		if resolved_name:
			name = resolved_name
		else:
			frappe.throw(_("Document {0} {1} not found").format(real_doctype, name), frappe.DoesNotExistError)

	# Permission check
	if not frappe.has_permission(real_doctype, "read", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to view {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	meta = frappe.get_meta(real_doctype)

	permissions = {
		"read": True,
		"write": bool(frappe.has_permission(real_doctype, "write", doc=doc)),
		"create": bool(frappe.has_permission(real_doctype, "create")),
		"submit": bool(meta.is_submittable and doc.docstatus == 0 and frappe.has_permission(real_doctype, "submit", doc=doc)),
		"cancel": bool(meta.is_submittable and doc.docstatus == 1 and frappe.has_permission(real_doctype, "cancel", doc=doc)),
		"delete": bool(frappe.has_permission(real_doctype, "delete", doc=doc))
	}

	# Retrieve authoritative, dynamic workflow & submission state
	workflow_state = get_document_workflow_state(real_doctype, name)

	# Extract scalar fields
	fields_meta = []
	doc_fields = {}
	ignored_fields = {"docstatus", "idx", "modified_by", "owner", "creation", "modified", "_user_tags", "_comments", "_assign", "_liked_by"}

	for df in meta.fields:
		if df.fieldname in ignored_fields or df.fieldtype in ["Section Break", "Column Break", "HTML", "Fold", "Tab Break"]:
			continue
		fields_meta.append({
			"fieldname": df.fieldname,
			"label": df.label or df.fieldname,
			"fieldtype": df.fieldtype,
			"options": df.options,
			"read_only": bool(df.read_only),
			"reqd": bool(df.reqd),
			"in_list_view": bool(df.in_list_view)
		})
		doc_fields[df.fieldname] = doc.get(df.fieldname)

	# Child tables
	table_fields = []
	tables = {}
	for df in meta.get_table_fields():
		table_meta = frappe.get_meta(df.options)
		cols = []
		for tf in table_meta.fields:
			if tf.fieldname in ignored_fields or tf.fieldtype in ["Section Break", "Column Break", "HTML"]:
				continue
			cols.append({
				"fieldname": tf.fieldname,
				"label": tf.label or tf.fieldname,
				"fieldtype": tf.fieldtype,
				"options": tf.options,
				"read_only": bool(tf.read_only),
				"reqd": bool(tf.reqd)
			})
		rows = []
		for row in doc.get(df.fieldname) or []:
			row_dict = {col["fieldname"]: row.get(col["fieldname"]) for col in cols}
			row_dict["name"] = row.name
			rows.append(row_dict)
		
		table_fields.append({
			"fieldname": df.fieldname,
			"label": df.label or df.fieldname,
			"options": df.options,
			"columns": cols
		})
		tables[df.fieldname] = rows

	# Fetch attachments
	attachments = frappe.get_all(
		"File",
		filters={"attached_to_doctype": real_doctype, "attached_to_name": name},
		fields=["name as id", "file_name as name", "file_size as size", "file_url as url", "creation as created"]
	)

	# Fetch activity comments
	comments = frappe.get_all(
		"Comment",
		filters={"reference_doctype": real_doctype, "reference_name": name},
		fields=["content", "comment_email as actor", "creation as time"],
		order_by="creation desc",
		limit=20
	)
	history = [{
		"time": str(c.time),
		"actor": c.actor or "System",
		"action": c.content
	} for c in comments]

	# Always add document creation step to history
	history.append({
		"time": str(doc.creation),
		"actor": doc.owner or "Administrator",
		"action": "Document created in MariaDB"
	})

	# Handle review_comments payload for ITS Review Document compatibility
	prototype_data = {}
	if real_doctype == "ITS Review Document" and getattr(doc, "review_comments", None):
		try:
			prototype_data = json.loads(doc.review_comments)
			if isinstance(prototype_data.get("history"), list):
				for h in prototype_data["history"]:
					if not any(x["action"] == h.get("action") for x in history):
						history.append({
							"time": str(h.get("time", "")),
							"actor": h.get("actor", "Administrator"),
							"action": h.get("action", "")
						})
		except Exception:
			pass

	# Sort history chronologically descending
	history.sort(key=lambda x: str(x.get("time", "")), reverse=True)

	# Dynamic allowed actions based on workflow state & docstatus
	allowed_actions = {
		"can_edit": bool(doc.docstatus == 0 and permissions["write"]),
		"can_submit": workflow_state["can_submit"],
		"can_cancel": workflow_state["can_cancel"],
		"can_delete": bool(doc.docstatus == 0 and permissions["delete"]),
		"can_print": True,
		"permitted_transitions": workflow_state["permitted_transitions"]
	}

	# Organize field sections for executive presentation
	general_keys = {"title", "project_id", "skid_id", "category", "reference", "revision", "status"}
	stakeholder_keys = {"customer", "supplier", "contact", "owner", "manager", "engineer", "witness", "discipline", "transmittal"}
	schedule_keys = {"due", "submitted_date", "review_due", "planned_date", "actual_date", "target_date", "date"}

	sections = {
		"general": [f for f in fields_meta if f["fieldname"] in general_keys],
		"stakeholders": [f for f in fields_meta if f["fieldname"] in stakeholder_keys],
		"schedule": [f for f in fields_meta if f["fieldname"] in schedule_keys],
		"other": [f for f in fields_meta if f["fieldname"] not in (general_keys | stakeholder_keys | schedule_keys) and f["fieldname"] not in ["review_comments", "previous_revision_id"]]
	}

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"doctype": real_doctype,
		"name": doc.name,
		"title": getattr(doc, "title", None) or getattr(doc, "customer_name", None) or getattr(doc, "supplier_name", None) or doc.name,
		"docstatus": doc.docstatus,
		"status": workflow_state["current_state"],
		"owner": doc.owner,
		"creation": str(doc.creation),
		"modified": str(doc.modified),
		"fields": doc_fields,
		"fields_meta": fields_meta,
		"sections": sections,
		"tables": tables,
		"table_fields": table_fields,
		"permissions": permissions,
		"workflow_state": workflow_state,
		"workflow_steps": workflow_state["steps"],
		"allowed_actions": allowed_actions,
		"attachments": attachments,
		"history": history,
		"prototype_data": prototype_data,
		"token": token
	}

@frappe.whitelist()
def transition_document_workflow(doctype=None, name=None, action=None, comments=None, persona=None):
	"""
	Backward compatibility wrapper that delegates to execute_document_workflow_action.
	"""
	action_map = {
		"submit_review": "Submit for Approval",
		"approve": "Approve",
		"return": "Reject",
		"final_submit": "Submit",
		"cancel": "Cancel"
	}
	real_action = action_map.get(action, action)
	return execute_document_workflow_action(doctype=doctype, name=name, action=real_action)

@frappe.whitelist(allow_guest=True)
def save_document_detail(doctype=None, name=None, data=None):
	"""
	Saves modifications to a document with write permission enforcement and Frappe validation.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name or not data:
		frappe.throw(_("Document name and data are required"))

	if isinstance(data, str):
		data = json.loads(data)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.db.exists(real_doctype, name):
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)

	# Write permission check
	if not frappe.has_permission(real_doctype, "write", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to edit {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	
	if doc.docstatus != 0:
		frappe.throw(_("Submitted or Cancelled documents cannot be edited"))

	# Update scalar fields
	fields_dict = data.get("fields", {})
	for k, v in fields_dict.items():
		if hasattr(doc, k) and k not in ["name", "doctype", "docstatus", "owner", "creation", "modified"]:
			setattr(doc, k, v)

	# Update child tables
	tables_dict = data.get("tables", {})
	for table_field, rows in tables_dict.items():
		if hasattr(doc, table_field):
			doc.set(table_field, [])
			for r in rows:
				doc.append(table_field, r)

	# Specific titles or comments for ITS Review Document
	if real_doctype == "ITS Review Document" and data.get("prototype_data"):
		doc.review_comments = json.dumps(data["prototype_data"])

	doc.save()
	frappe.db.commit()

	return get_document_detail(real_doctype, doc.name)

@frappe.whitelist(allow_guest=True)
def create_document_detail(doctype=None, data=None):
	"""
	Creates a new document with create permission enforcement.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not doctype or not data:
		frappe.throw(_("DocType and document data are required"))

	if isinstance(data, str):
		data = json.loads(data)

	real_doctype = resolve_target_doctype(doctype, None)

	if not frappe.has_permission(real_doctype, "create"):
		frappe.throw(_("Access Denied: You do not have permission to create {0}").format(real_doctype), frappe.PermissionError)

	doc_payload = {"doctype": real_doctype}
	doc_payload.update(data.get("fields", {}))

	tables_dict = data.get("tables", {})
	for table_field, rows in tables_dict.items():
		doc_payload[table_field] = rows

	doc = frappe.get_doc(doc_payload)
	doc.insert()
	frappe.db.commit()

	return get_document_detail(real_doctype, doc.name)

@frappe.whitelist(allow_guest=True)
def submit_document_detail(doctype=None, name=None):
	"""
	Submits a draft document natively via Frappe lifecycle.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.has_permission(real_doctype, "submit", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to submit {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	if doc.docstatus != 0:
		frappe.throw(_("Document is not in Draft state"))

	doc.submit()
	frappe.db.commit()

	return get_document_detail(real_doctype, name)

@frappe.whitelist(allow_guest=True)
def cancel_document_detail(doctype=None, name=None):
	"""
	Cancels a submitted document natively via Frappe lifecycle.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.has_permission(real_doctype, "cancel", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to cancel {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	if doc.docstatus != 1:
		frappe.throw(_("Only submitted documents can be cancelled"))

	doc.cancel()
	frappe.db.commit()

	return get_document_detail(real_doctype, name)

@frappe.whitelist(allow_guest=True)
def delete_document_detail(doctype=None, name=None):
	"""
	Deletes a document natively via Frappe lifecycle with permission verification.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.has_permission(real_doctype, "delete", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to delete {0} {1}").format(real_doctype, name), frappe.PermissionError)

	frappe.delete_doc(real_doctype, name)
	frappe.db.commit()

	return {"ok": True, "message": "Document deleted successfully"}

@frappe.whitelist(allow_guest=True)
def get_document_print(doctype=None, name=None, print_format=None):
	"""
	Renders printable HTML for a real document using high-fidelity ITS corporate print layout.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.has_permission(real_doctype, "read", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to print {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	detail = get_document_detail(real_doctype, name)

	# Try native print format first if specified
	if print_format and print_format != "Standard":
		try:
			native_html = frappe.get_print(real_doctype, name, print_format=print_format)
			if native_html:
				return {"html": native_html, "doctype": real_doctype, "name": name}
		except Exception:
			pass

	from its_erp_review.utils.print_helpers import (
		its_print_company,
		get_its_logo_data_uri,
		get_its_doctype_title,
		get_its_doc_items,
		get_its_doc_totals,
		get_its_field_groups,
		get_its_child_tables,
	)

	context = {
		"doc": doc,
		"company": its_print_company(doc),
		"logo_uri": get_its_logo_data_uri(),
		"doc_title": get_its_doctype_title(doc.doctype),
		"items": get_its_doc_items(doc),
		"totals": get_its_doc_totals(doc),
		"field_groups": get_its_field_groups(doc),
		"child_tables": get_its_child_tables(doc),
		"show_controls": True,
		"frappe": frappe,
		"_": frappe._,
	}

	html = frappe.render_template("its_erp_review/templates/print_formats/its_universal_print.html", context)
	return {"html": html, "doctype": real_doctype, "name": name}

@frappe.whitelist(allow_guest=True)
def get_document_pdf(doctype=None, name=None, view=0, download=0, print_format=None):
	"""
	Generates and returns high-fidelity A4 PDF for a real ERPNext document.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.has_permission(real_doctype, "read", doc=name) and not frappe.has_permission(real_doctype, "print", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to print {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)

	from its_erp_review.utils.print_helpers import (
		its_print_company,
		get_its_logo_data_uri,
		get_its_doctype_title,
		get_its_doc_items,
		get_its_doc_totals,
		get_its_field_groups,
		get_its_child_tables,
	)

	context = {
		"doc": doc,
		"company": its_print_company(doc),
		"logo_uri": get_its_logo_data_uri(),
		"doc_title": get_its_doctype_title(doc.doctype),
		"items": get_its_doc_items(doc),
		"totals": get_its_doc_totals(doc),
		"field_groups": get_its_field_groups(doc),
		"child_tables": get_its_child_tables(doc),
		"show_controls": False,
		"frappe": frappe,
		"_": frappe._,
	}

	html = frappe.render_template("its_erp_review/templates/print_formats/its_universal_print.html", context)

	from frappe.utils.pdf import get_pdf
	opts = {
		"quiet": "",
		"margin-top": "8mm",
		"margin-bottom": "8mm",
		"margin-left": "10mm",
		"margin-right": "10mm",
		"page-size": "A4"
	}
	pdf_bytes = get_pdf(html, options=opts)

	frappe.response.filename = f"{real_doctype}_{name}.pdf"
	frappe.response.filecontent = pdf_bytes
	frappe.response.type = "pdf"
	if int(view or 0):
		frappe.response.display_content_as = "inline"
	else:
		frappe.response.display_content_as = "attachment"

@frappe.whitelist(allow_guest=True)
def get_link_options(doctype=None, txt=""):
	"""
	Returns search options for link fields in edit mode.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not doctype or not frappe.db.exists("DocType", doctype):
		return {"options": []}

	if not frappe.has_permission(doctype, "read"):
		return {"options": []}

	filters = {}
	if txt:
		filters["name"] = ["like", f"%{txt}%"]

	records = frappe.get_list(doctype, filters=filters, fields=["name"], limit=20)
	return {"options": [r.name for r in records]}


