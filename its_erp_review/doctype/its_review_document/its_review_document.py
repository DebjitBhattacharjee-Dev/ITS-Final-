import frappe
from frappe.model.document import Document

class ITSReviewDocument(Document):
	def autoname(self):
		if not self.name or self.name.startswith("new-"):
			self.name = self.get("id") or self.get("reference") or frappe.generate_hash(length=10)


