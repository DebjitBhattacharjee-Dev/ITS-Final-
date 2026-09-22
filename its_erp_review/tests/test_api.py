import unittest
import frappe
from its_erp_review.api.permissions import get_user_permissions
from its_erp_review.api.documents import get_workspace
from its_erp_review.api.dashboard import get_dashboard_metrics
from its_erp_review.api.directories import get_parties
from its_erp_review.api.materials import get_materials
from its_erp_review.api.registers import get_registers

class TestITSERPReviewAPI(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		if not getattr(frappe.local, "site", None):
			frappe.init(site="frappe.com", sites_path="/home/frappe/frappe-bench/sites")
			frappe.connect()

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_user_permissions(self):
		res = get_user_permissions()
		self.assertIn("user", res)
		self.assertEqual(res["user"], "Administrator")
		self.assertTrue(res["is_admin"])

	def test_get_workspace(self):
		res = get_workspace()
		self.assertIn("state", res)
		self.assertIn("revision", res)
		self.assertIn("projects", res["state"])

	def test_get_dashboard_metrics(self):
		metrics = get_dashboard_metrics()
		self.assertIn("projects", metrics)
		self.assertIn("skids", metrics)
		self.assertIn("punchOpen", metrics)

	def test_get_directories(self):
		res = get_parties()
		self.assertIn("parties", res)

	def test_get_materials(self):
		res = get_materials()
		self.assertIn("materials", res)

	def test_get_registers(self):
		res = get_registers()
		self.assertIn("rows", res)

	def test_guest_access_denied(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_workspace()
		frappe.set_user("Administrator")
