import unittest
import frappe
from its_erp_review.api.documents import save_workspace

class TestWorkflows(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		if not getattr(frappe.local, "site", None):
			frappe.init(site="frappe.com", sites_path="/home/frappe/frappe-bench/sites")
			frappe.connect()

	def setUp(self):
		frappe.set_user("Administrator")

	def test_optimistic_concurrency_mismatch(self):
		initial_state = {
			"projects": [], "skids": [], "events": [], "punches": [],
			"commissioning": [], "documents": [], "activities": [], "handovers": []
		}
		with self.assertRaises(frappe.ConcurrencyError):
			save_workspace(initial_state, revision=99999)
