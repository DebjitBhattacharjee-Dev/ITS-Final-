import frappe
from frappe.utils import today, getdate

@frappe.whitelist()
def get_dashboard_metrics(project_id=None, department=None, date_filter=None):
	"""
	Calculates dashboard KPI metrics and executive review indicators directly from MariaDB.
	Enforces user permissions and record-level filters.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Authentication required", frappe.AuthenticationError)

	filters = {}
	if project_id:
		filters["project_id"] = project_id

	# Fetch projects accessible to user
	projects = frappe.get_list(
		"ITS Review Project",
		filters={"project_type": "POWERSKID"} if not project_id else {"name": project_id, "project_type": "POWERSKID"},
		fields=["name", "project_name", "customer"]
	)
	pids = [p["name"] for p in projects]

	if not pids:
		return {
			"projects": 0, "skids": 0, "wells": 0, "integration": 0,
			"fatPending": 0, "fatCompleted": 0, "ifatPending": 0, "ifatCompleted": 0,
			"delivered": 0, "commissionPending": 0, "commissionInProgress": 0,
			"commissioned": 0, "punchOpen": 0, "punchClosed": 0, "punchOverdue": 0
		}

	skids = frappe.get_list(
		"ITS Review Skid",
		filters={"project_id": ["in", pids]},
		fields=["name", "project_id", "well_number", "status"]
	)

	punches = frappe.get_list(
		"ITS Review Punch",
		filters={"project_id": ["in", pids]},
		fields=["name", "status", "target_date"]
	)

	events = frappe.get_list(
		"ITS Review Event",
		filters={"project_id": ["in", pids]},
		fields=["skid_id", "test", "status"]
	)

	commissioning = frappe.get_list(
		"ITS Review Commissioning",
		filters={"project_id": ["in", pids]},
		fields=["skid_id", "status"]
	)

	today_str = date_filter or today()
	wells_set = set(f"{s['project_id']}:{s['well_number']}" for s in skids)

	def get_event_status(skid_id, test_name):
		skid_events = [e for e in events if e["skid_id"] == skid_id and e["test"] == test_name]
		return skid_events[-1]["status"] if skid_events else None

	def get_comm_status(skid_id):
		skid_comm = [c for c in commissioning if c["skid_id"] == skid_id]
		return skid_comm[-1]["status"] if skid_comm else None

	fat_completed = sum(1 for s in skids if get_event_status(s["name"], "FAT") == "Completed")
	ifat_completed = sum(1 for s in skids if get_event_status(s["name"], "IFAT") == "Completed")

	comm_in_progress = sum(1 for s in skids if get_comm_status(s["name"]) == "Commissioning In Progress")
	commissioned_count = sum(1 for s in skids if get_comm_status(s["name"]) in ["Commissioned", "Handover Pending", "Handed Over"])
	comm_pending = len(skids) - (comm_in_progress + commissioned_count)

	punch_open = sum(1 for p in punches if p["status"] != "Closed")
	punch_closed = sum(1 for p in punches if p["status"] == "Closed")
	punch_overdue = sum(1 for p in punches if p["status"] != "Closed" and p.get("target_date") and str(p["target_date"]) < today_str)

	return {
		"projects": len(projects),
		"skids": len(skids),
		"wells": len(wells_set),
		"integration": sum(1 for s in skids if s["status"] == "In Progress"),
		"fatPending": len(skids) - fat_completed,
		"fatCompleted": fat_completed,
		"ifatPending": len(skids) - ifat_completed,
		"ifatCompleted": ifat_completed,
		"delivered": sum(1 for s in skids if s["status"] == "Completed"),
		"commissionPending": comm_pending,
		"commissionInProgress": comm_in_progress,
		"commissioned": commissioned_count,
		"punchOpen": punch_open,
		"punchClosed": punch_closed,
		"punchOverdue": punch_overdue
	}
