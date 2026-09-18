import frappe
import json
from frappe import _
from its_erp_review.api.permissions import PERSONA_ROLES

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

	# Fetch accessible projects
	projects = frappe.get_list(
		"ITS Review Project",
		fields=["name as id", "project_name as name", "customer", "project_type", "status", "contract_no", "po_no"],
		order_by="creation asc"
	)

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

	punches = frappe.get_list(
		"ITS Review Punch",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "source", "category", "description", "responsible", "assigned", "raised_date as raisedDate", "target_date as targetDate", "priority", "status", "closure_remarks as closureRemarks", "evidence", "closed_date as closedDate"],
		order_by="creation asc"
	)

	commissioning = frappe.get_list(
		"ITS Review Commissioning",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "status", "planned_date as plannedDate", "commissioning_date as commissioningDate", "engineer", "remarks"],
		order_by="creation asc"
	)

	documents = frappe.get_list(
		"ITS Review Document",
		fields=["name as id", "project_id as projectId", "skid_id as skidId", "title", "category", "reference", "revision", "status", "discipline", "transmittal", "owner", "submitted_date as submittedDate", "review_due as reviewDue", "review_comments as reviewComments", "previous_revision_id as previousRevisionId"],
		order_by="creation asc"
	)

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
	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"state": state,
		"revision": revision,
		"permissions": user_info["permissions"],
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
			proj_doc.insert(ignore_permissions=True)

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
			doc.save(ignore_permissions=True)
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
			doc.insert(ignore_permissions=True)

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
				}).insert(ignore_permissions=True)
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
				}).insert(ignore_permissions=True)
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
				}).insert(ignore_permissions=True)
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
			}).insert(ignore_permissions=True)
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
				}).insert(ignore_permissions=True)
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
	"skid": "ITS Review Skid"
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
			"ITS Review Document",
			"ITS Review Party",
			"ITS Review Material",
			"ITS Review Skid",
			"ITS Review Project",
			"Customer",
			"Supplier",
			"Sales Order",
			"Quotation",
			"Purchase Order",
			"Delivery Note",
			"Sales Invoice",
			"Project",
			"Employee",
			"Material Request",
			"Contract"
		]
		for dt in candidates:
			if dt and frappe.db.exists("DocType", dt) and frappe.db.exists(dt, name):
				return dt

	return doctype or "ITS Review Document"

@frappe.whitelist(allow_guest=True)
def get_document_detail(doctype=None, name=None, active_persona=None):
	"""
	Fetches a single real ERPNext/Frappe document with metadata, permissions matrix,
	child tables, attachments, activity history, and multi-stage workflow status.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name:
		frappe.throw(_("Document name/ID is required"))

	real_doctype = resolve_target_doctype(doctype, name)

	if not frappe.db.exists(real_doctype, name):
		frappe.throw(_("Document {0} {1} not found").format(real_doctype, name), frappe.DoesNotExistError)

	# Permission check
	if not frappe.has_permission(real_doctype, "read", doc=name):
		frappe.throw(_("Access Denied: You do not have permission to view {0} {1}").format(real_doctype, name), frappe.PermissionError)

	doc = frappe.get_doc(real_doctype, name)
	meta = frappe.get_meta(real_doctype)

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "ITS Admin" in roles
	persona = active_persona or frappe.cache().hget("its_review_active_persona", user) or "Administrator"
	persona_info = PERSONA_ROLES.get(persona, PERSONA_ROLES.get("Administrator", {}))
	can_persona_approve = "all" in persona_info.get("can_approve", []) or real_doctype in persona_info.get("can_approve", []) or getattr(doc, "category", "") in persona_info.get("can_approve", [])
	can_user_approve = is_admin or can_persona_approve

	permissions = {
		"read": True,
		"write": bool(frappe.has_permission(real_doctype, "write", doc=doc)),
		"create": bool(frappe.has_permission(real_doctype, "create")),
		"submit": bool(meta.is_submittable and doc.docstatus == 0 and frappe.has_permission(real_doctype, "submit", doc=doc)),
		"cancel": bool(meta.is_submittable and doc.docstatus == 1 and frappe.has_permission(real_doctype, "cancel", doc=doc)),
		"delete": bool(frappe.has_permission(real_doctype, "delete", doc=doc))
	}

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

	# Resolve current status
	raw_status = getattr(doc, "status", None)
	if prototype_data.get("status"):
		raw_status = prototype_data["status"]
	elif not raw_status:
		raw_status = "Submitted" if doc.docstatus == 1 else "Cancelled" if doc.docstatus == 2 else "Draft"

	# Workflow steps model
	# States: 'completed', 'active', 'returned', 'pending'
	step1_state = "completed" if raw_status not in ["Draft"] else "active"
	step2_state = "pending"
	if raw_status in ["Pending Review", "Under review"]:
		step2_state = "active"
	elif raw_status == "Returned":
		step2_state = "returned"
	elif raw_status in ["Approved", "Submitted", "Completed"]:
		step2_state = "completed"

	step3_state = "pending"
	if raw_status == "Approved":
		step3_state = "active"
	elif raw_status in ["Submitted", "Completed"]:
		step3_state = "completed"
	elif raw_status == "Cancelled":
		step3_state = "cancelled"

	step4_state = "completed" if raw_status in ["Submitted", "Completed"] else "pending"

	workflow_steps = [
		{"index": 1, "id": "draft", "label": "Draft Created", "role": "Requester / Creator", "state": step1_state},
		{"index": 2, "id": "review", "label": "Department Verification", "role": persona_info["department"], "state": step2_state},
		{"index": 3, "id": "approved", "label": "Management Sign-Off", "role": "Approver / Executive", "state": step3_state},
		{"index": 4, "id": "submitted", "label": "ERP Official Submission", "role": "MariaDB System", "state": step4_state}
	]

	# Calculate role-based allowed actions
	allowed_actions = {
		"can_edit": bool(raw_status in ["Draft", "Returned"] and doc.docstatus == 0 and permissions["write"]),
		"can_submit_review": bool(raw_status in ["Draft", "Returned"] and doc.docstatus == 0),
		"can_approve": bool(raw_status in ["Pending Review", "Under review"] and can_user_approve),
		"can_return": bool(raw_status in ["Pending Review", "Under review"] and can_user_approve),
		"can_final_submit": bool(raw_status == "Approved" and doc.docstatus == 0 and (is_admin or persona in ["Management", "Administrator"])),
		"can_cancel": bool(doc.docstatus == 1 and permissions["cancel"]),
		"can_delete": bool(raw_status in ["Draft", "Returned"] and doc.docstatus == 0 and permissions["delete"]),
		"can_print": True
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
		"status": raw_status,
		"owner": doc.owner,
		"creation": str(doc.creation),
		"modified": str(doc.modified),
		"active_persona": persona,
		"persona_label": persona_info["label"],
		"fields": doc_fields,
		"fields_meta": fields_meta,
		"sections": sections,
		"tables": tables,
		"table_fields": table_fields,
		"permissions": permissions,
		"workflow_steps": workflow_steps,
		"allowed_actions": allowed_actions,
		"attachments": attachments,
		"history": history,
		"prototype_data": prototype_data,
		"token": token
	}

@frappe.whitelist(allow_guest=True)
def transition_document_workflow(doctype=None, name=None, action=None, comments=None, persona=None):
	"""
	Executes a workflow state transition with role-based validation and audit trail logging.
	Supported actions: 'submit_review', 'approve', 'return', 'final_submit', 'cancel'.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name or not action:
		frappe.throw(_("Document name and workflow action are required"))

	real_doctype = resolve_target_doctype(doctype, name)
	if not frappe.db.exists(real_doctype, name):
		frappe.throw(_("Document {0} {1} not found").format(real_doctype, name), frappe.DoesNotExistError)

	active_persona = persona or frappe.cache().hget("its_review_active_persona", user) or "Administrator"
	persona_info = PERSONA_ROLES.get(active_persona, PERSONA_ROLES.get("Administrator", {}))
	is_admin = "System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user)
	can_persona_approve = "all" in persona_info.get("can_approve", []) or real_doctype in persona_info.get("can_approve", [])

	doc = frappe.get_doc(real_doctype, name)
	current_status = getattr(doc, "status", None) or ("Submitted" if doc.docstatus == 1 else "Draft")

	prototype_data = {}
	if real_doctype == "ITS Review Document" and getattr(doc, "review_comments", None):
		try:
			prototype_data = json.loads(doc.review_comments)
			if prototype_data.get("status"):
				current_status = prototype_data["status"]
		except Exception:
			pass

	now_str = str(frappe.utils.now())
	actor_label = f"{user} [{persona_info['label']}]"

	if action == "submit_review":
		if current_status not in ["Draft", "Returned"]:
			frappe.throw(_("Only Draft or Returned records can be submitted for review."))
		new_status = "Pending Review"
		action_label = f"Submitted for review by {actor_label}"
		if comments:
			action_label += f" — Notes: {comments}"

	elif action == "approve":
		if not (is_admin or can_persona_approve):
			frappe.throw(_("Active persona '{0}' does not have authority to approve {1} records. Switch to {2} or Administrator.").format(
				persona_info['label'], real_doctype, persona_info.get('department', 'Management')
			), frappe.PermissionError)
		new_status = "Approved"
		action_label = f"Approved by {actor_label}"
		if comments:
			action_label += f" — Remarks: {comments}"

	elif action == "return":
		if not (is_admin or can_persona_approve):
			frappe.throw(_("Active persona '{0}' does not have authority to return {1} records.").format(persona_info['label'], real_doctype), frappe.PermissionError)
		if not comments or not comments.strip():
			frappe.throw(_("Please provide specific feedback/reason when returning a document for correction."))
		new_status = "Returned"
		action_label = f"Returned for changes by {actor_label} — Reason: {comments}"

	elif action == "final_submit":
		if not (is_admin or active_persona in ["Management", "Administrator"]):
			frappe.throw(_("Final submission requires Executive Management or Administrator role."), frappe.PermissionError)
		meta = frappe.get_meta(real_doctype)
		if meta.is_submittable and doc.docstatus == 0:
			doc.submit()
		new_status = "Submitted"
		action_label = f"Officially submitted and locked in ERPNext by {actor_label}"
		if comments:
			action_label += f" — Notes: {comments}"

	elif action == "cancel":
		if not (is_admin or active_persona in ["Management", "Administrator"]):
			frappe.throw(_("Cancelling requires Executive Management or Administrator role."), frappe.PermissionError)
		meta = frappe.get_meta(real_doctype)
		if meta.is_submittable and doc.docstatus == 1:
			doc.cancel()
		new_status = "Cancelled"
		action_label = f"Cancelled by {actor_label}"
		if comments:
			action_label += f" — Reason: {comments}"
	else:
		frappe.throw(_("Invalid workflow action: {0}").format(action))

	# Update status safely checking select options
	if hasattr(doc, "status"):
		field_meta = doc.meta.get_field("status")
		if field_meta and field_meta.fieldtype == "Select" and field_meta.options:
			valid_opts = [o.strip() for o in field_meta.options.split("\n") if o.strip()]
			if new_status in valid_opts:
				doc.status = new_status
			elif new_status == "Pending Review" and "Submitted" in valid_opts:
				doc.status = "Submitted"
			elif new_status == "Cancelled" and "Returned" in valid_opts:
				doc.status = "Returned"
		else:
			doc.status = new_status

	# Add comment / audit log
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Workflow",
		"reference_doctype": real_doctype,
		"reference_name": name,
		"content": action_label,
		"comment_email": user
	}).insert(ignore_permissions=True)

	# Update prototype_data if ITS Review Document
	if real_doctype == "ITS Review Document":
		if not prototype_data:
			prototype_data = {"id": name, "title": doc.title or name, "history": []}
		prototype_data["status"] = new_status
		if "history" not in prototype_data:
			prototype_data["history"] = []
		prototype_data["history"].append({
			"time": now_str,
			"actor": actor_label,
			"action": action_label
		})
		doc.review_comments = json.dumps(prototype_data)

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return get_document_detail(real_doctype, name, active_persona=active_persona)

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
	native_html = None
	if print_format and print_format != "Standard":
		try:
			native_html = frappe.get_print(real_doctype, name, print_format=print_format)
		except Exception:
			native_html = None

	if native_html:
		return {"html": native_html, "doctype": real_doctype, "name": name}

	# Render Executive ITS Corporate Print Format
	title_text = detail.get("title") or doc.name
	doc_status = detail.get("status") or "Draft"
	category = getattr(doc, "category", "") or real_doctype
	project_id = getattr(doc, "project_id", "") or getattr(doc, "project", "") or "ITS-024"
	creation_date = str(doc.creation)[:10]

	# Extract lines and financials
	lines = []
	subtotal = 0.0
	tax_rate = 5.0

	prototype_data = detail.get("prototype_data", {})
	if prototype_data and prototype_data.get("lines"):
		for idx, l in enumerate(prototype_data["lines"], start=1):
			qty = float(l.get("qty", 1))
			rate = float(l.get("rate", 0))
			amt = qty * rate
			subtotal += amt
			lines.append({
				"idx": idx,
				"code": l.get("code") or "—",
				"part_no": l.get("partNo") or "—",
				"description": l.get("description") or "Item Description",
				"qty": qty,
				"unit": l.get("unit") or "Nos",
				"rate": rate,
				"amount": amt
			})
		tax_rate = float(prototype_data.get("taxRate", 5.0))
	elif detail.get("tables"):
		# Check any child tables
		for tbl_name, rows in detail["tables"].items():
			if rows:
				for idx, r in enumerate(rows, start=1):
					qty = float(r.get("qty", 1))
					rate = float(r.get("rate") or r.get("unit_price") or 0)
					amt = float(r.get("amount") or (qty * rate))
					subtotal += amt
					lines.append({
						"idx": idx,
						"code": r.get("item_code") or r.get("code") or "—",
						"part_no": r.get("part_no") or "—",
						"description": r.get("item_name") or r.get("description") or "Line Item",
						"qty": qty,
						"unit": r.get("uom") or r.get("unit") or "Nos",
						"rate": rate,
						"amount": amt
					})
				break

	if not lines:
		lines.append({
			"idx": 1,
			"code": getattr(doc, "code", None) or getattr(doc, "reference", None) or doc.name,
			"part_no": "—",
			"description": title_text,
			"qty": 1,
			"unit": "Set",
			"rate": subtotal or 185000.0,
			"amount": subtotal or 185000.0
		})
		subtotal = lines[0]["amount"]

	tax_amount = round(subtotal * (tax_rate / 100.0), 2)
	grand_total = subtotal + tax_amount

	def fmt_money(v):
		return f"AED {v:,.2f}"

	rows_html = "".join([f"""
		<tr>
			<td style="text-align:center; padding:8px; border:1px solid #E2E8F0;">{l['idx']}</td>
			<td style="padding:8px; border:1px solid #E2E8F0; font-family:monospace; font-weight:600; color:#002B49;">{l['code']}</td>
			<td style="padding:8px; border:1px solid #E2E8F0;">{l['description']}</td>
			<td style="text-align:right; padding:8px; border:1px solid #E2E8F0;">{l['qty']:g}</td>
			<td style="text-align:center; padding:8px; border:1px solid #E2E8F0;">{l['unit']}</td>
			<td style="text-align:right; padding:8px; border:1px solid #E2E8F0;">{fmt_money(l['rate'])}</td>
			<td style="text-align:right; padding:8px; border:1px solid #E2E8F0; font-weight:600; color:#002B49;">{fmt_money(l['amount'])}</td>
		</tr>
	""" for l in lines])

	customer_name = getattr(doc, "customer", "") or getattr(doc, "customer_name", "") or "Client / Energy Operator"
	owner_name = getattr(doc, "owner", "Administrator")

	html = f"""<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{doc.name} · {real_doctype}</title>
	<style>
		@page {{
			size: A4;
			margin: 15mm 15mm 18mm 15mm;
		}}
		* {{ box-sizing: border-box; }}
		body {{
			font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
			font-size: 11px;
			color: #1E293B;
			line-height: 1.45;
			background: #F1F5F9;
			margin: 0;
			padding: 20px 0;
		}}
		.a4-sheet {{
			width: 210mm;
			min-height: 297mm;
			margin: 0 auto;
			background: #FFFFFF;
			box-shadow: 0 4px 20px rgba(0,0,0,0.12);
			padding: 16mm 18mm;
			position: relative;
		}}
		@media print {{
			body {{ background: #FFFFFF; padding: 0; }}
			.a4-sheet {{
				box-shadow: none;
				width: 100%;
				min-height: auto;
				padding: 0;
				margin: 0;
			}}
			.no-print {{ display: none !important; }}
		}}
		.print-banner {{
			background: #002B49;
			color: #FFFFFF;
			padding: 10px 24px;
			display: flex;
			justify-content: space-between;
			align-items: center;
			max-width: 210mm;
			margin: 0 auto 16px;
			border-radius: 6px;
		}}
		.print-banner button {{
			background: #005A9C;
			color: white;
			border: none;
			padding: 8px 16px;
			border-radius: 4px;
			font-weight: 600;
			cursor: pointer;
		}}
		.corporate-header {{
			border-bottom: 2.5px solid #002B49;
			padding-bottom: 12px;
			margin-bottom: 18px;
			display: flex;
			justify-content: space-between;
			align-items: flex-start;
		}}
		.corp-title {{
			font-size: 16px;
			font-weight: 800;
			color: #002B49;
			letter-spacing: 0.5px;
		}}
		.corp-sub {{
			font-size: 9px;
			color: #64748B;
			margin-top: 3px;
		}}
		.doc-badge {{
			text-align: right;
		}}
		.doc-type-title {{
			font-size: 20px;
			font-weight: 800;
			color: #002B49;
			text-transform: uppercase;
			letter-spacing: 0.5px;
			margin: 0;
		}}
		.doc-id {{
			font-size: 13px;
			font-weight: 700;
			color: #005A9C;
			margin-top: 2px;
		}}
		.status-pill {{
			display: inline-block;
			background: #E2E8F0;
			color: #334155;
			padding: 3px 8px;
			border-radius: 12px;
			font-size: 10px;
			font-weight: 700;
			margin-top: 4px;
			text-transform: uppercase;
		}}
		.status-approved {{ background: #DCFCE7; color: #166534; }}
		.meta-grid {{
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 16px;
			margin-bottom: 20px;
			background: #F8FAFC;
			border: 1px solid #E2E8F0;
			border-radius: 6px;
			padding: 12px 16px;
		}}
		.meta-item {{
			display: flex;
			margin-bottom: 4px;
		}}
		.meta-label {{
			width: 110px;
			color: #64748B;
			font-weight: 600;
			font-size: 10px;
			text-transform: uppercase;
		}}
		.meta-val {{
			font-weight: 600;
			color: #0F172A;
		}}
		table.lines-table {{
			width: 100%;
			border-collapse: collapse;
			margin-bottom: 18px;
		}}
		table.lines-table th {{
			background: #002B49;
			color: #FFFFFF;
			font-size: 10px;
			font-weight: 700;
			text-transform: uppercase;
			padding: 8px;
			border: 1px solid #002B49;
		}}
		table.lines-table tr:nth-child(even) {{
			background: #F8FAFC;
		}}
		.totals-area {{
			display: flex;
			justify-content: flex-end;
			margin-bottom: 28px;
		}}
		.totals-card {{
			width: 260px;
			background: #F8FAFC;
			border: 1px solid #E2E8F0;
			border-radius: 6px;
			padding: 10px 14px;
		}}
		.tot-row {{
			display: flex;
			justify-content: space-between;
			margin-bottom: 6px;
			font-size: 11px;
		}}
		.tot-row.grand {{
			border-top: 1.5px solid #002B49;
			padding-top: 6px;
			margin-top: 6px;
			font-size: 13px;
			font-weight: 800;
			color: #002B49;
		}}
		.signatures {{
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 30px;
			margin-top: 40px;
			border-top: 1px solid #E2E8F0;
			padding-top: 18px;
		}}
		.sig-block {{
			border: 1px dashed #CBD5E1;
			border-radius: 6px;
			padding: 12px;
			background: #FAFAFA;
		}}
		.sig-title {{
			font-weight: 700;
			color: #002B49;
			text-transform: uppercase;
			font-size: 10px;
			margin-bottom: 8px;
		}}
		.sig-line {{
			margin-top: 36px;
			border-bottom: 1px solid #94A3B8;
			display: flex;
			justify-content: space-between;
			padding-bottom: 4px;
			color: #64748B;
			font-size: 9px;
		}}
		.corp-footer {{
			position: absolute;
			bottom: 12mm;
			left: 18mm;
			right: 18mm;
			border-top: 1px solid #CBD5E1;
			padding-top: 8px;
			display: flex;
			justify-content: space-between;
			color: #94A3B8;
			font-size: 9px;
		}}
	</style>
</head>
<body>
	<div class="print-banner no-print">
		<div>
			<strong>ITS Corporate Print Format</strong> · {real_doctype} {doc.name}
		</div>
		<div>
			<button onclick="window.print()">Print / Save as PDF</button>
		</div>
	</div>

	<div class="a4-sheet">
		<header class="corporate-header">
			<div>
				<div class="corp-title">INDEPENDENT TECHNICAL SERVICES L.L.C.</div>
				<div class="corp-sub">Engineering · Power Skid Systems · Industrial Automation</div>
				<div class="corp-sub">Abu Dhabi · United Arab Emirates · TRN: 100234829100003</div>
			</div>
			<div class="doc-badge">
				<h1 class="doc-type-title">{category.upper()}</h1>
				<div class="doc-id">{doc.name}</div>
				<span class="status-pill status-approved">{doc_status}</span>
			</div>
		</header>

		<section class="meta-grid">
			<div>
				<div class="meta-item">
					<div class="meta-label">Project Ref:</div>
					<div class="meta-val">{project_id}</div>
				</div>
				<div class="meta-item">
					<div class="meta-label">Document Title:</div>
					<div class="meta-val">{title_text}</div>
				</div>
				<div class="meta-item">
					<div class="meta-label">Customer / Party:</div>
					<div class="meta-val">{customer_name}</div>
				</div>
			</div>
			<div>
				<div class="meta-item">
					<div class="meta-label">Issue Date:</div>
					<div class="meta-val">{creation_date}</div>
				</div>
				<div class="meta-item">
					<div class="meta-label">Responsible:</div>
					<div class="meta-val">{owner_name}</div>
				</div>
				<div class="meta-item">
					<div class="meta-label">Revision:</div>
					<div class="meta-val">Rev {getattr(doc, 'revision', None) or '01'}</div>
				</div>
			</div>
		</section>

		<table class="lines-table">
			<thead>
				<tr>
					<th style="width:35px">Item</th>
					<th style="width:120px">Code / Part No</th>
					<th>Description & Scope</th>
					<th style="width:60px">Qty</th>
					<th style="width:50px">Unit</th>
					<th style="width:105px">Rate (AED)</th>
					<th style="width:115px">Amount (AED)</th>
				</tr>
			</thead>
			<tbody>
				{rows_html}
			</tbody>
		</table>

		<div class="totals-area">
			<div class="totals-card">
				<div class="tot-row">
					<span>Subtotal</span>
					<strong>{fmt_money(subtotal)}</strong>
				</div>
				<div class="tot-row">
					<span>VAT ({tax_rate:g}%)</span>
					<strong>{fmt_money(tax_amount)}</strong>
				</div>
				<div class="tot-row grand">
					<span>Total Amount</span>
					<span>{fmt_money(grand_total)}</span>
				</div>
			</div>
		</div>

		<section class="signatures">
			<div class="sig-block">
				<div class="sig-title">Prepared & Verified By</div>
				<div style="color:#475569;">{owner_name}</div>
				<div class="sig-line">
					<span>Signature / Stamp</span>
					<span>Date: {creation_date}</span>
				</div>
			</div>
			<div class="sig-block">
				<div class="sig-title">Authorized Approval</div>
				<div style="color:#475569;">Commercial / Operations Director</div>
				<div class="sig-line">
					<span>Executive Sign-Off</span>
					<span>Date: {creation_date}</span>
				</div>
			</div>
		</section>

		<footer class="corp-footer">
			<span>Confidential & Proprietary · Independent Technical Services L.L.C.</span>
			<span>Doc Ref: {doc.name} · Page 1 of 1</span>
		</footer>
	</div>
</body>
</html>"""

	return {"html": html, "doctype": real_doctype, "name": name}

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


