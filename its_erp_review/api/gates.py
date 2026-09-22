import frappe
from frappe import _

def validate_document_gates(doc, action):
	"""
	Enforces the BRD v1.2 server-side business gates before workflow transition or submission:
	- Gate 1: Client PO Validation (Sales Order)
	- Gate 2: Finance Commitment (Purchase Order)
	- Gate 3: Punch Point Closure (Delivery Note)
	- Gate 4: Invoice Readiness (Sales Invoice)
	"""
	doctype = doc.doctype
	
	# Only validate gates for forward progression / submission / approval actions
	eval_actions = {"submit", "approve", "confirm", "sign", "sign-off", "next level approval", "official erp submission"}
	action_lower = (action or "").strip().lower()
	is_progression = any(k in action_lower for k in eval_actions)
	if not is_progression and action != "Submit":
		return

	# -------------------------------------------------------------------------
	# Gate 1: Sales Order Client PO Validation
	# -------------------------------------------------------------------------
	if doctype == "Sales Order":
		quotation_ref = None
		items = doc.get("items") if isinstance(doc.get("items"), list) else []
		for item in items:
			prev_dt = item.get("prevdoc_doctype") if hasattr(item, "get") else getattr(item, "prevdoc_doctype", None)
			prev_dn = item.get("prevdoc_docname") if hasattr(item, "get") else getattr(item, "prevdoc_docname", None)
			if prev_dt == "Quotation" and prev_dn:
				quotation_ref = prev_dn
				break

		if quotation_ref and frappe.db.exists("Quotation", quotation_ref):
			quotation = frappe.get_doc("Quotation", quotation_ref)
			doc_total = float(doc.grand_total or 0.0)
			qtn_total = float(quotation.grand_total or 0.0)
			if abs(doc_total - qtn_total) > 1.0:
				if not getattr(doc, "po_validation_exception", None):
					frappe.throw(
						_("Client PO must be validated before the Sales Order can proceed. "
						  "Linked Client PO Validation has a mismatch result: Customer PO Total ({0:,.2f}) does not match Quotation {1} ({2:,.2f}).").format(
							doc_total, quotation_ref, qtn_total
						),
						frappe.ValidationError,
						title=_("Client PO Validation Mismatch")
					)

	# -------------------------------------------------------------------------
	# Gate 2: Purchase Order Finance Commitment Gate
	# -------------------------------------------------------------------------
	elif doctype == "Purchase Order":
		proj = getattr(doc, "project", None)
		if proj:
			if frappe.db.exists("DocType", "Finance Commitment"):
				approved_fc = frappe.db.exists("Finance Commitment", {
					"project": proj,
					"approval_status": "Approved"
				})
				if not approved_fc:
					frappe.throw(
						_("Required finance commitment has not been approved for Project '{0}'.").format(proj),
						frappe.ValidationError,
						title=_("Finance Commitment Required")
					)

	# -------------------------------------------------------------------------
	# Gate 3: Delivery Note Critical Punch Points Gate
	# -------------------------------------------------------------------------
	elif doctype == "Delivery Note":
		proj = getattr(doc, "project", None)
		if proj:
			open_punches = 0
			if frappe.db.exists("DocType", "ITS Review Punch"):
				open_punches += frappe.db.count("ITS Review Punch", {
					"project_id": proj,
					"category": ["in", ["Category A", "Critical"]],
					"status": ["!=", "Closed"]
				})
			if frappe.db.exists("DocType", "Snag List"):
				open_punches += frappe.db.count("Snag List", {
					"project": proj,
					"status": ["in", ["Open", "Pending Inspection"]]
				})
			if open_punches > 0:
				frappe.throw(
					_("Delivery is blocked by unresolved critical punch points ({0} open items for Project '{1}').").format(
						open_punches, proj
					),
					frappe.ValidationError,
					title=_("Open Punch Points Block Delivery")
				)

	# -------------------------------------------------------------------------
	# Gate 4: Sales Invoice Invoice Readiness Gate
	# -------------------------------------------------------------------------
	elif doctype == "Sales Invoice":
		proj = getattr(doc, "project", None)
		if proj:
			dn_count = frappe.db.count("Delivery Note", {"project": proj, "docstatus": 1})
			if dn_count == 0:
				frappe.throw(
					_("Invoice readiness requirements are incomplete: No submitted Delivery Note found for project '{0}'.").format(proj),
					frappe.ValidationError,
					title=_("Invoice Readiness Incomplete")
				)

			if frappe.db.exists("DocType", "ITS Review Punch"):
				open_p = frappe.db.count("ITS Review Punch", {
					"project_id": proj,
					"status": ["!=", "Closed"]
				})
				if open_p > 0:
					frappe.throw(
						_("Invoice readiness requirements are incomplete: {0} open punch points remain on project '{1}'.").format(
							open_p, proj
						),
						frappe.ValidationError,
						title=_("Invoice Readiness Incomplete")
					)
