import unittest
from unittest.mock import patch
import frappe
from its_erp_review.api.documents import (
	get_next_document_preview,
	create_next_document,
	BRD_NEXT_STEP_MAPPING
)

class TestDocumentNextStep(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		if not getattr(frappe.local, "site", None):
			frappe.init(site="frappe.com", sites_path="/home/frappe/frappe-bench/sites")
			frappe.connect()

	@classmethod
	def tearDownClass(cls):
		if frappe.db:
			frappe.db.rollback()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_brd_next_step_mapping_coverage(self):
		"""Verify key BRD v1.2 DocTypes have mapped next steps."""
		required_doctypes = [
			"Opportunity", "Quotation", "Sales Order", "Purchase Order",
			"Purchase Receipt", "Purchase Invoice", "Delivery Note",
			"Sales Invoice", "Payment Entry", "ITS Review Skid",
			"ITS Review Event", "ITS Review Commissioning", "ITS Review Handover"
		]
		for dt in required_doctypes:
			self.assertIn(dt, BRD_NEXT_STEP_MAPPING, f"{dt} must be mapped in BRD_NEXT_STEP_MAPPING")
			rule = BRD_NEXT_STEP_MAPPING[dt]
			self.assertTrue(rule.get("target_doctype"), f"{dt} must have target_doctype")
			self.assertTrue(rule.get("label"), f"{dt} must have label")

	def test_next_document_preview_quotation_to_sales_order(self):
		"""Verify Quotation preview maps to Sales Order with inherited dependencies."""
		quotations = frappe.get_all("Quotation", limit=1)
		if not quotations:
			self.skipTest("No Quotation found in database")

		q_name = quotations[0].name
		preview = get_next_document_preview("Quotation", q_name)
		self.assertEqual(preview["target_doctype"], "Sales Order")
		self.assertIn("Sales Order", preview["target_label"])
		self.assertEqual(preview["source_doctype"], "Quotation")
		self.assertEqual(preview["source_name"], q_name)
		self.assertTrue("defaults" in preview)
		self.assertTrue("customer" in preview["defaults"])
		self.assertTrue("items" in preview["defaults"])

	def test_next_document_preview_sales_order_to_purchase_order(self):
		"""Verify Sales Order preview maps to Purchase Order with inherited project."""
		orders = frappe.get_all("Sales Order", limit=1)
		if not orders:
			self.skipTest("No Sales Order found in database")

		so_name = orders[0].name
		preview = get_next_document_preview("Sales Order", so_name)
		self.assertEqual(preview["target_doctype"], "Purchase Order")
		self.assertIn("Purchase Order", preview["target_label"])
		self.assertEqual(preview["source_doctype"], "Sales Order")
		self.assertEqual(preview["source_name"], so_name)

	def test_next_document_preview_delivery_note_to_invoice(self):
		"""Verify Delivery Note preview maps to Sales Invoice."""
		dns = frappe.get_all("Delivery Note", limit=1)
		if not dns:
			self.skipTest("No Delivery Note found in database")

		dn_name = dns[0].name
		preview = get_next_document_preview("Delivery Note", dn_name)
		self.assertEqual(preview["target_doctype"], "Sales Invoice")
		self.assertIn("Sales Invoice", preview["target_label"])

	def test_next_document_preview_invoice_to_payment_entry(self):
		"""Verify Sales Invoice preview maps to Payment Entry."""
		invoices = frappe.get_all("Sales Invoice", limit=1)
		if not invoices:
			self.skipTest("No Sales Invoice found in database")

		si_name = invoices[0].name
		preview = get_next_document_preview("Sales Invoice", si_name)
		self.assertEqual(preview["target_doctype"], "Payment Entry")
		self.assertIn("Payment Entry", preview["target_label"])

	@patch("frappe.workflow.doctype.workflow_action.workflow_action.send_workflow_action_email")
	def test_create_next_document_execution_quotation_to_so(self, mock_send_email):
		"""Verify create_next_document creates a real linked Sales Order with inherited dependencies."""
		quotations = frappe.get_all("Quotation", limit=1)
		if not quotations:
			self.skipTest("No Quotation found in database")

		q_doc = frappe.get_doc("Quotation", quotations[0].name)
		detail = create_next_document("Quotation", q_doc.name)

		self.assertEqual(detail["doctype"], "Sales Order")
		self.assertEqual(detail["status"], "Draft")
		self.assertTrue(detail["name"].startswith("SAL-ORD-"))

		# Verify dependency linkage in child table
		so_doc = frappe.get_doc("Sales Order", detail["name"])
		self.assertEqual(so_doc.customer, q_doc.party_name)
		if q_doc.items and so_doc.items:
			first_item = so_doc.items[0]
			self.assertEqual(first_item.prevdoc_docname, q_doc.name)

		# Rollback so database remains clean
		frappe.db.rollback()
