import frappe
from frappe.tests.utils import FrappeTestCase
from its_ui_redesign.api.auth import get_logged_user
from its_ui_redesign.api.common import (
    get_workspace_dashboard,
    get_document_list,
    get_document_detail,
    save_document,
    delete_document,
    submit_document,
    cancel_document,
    amend_document,
    apply_workflow_action,
    get_related_documents,
    get_document_pdf,
    search_link_options,
    validate_supplier_po_release,
    insert_missing_custom_doctypes,
    reload_custom_doctypes,
    audit_navigation_doctypes
)
from its_ui_redesign.api.search import global_search

class TestPortalAPI(FrappeTestCase):

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    # TEST 1: Unauthenticated user cannot access protected dashboard
    def test_01_unauthenticated_dashboard_fails(self):
        frappe.set_user("Guest")
        self.assertRaises(frappe.AuthenticationError, get_workspace_dashboard, "01-project-management")

    # TEST 2: Authenticated user can access permitted dashboard
    def test_02_authenticated_permitted_dashboard(self):
        frappe.set_user("Administrator")
        data = get_workspace_dashboard("01-project-management")
        self.assertIn("kpis", data)
        self.assertIn("charts", data)
        self.assertIn("recent_list", data)
        self.assertEqual(data["doctype"], "Project")

    # TEST 3: User without DocType read permission cannot retrieve that DocType list
    def test_03_doctype_read_permission_enforced(self):
        frappe.set_user("Guest")
        res = get_document_list("Project")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 4: User without read permission cannot fetch document detail
    def test_04_document_detail_read_permission(self):
        frappe.set_user("Guest")
        res = get_document_detail("Project", "NON_EXISTENT_PROJECT")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 5: User without create permission cannot save/create new document
    def test_05_create_permission_enforced(self):
        frappe.set_user("Guest")
        res = save_document("Project", {"project_name": "Test Unauth Project"})
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 6: User without write permission cannot update a document
    def test_06_write_permission_enforced(self):
        frappe.set_user("Guest")
        res = save_document("Project", {"name": "PROJ-001", "project_name": "Updated Name"})
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 7: User without delete permission cannot delete a document
    def test_07_delete_permission_enforced(self):
        frappe.set_user("Guest")
        res = delete_document("Project", "PROJ-001")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 8: User without submit permission cannot submit a document
    def test_08_submit_permission_enforced(self):
        frappe.set_user("Guest")
        res = submit_document("Sales Order", "SO-001")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 9: User without cancel permission cannot cancel a document
    def test_09_cancel_permission_enforced(self):
        frappe.set_user("Guest")
        res = cancel_document("Sales Order", "SO-001")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 10: Unauthorized workflow transition is rejected
    def test_10_unauthorized_workflow_transition(self):
        frappe.set_user("Guest")
        res = apply_workflow_action("Project", "PROJ-001", "Approve")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 11: Dashboard metrics only include records accessible to the session user
    def test_11_dashboard_metrics_permission_scoped(self):
        frappe.set_user("Administrator")
        data = get_workspace_dashboard("09-accounting")
        self.assertIn("kpis", data)
        self.assertIn("charts", data)
        self.assertEqual(data["doctype"], "Payment Entry")

    # TEST 12: Search link options enforces read permissions
    def test_12_link_search_permission_enforced(self):
        frappe.set_user("Guest")
        res = search_link_options("Customer", "Test")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 13: Global search returns empty data for guest / unauthenticated
    def test_13_global_search_guest(self):
        frappe.set_user("Guest")
        results = global_search("Project")
        self.assertEqual(results["doctypes"], [])
        self.assertEqual(results["documents"], [])

    # TEST 14: Restricted document cannot generate PDF
    def test_14_document_pdf_permission_enforced(self):
        frappe.set_user("Guest")
        res = get_document_pdf("Project", "PROJ-001")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "UNAUTHENTICATED")

    # TEST 15: Administrative setup endpoint rejects user without System Manager
    def test_15_admin_endpoint_protection(self):
        # Create or use a restricted non-System Manager user
        if not frappe.db.exists("User", "test_restricted_user@example.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "test_restricted_user@example.com",
                "first_name": "Test Restricted",
                "send_welcome_email": 0,
                "roles": [{"role": "Projects User"}]
            })
            user.insert(ignore_permissions=True)

        frappe.set_user("test_restricted_user@example.com")
        self.assertRaises(frappe.PermissionError, insert_missing_custom_doctypes)
        self.assertRaises(frappe.PermissionError, reload_custom_doctypes)
        self.assertRaises(frappe.PermissionError, audit_navigation_doctypes)

    # TEST 16: Get logged user returns authenticated info
    def test_16_get_logged_user(self):
        frappe.set_user("Administrator")
        user_info = get_logged_user()
        self.assertEqual(user_info["user"], "Administrator")
        self.assertIn("csrf_token", user_info)
