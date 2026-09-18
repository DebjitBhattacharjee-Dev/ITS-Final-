import frappe

def get_context(context):
	user = frappe.session.user
	context.user = user if user != "Guest" else "Guest Reviewer"
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "ITS • Operations workspace"
	return context
