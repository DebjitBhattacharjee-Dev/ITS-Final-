import frappe
from frappe.tests.utils import FrappeTestCase
from its_ui_redesign.api.admin import (
    get_users,
    get_user_detail,
    save_user,
    set_user_enabled,
    add_user_permission,
    delete_user_permission,
    get_roles,
    save_role,
    get_role_permission_matrix,
    update_role_permission
)

class TestAdminAPI(FrappeTestCase):

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def test_01_user_creation_and_role_assignment(self):
        frappe.set_user("Administrator")
        test_email = "uat-admin-user@example.com"
        
        # Clean up if exists
        if frappe.db.exists("User", test_email):
            frappe.delete_doc("User", test_email, force=True, ignore_permissions=True)

        res = save_user(
            user_data={
                "email": test_email,
                "first_name": "UAT Admin",
                "last_name": "Tester",
                "enabled": 1
            },
            roles=["Projects User", "Purchase User"]
        )

        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("data", {}).get("email"), test_email)

        # Verify in native Frappe DB
        user_doc = frappe.get_doc("User", test_email)
        assigned_roles = [r.role for r in user_doc.roles]
        self.assertIn("Projects User", assigned_roles)
        self.assertIn("Purchase User", assigned_roles)

    def test_02_user_permission_management(self):
        frappe.set_user("Administrator")
        test_email = "uat-admin-user@example.com"
        if not frappe.db.exists("User", test_email):
            save_user({"email": test_email, "first_name": "UAT Admin"})

        # Get or create a project for testing
        test_project_name = "PROJ-TEST-UAT"
        existing_proj = frappe.db.get_value("Project", {"project_name": test_project_name}, "name")
        if not existing_proj:
            proj = frappe.get_doc({"doctype": "Project", "project_name": test_project_name, "status": "Open"})
            proj.insert(ignore_permissions=True)
            test_project_id = proj.name
        else:
            test_project_id = existing_proj

        # Add User Permission via API
        res = add_user_permission(
            user_id=test_email,
            allow_doctype="Project",
            for_value=test_project_id,
            is_default=1
        )

        self.assertTrue(res.get("success"))
        up_name = res.get("data", {}).get("name")
        self.assertTrue(bool(up_name))

        # Verify in native Frappe DB
        up_doc = frappe.get_doc("User Permission", up_name)
        self.assertEqual(up_doc.user, test_email)
        self.assertEqual(up_doc.allow, "Project")
        self.assertEqual(up_doc.for_value, test_project_id)

        # Delete User Permission via API
        del_res = delete_user_permission(up_name)
        self.assertTrue(del_res.get("success"))
        self.assertFalse(frappe.db.exists("User Permission", up_name))

    def test_03_role_and_permission_matrix(self):
        frappe.set_user("Administrator")
        test_role = "UAT Test Role"

        res = save_role(role_name=test_role, desk_access=1)
        self.assertTrue(res.get("success"))
        self.assertTrue(frappe.db.exists("Role", test_role))

        # Update permission property
        perm_res = update_role_permission(
            doctype="Project",
            role=test_role,
            permlevel=0,
            ptype="read",
            value=1
        )
        self.assertTrue(perm_res.get("success"))

        # Fetch matrix
        matrix_res = get_role_permission_matrix(doctype="Project", role=test_role)
        self.assertTrue(matrix_res.get("success"))

    def test_04_unauthorized_admin_access_rejected(self):
        # Create non-System Manager restricted user
        restricted_email = "uat-restricted-admin@example.com"
        if not frappe.db.exists("User", restricted_email):
            save_user({"email": restricted_email, "first_name": "Restricted User"}, roles=["Projects User"])

        frappe.set_user(restricted_email)

        self.assertRaises(frappe.PermissionError, get_users)
        self.assertRaises(frappe.PermissionError, save_user, {"email": "illegal@example.com"})
        self.assertRaises(frappe.PermissionError, get_roles)
        self.assertRaises(frappe.PermissionError, save_role, "Illegal Role")
