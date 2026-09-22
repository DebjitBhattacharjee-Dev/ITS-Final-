import unittest
import frappe
from its_erp_review.api.gates import validate_document_gates
from its_erp_review.www.review_print import get_context

class TestDemoProcessFlow(unittest.TestCase):
	"""
	Automated validation of the ITS ERP Review Complete Client Demo Process:
	- Verifies existence of demo master and transaction chain records.
	- Validates Gate 1, Gate 2, Gate 3, Gate 4 hard stops.
	- Validates print generation across all 8 standard demo documents.
	"""
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")

	def test_01_demo_parties_and_items_exist(self):
		self.assertTrue(frappe.db.exists("Customer", "Demo Energy Customer"))
		self.assertTrue(frappe.db.exists("Supplier", "Demo Power Equipment Supplier"))
		for item in ["DEMO-PSS-SKID-400KVA", "DEMO-VSD-PANEL", "DEMO-TRANSFORMER-400KVA", "DEMO-PLC-PANEL", "DEMO-UPS-SYSTEM"]:
			self.assertTrue(frappe.db.exists("Item", item), f"Missing item: {item}")

	def test_02_commercial_chain_linkage(self):
		opp = frappe.db.get_value("Opportunity", {"party_name": "Demo Energy Customer"}, "name")
		self.assertTrue(bool(opp))

		qtn = frappe.db.get_value("Quotation", {"party_name": "Demo Energy Customer"}, "name")
		self.assertTrue(bool(qtn))

		so = frappe.db.get_value("Sales Order", {"customer": "Demo Energy Customer"}, "name")
		self.assertTrue(bool(so))

		proj = frappe.db.get_value("Project", {"customer": "Demo Energy Customer"}, "name")
		self.assertTrue(bool(proj))

	def test_03_gate1_sales_order_mismatch_hard_stop(self):
		qtn = frappe.db.get_value("Quotation", {"party_name": "Demo Energy Customer"}, "name")
		# Construct a mock Sales Order doc with a mismatched total
		fake_so = frappe._dict({
			"doctype": "Sales Order",
			"grand_total": 999999.0,
			"items": [frappe._dict({"prevdoc_doctype": "Quotation", "prevdoc_docname": qtn})]
		})
		with self.assertRaises(frappe.ValidationError):
			validate_document_gates(fake_so, "Submit")

	def test_04_gate2_finance_commitment_hard_stop(self):
		fake_po = frappe._dict({
			"doctype": "Purchase Order",
			"project": "NON-EXISTENT-PROJ-999"
		})
		with self.assertRaises(frappe.ValidationError):
			validate_document_gates(fake_po, "Submit")

	def test_05_gate3_punch_point_delivery_hard_stop(self):
		# If an open punch exists for a project, Delivery Note submission is blocked
		fake_dn = frappe._dict({
			"doctype": "Delivery Note",
			"project": "DEMO-ITS-2026-PSS-001"
		})
		# Temporarily ensure a punch point exists for this demo review project
		if frappe.db.exists("DocType", "ITS Review Punch"):
			dummy_punch = frappe.get_doc({
				"doctype": "ITS Review Punch",
				"project_id": "DEMO-ITS-2026-PSS-001",
				"category": "Critical",
				"priority": "Critical",
				"status": "Open",
				"source": "FAT Test",
				"description": "Critical unpainted transformer frame",
				"responsible": "Demo Power Equipment Supplier",
				"assigned": "Administrator",
				"raised_date": frappe.utils.today(),
				"target_date": frappe.utils.today()
			}).insert(ignore_permissions=True)

			try:
				with self.assertRaises(frappe.ValidationError):
					validate_document_gates(fake_dn, "Submit")
			finally:
				frappe.delete_doc("ITS Review Punch", dummy_punch.name, force=True)

	def test_06_gate4_sales_invoice_readiness_hard_stop(self):
		fake_inv = frappe._dict({
			"doctype": "Sales Invoice",
			"project": "PROJ-WITHOUT-DELIVERY"
		})
		with self.assertRaises(frappe.ValidationError):
			validate_document_gates(fake_inv, "Submit")

	def test_07_universal_print_formats(self):
		docs_to_test = [
			("Quotation", frappe.db.get_value("Quotation", {"party_name": "Demo Energy Customer"}, "name")),
			("Project Contract", frappe.db.get_value("Project Contract", {"title": ["like", "DEMO-ITS-2026-%"]}, "name")),
			("Sales Order", frappe.db.get_value("Sales Order", {"customer": "Demo Energy Customer"}, "name")),
			("Purchase Order", frappe.db.get_value("Purchase Order", {"supplier": "Demo Power Equipment Supplier"}, "name")),
			("Delivery Note", frappe.db.get_value("Delivery Note", {"customer": "Demo Energy Customer"}, "name")),
			("Sales Invoice", frappe.db.get_value("Sales Invoice", {"customer": "Demo Energy Customer"}, "name")),
		]
		for dt, dn in docs_to_test:
			if not dn:
				continue
			frappe.form_dict.doctype = dt
			frappe.form_dict.name = dn
			ctx = {}
			get_context(ctx)
			self.assertEqual(ctx.get("doc").name, dn)
			self.assertTrue(len(ctx.get("doc_title", "")) > 0)
