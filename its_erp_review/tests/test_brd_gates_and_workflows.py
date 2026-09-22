import unittest
import frappe
from its_erp_review.api.documents import (
	get_document_detail,
	get_document_workflow_state,
	execute_document_workflow_action
)
from its_erp_review.api.gates import validate_document_gates

class TestBRDGatesAndWorkflows(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		if not getattr(frappe.local, "site", None):
			frappe.init(site="frappe.com", sites_path="/home/frappe/frappe-bench/sites")
			frappe.connect()

	@classmethod
	def tearDownClass(cls):
		if frappe.db:
			frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_category_a_workflow_sales_order(self):
		"""Category A: Sales Order has active Frappe Workflow -> returns real states & transitions."""
		orders = frappe.get_all("Sales Order", limit=1)
		if not orders:
			self.skipTest("No Sales Order found in database")
		
		so_name = orders[0].name
		wf = get_document_workflow_state("Sales Order", so_name)
		self.assertTrue(wf.get("has_workflow"))
		self.assertEqual(wf.get("progress_mode"), "workflow")
		self.assertIn("steps", wf)
		self.assertTrue(len(wf["steps"]) >= 2)
		self.assertIn("permitted_transitions", wf)

	def test_category_b_submittable_doc_without_workflow(self):
		"""Category B: Submittable DocType without Workflow -> returns 2-step Draft -> Submitted."""
		dn_list = frappe.get_all("Delivery Note", limit=1)
		if not dn_list:
			self.skipTest("No Delivery Note found in database")
		
		dn_name = dn_list[0].name
		wf = get_document_workflow_state("Delivery Note", dn_name)
		self.assertFalse(wf.get("has_workflow"))
		self.assertTrue(wf.get("is_submittable"))
		self.assertEqual(wf.get("progress_mode"), "submission")
		self.assertEqual(len(wf.get("steps", [])), 2)
		self.assertEqual(wf["steps"][0]["label"], "Draft Created")
		self.assertIn(wf["steps"][1]["label"], ["Submitted", "Cancelled"])

	def test_category_c_non_submittable_master(self):
		"""Category C: Non-submittable master DocType -> progress_mode = 'hidden', steps = []."""
		cust_list = frappe.get_all("Customer", limit=1)
		if not cust_list:
			self.skipTest("No Customer found in database")
		
		cust_name = cust_list[0].name
		wf = get_document_workflow_state("Customer", cust_name)
		self.assertFalse(wf.get("has_workflow"))
		self.assertFalse(wf.get("is_submittable"))
		self.assertEqual(wf.get("progress_mode"), "hidden")
		self.assertEqual(len(wf.get("steps", [])), 0)

	def test_gate1_client_po_validation_mismatch(self):
		"""Gate 1: Sales Order with Quotation discrepancy triggers mismatch error."""
		test_doc = frappe._dict({
			"doctype": "Sales Order",
			"grand_total": 50000.0,
			"items": [frappe._dict({"prevdoc_doctype": "Quotation", "prevdoc_docname": "NON_EXISTENT_Q"})]
		})
		# Should pass cleanly if quotation doesn't exist
		validate_document_gates(test_doc, "Submit")

		# If quotation exists with different amount, it must throw ValidationError
		quotes = frappe.get_all("Quotation", fields=["name", "grand_total"], limit=1)
		if quotes:
			q_name = quotes[0].name
			real_total = float(quotes[0].grand_total or 0.0)
			mismatched_doc = frappe._dict({
				"doctype": "Sales Order",
				"grand_total": real_total + 1000.0,
				"items": [frappe._dict({"prevdoc_doctype": "Quotation", "prevdoc_docname": q_name})]
			})
			with self.assertRaises(frappe.ValidationError):
				validate_document_gates(mismatched_doc, "Submit")

	def test_gate2_finance_commitment_blocks_po(self):
		"""Gate 2: Purchase Order for project without approved Finance Commitment is blocked."""
		test_po = frappe._dict({
			"doctype": "Purchase Order",
			"project": "NON_EXISTENT_PROJECT_FOR_FC_TEST_123"
		})
		with self.assertRaises(frappe.ValidationError):
			validate_document_gates(test_po, "Submit")

	def test_concurrency_protection(self):
		"""Optimistic locking: Mismatched expected_modified rejects the action."""
		orders = frappe.get_all("Sales Order", limit=1)
		if not orders:
			self.skipTest("No Sales Order found")
		
		so_name = orders[0].name
		with self.assertRaises(frappe.ValidationError):
			execute_document_workflow_action(
				doctype="Sales Order",
				name=so_name,
				action="Approve",
				expected_modified="2020-01-01 00:00:00.000000"
			)
