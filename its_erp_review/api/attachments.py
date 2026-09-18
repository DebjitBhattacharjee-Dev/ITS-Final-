import frappe
import base64
from frappe import _

@frappe.whitelist()
def get_attachments(project_id=None, record_id=None):
	"""
	Returns all attached files using native Frappe File records.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	filters = {"attached_to_doctype": ["in", ["ITS Review Project", "ITS Review Document", "ITS Review Skid", "ITS Review Register"]]}
	if record_id:
		filters["attached_to_name"] = record_id

	files = frappe.get_list(
		"File",
		filters=filters,
		fields=["name as id", "attached_to_name as recordId", "file_name as name", "file_size as size", "creation as created", "file_url"],
		order_by="creation desc"
	)

	token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return {
		"files": files,
		"token": token
	}

@frappe.whitelist()
def upload_attachment(projectId=None, recordId=None, recordTitle=None, category=None, name=None, base64_data=None):
	"""
	Saves a file attachment natively in Frappe's file manager.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not name or not base64_data or not projectId:
		frappe.throw(_("Project ID, file name, and file content are required."))

	content = base64.b64decode(base64_data)
	
	# Create native Frappe File document
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": name,
		"attached_to_doctype": "ITS Review Project",
		"attached_to_name": projectId,
		"content": content,
		"is_private": 1
	})
	file_doc.insert()

	return {
		"file": {
			"id": file_doc.name,
			"projectId": projectId,
			"recordId": recordId or projectId,
			"recordTitle": recordTitle or name,
			"name": name,
			"category": category or "General",
			"size": file_doc.file_size,
			"created": str(file_doc.creation),
			"url": file_doc.file_url
		}
	}

@frappe.whitelist()
def download_file(file_id=None):
	"""
	Downloads an attached file from Frappe File storage with permission check.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Authentication required"), frappe.AuthenticationError)

	if not file_id:
		frappe.throw(_("File ID is required."))

	if not frappe.db.exists("File", file_id):
		frappe.throw(_("File not found."), frappe.DoesNotExistError)

	file_doc = frappe.get_doc("File", file_id)
	file_doc.check_permission("read")

	content = file_doc.get_content()
	frappe.response['filename'] = file_doc.file_name
	frappe.response['filecontent'] = content
	frappe.response['type'] = 'download'

