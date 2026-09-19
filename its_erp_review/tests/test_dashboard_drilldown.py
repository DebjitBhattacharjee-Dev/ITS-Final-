import unittest
import frappe
from its_erp_review.api.dashboard import get_dashboard_data, get_drilldown_records
from its_erp_review.api.documents import get_document_detail

class TestDashboardDrilldown(unittest.TestCase):
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

	def test_get_dashboard_data_guest_denied(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_dashboard_data()

	def test_get_drilldown_records_guest_denied(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_drilldown_records(key="overdue")

	def test_get_dashboard_data_structure(self):
		frappe.set_user("Administrator")
		data = get_dashboard_data(days=30)
		self.assertIn("today", data)
		self.assertIn("window_days", data)
		self.assertIn("scope", data)
		self.assertIn("department", data)
		self.assertIn("projects", data)
		self.assertIn("cards", data)
		self.assertIn("priority_actions", data)
		self.assertIn("review_status", data)
		self.assertIn("workload", data)
		self.assertIn("commercial_counts", data)
		self.assertIn("finance_counts", data)
		self.assertIn("operations_counts", data)
		self.assertIn("expiry_watch", data)
		self.assertIn("pss", data)

		# Check 4 KPI cards
		for kpi in ["approval", "overdue", "due", "returned"]:
			self.assertIn(kpi, data["cards"])
			self.assertIn("count", data["cards"][kpi])
			self.assertIsInstance(data["cards"][kpi]["count"], int)

		# Check review status
		self.assertIn("total_records", data["review_status"])
		self.assertIn("counts", data["review_status"])
		for st in ["Draft", "Submitted", "Returned", "Approved"]:
			self.assertIn(st, data["review_status"]["counts"])

	def test_same_query_principle_kpi_counts(self):
		"""
		CRITICAL: The KPI count on the dashboard must match the count of records
		returned by the drilldown endpoint for the same business definition.
		"""
		frappe.set_user("Administrator")
		dash = get_dashboard_data(days=30)

		for key in ["approval", "overdue", "due", "returned"]:
			kpi_count = dash["cards"][key]["count"]
			drilldown_res = get_drilldown_records(key=key, days=30, limit=1000)
			records = drilldown_res["records"]
			self.assertEqual(
				kpi_count, len(records),
				f"Mismatch for KPI '{key}': dashboard count={kpi_count} vs drilldown count={len(records)}"
			)

	def test_doctype_allowlist_enforcement(self):
		"""
		Security: Unallowlisted DocTypes (like 'User', 'DocType') must be rejected.
		"""
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.PermissionError):
			get_drilldown_records(doctype="User")

	def test_status_drilldown(self):
		frappe.set_user("Administrator")
		dash = get_dashboard_data()
		draft_count = dash["review_status"]["counts"]["Draft"]
		drilldown_res = get_drilldown_records(status="Draft", limit=1000)
		self.assertEqual(draft_count, len(drilldown_res["records"]))

	def test_record_structure_and_detail_linkage(self):
		"""
		Every record in the drilldown list must contain valid document identity
		and be retrievable via get_document_detail.
		"""
		frappe.set_user("Administrator")
		res = get_drilldown_records(key="approval", limit=5)
		for r in res["records"]:
			self.assertTrue(r["id"])
			self.assertTrue(r["name"])
			self.assertTrue(r["doctype"])
			self.assertTrue(r["status"])

			# Test opening exact record
			detail = get_document_detail(doctype=r["doctype"], name=r["name"])
			self.assertEqual(detail["name"], r["name"])
			self.assertEqual(detail["doctype"], r["doctype"])
			self.assertIn("fields", detail)
			self.assertIn("workflow_state", detail)
			self.assertIn("permissions", detail)
