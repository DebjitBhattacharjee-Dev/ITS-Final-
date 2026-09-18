import frappe
from frappe.model.document import Document

class ITSReviewSkid(Document):
	def autoname(self):
		if not self.name or self.name.startswith("new-"):
			self.name = self.get("id") or self.get("skid_number") or frappe.generate_hash(length=10)


