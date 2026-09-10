import frappe
from frappe.tests.utils import FrappeTestCase
from its_ui_redesign.api.auth import get_logged_user
from its_ui_redesign.api.dashboard import get_dashboard_summary

class TestPortalAPI(FrappeTestCase):
    def test_unauthenticated_dashboard_fails(self):
        frappe.set_user("Guest")
        self.assertRaises(frappe.AuthenticationError, get_dashboard_summary)

    def test_authenticated_user_access(self):
        frappe.set_user("Administrator")
        data = get_dashboard_summary()
        self.assertIn("active_projects", data)
        self.assertIn("total_sales", data)

    def test_get_logged_user(self):
        frappe.set_user("Administrator")
        user_info = get_logged_user()
        self.assertEqual(user_info["user"], "Administrator")
        self.assertIn("csrf_token", user_info)
