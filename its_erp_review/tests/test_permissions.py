import unittest
import frappe
from its_erp_review.api.permissions import get_user_permissions

class TestPermissions(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		if not getattr(frappe.local, "site", None):
			frappe.init(site="frappe.com", sites_path="/home/frappe/frappe-bench/sites")
			frappe.connect()

	def test_administrator_permissions(self):
		frappe.set_user("Administrator")
		perms = get_user_permissions()
		self.assertTrue(perms["is_admin"])
		self.assertIn("powerskid.admin", perms["permissions"])

	def test_unauthenticated_guest(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_user_permissions()
		frappe.set_user("Administrator")
