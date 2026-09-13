import frappe
from frappe.tests.utils import FrappeTestCase
from its_ui_redesign.services.business_flow import get_allowed_next_steps, build_next_step_payload
from its_ui_redesign.api.common import get_contextual_create_options, get_create_target_payload

class TestBusinessFlowRegistry(FrappeTestCase):

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        # Fetch existing test Project or create one
        proj = frappe.get_all("Project", limit=1)
        self.project_name = proj[0]["name"] if proj else None
        if not self.project_name:
            p = frappe.get_doc({
                "doctype": "Project",
                "project_name": "UAT Flow Test Project",
                "company": "BetaEdge (Demo)"
            }).insert(ignore_permissions=True)
            self.project_name = p.name

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    # TEST 1: Registered next steps for Quotation
    def test_01_quotation_next_steps(self):
        steps = get_allowed_next_steps("Quotation")
        self.assertIn("Sales Order", steps)
        self.assertIn("Finance Commitment", steps)
        self.assertIn("Project", steps)

    # TEST 2: Quotation -> Sales Order payload mapping
    def test_02_quotation_to_sales_order_payload(self):
        qtn = frappe.get_doc({
            "doctype": "Quotation",
            "party_name": "UAT-ITS Customer",
            "quotation_to": "Customer",
            "company": "BetaEdge (Demo)",
            "currency": "AED",
            "status": "Open",
            "project": self.project_name,
            "items": [{
                "item_code": "UAT-ITS-PSS-SKID-001",
                "qty": 2,
                "rate": 15000,
                "uom": "Nos",
                "description": "Test MV Power Skid"
            }]
        }).insert(ignore_permissions=True)

        payload = build_next_step_payload("Quotation", qtn.name, "Sales Order")
        self.assertEqual(payload.get("customer"), "UAT-ITS Customer")
        self.assertEqual(payload.get("company"), "BetaEdge (Demo)")
        self.assertEqual(payload.get("currency"), "AED")
        self.assertEqual(len(payload.get("items", [])), 1)
        self.assertEqual(payload["items"][0]["item_code"], "UAT-ITS-PSS-SKID-001")
        self.assertEqual(payload["items"][0]["prevdoc_docname"], qtn.name)

    # TEST 3: Finance Commitment Hard Stop (Must be Approved before creating Purchase Order)
    def test_03_finance_commitment_hard_stop(self):
        fc = frappe.get_doc({
            "doctype": "Finance Commitment",
            "project": self.project_name,
            "supplier": "UAT-ITS Supplier",
            "customer_po": "PO-TEST-001",
            "expected_payable": 30000,
            "approval_status": "Draft"
        }).insert(ignore_permissions=True)

        # Attempting to build PO payload from Draft FC should fail hard stop
        self.assertRaises(frappe.ValidationError, build_next_step_payload, "Finance Commitment", fc.name, "Purchase Order")

        # Now update FC to Approved
        fc.approval_status = "Approved"
        fc.save(ignore_permissions=True)

        payload = build_next_step_payload("Finance Commitment", fc.name, "Purchase Order")
        self.assertEqual(payload.get("supplier"), "UAT-ITS Supplier")
        self.assertEqual(payload.get("currency"), "AED")

    # TEST 4: FAT Hard Stop (Must be Passed before IFAT)
    def test_04_fat_to_ifat_hard_stop(self):
        fat = frappe.get_doc({
            "doctype": "Factory Acceptance Test",
            "title": "Test FAT Pending",
            "status": "Draft",
            "result": "Pending"
        }).insert(ignore_permissions=True)

        # Pending FAT cannot create IFAT
        self.assertRaises(frappe.ValidationError, build_next_step_payload, "Factory Acceptance Test", fat.name, "Integrated Factory Acceptance Test")

        # Set to Passed
        fat.result = "Passed"
        fat.status = "Approved"
        fat.save(ignore_permissions=True)

        payload = build_next_step_payload("Factory Acceptance Test", fat.name, "Integrated Factory Acceptance Test")
        self.assertEqual(payload.get("fat_reference"), fat.name)

    # TEST 5: IDOR & Invalid Target Protection
    def test_05_idor_invalid_target_rejected(self):
        qtn = frappe.get_doc({
            "doctype": "Quotation",
            "party_name": "UAT-ITS Customer",
            "quotation_to": "Customer",
            "company": "BetaEdge (Demo)",
            "currency": "AED",
            "status": "Open",
            "items": [{
                "item_code": "UAT-ITS-PSS-SKID-001",
                "qty": 1,
                "rate": 1000,
                "uom": "Nos",
                "description": "Test Item"
            }]
        }).insert(ignore_permissions=True)

        # Attempting to force target to User or System Settings must fail
        self.assertRaises(frappe.ValidationError, build_next_step_payload, "Quotation", qtn.name, "User")
        self.assertRaises(frappe.ValidationError, build_next_step_payload, "Quotation", qtn.name, "System Settings")

    # TEST 6: Unauthenticated user API access denied
    def test_06_unauthenticated_api_access(self):
        frappe.set_user("Guest")
        res = get_create_target_payload("Quotation", "SAL-QTN-2026-00015", "Sales Order")
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("error", {}).get("code"), "PERMISSION_DENIED")
