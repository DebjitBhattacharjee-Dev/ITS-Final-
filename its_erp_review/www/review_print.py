"""
ITS ERP Review Universal Print Page
Renders the ITS branded print layout directly in Python,
providing full browser preview with print controls toolbar and A4 formatting.

URL: /review-print?doctype=<DocType>&name=<DocumentName>
"""
import frappe
from frappe import _

no_cache = 1
base_template_path = "its_erp_review/www/review_print.html"


def get_context(context):
	doctype = frappe.form_dict.get("doctype")
	name = frappe.form_dict.get("name")

	if not doctype or not name:
		frappe.throw(_("DocType and Document Name are required"))

	# Enforce read permission using logged-in user's session
	frappe.has_permission(doctype, "read", name, throw=True)

	doc = frappe.get_doc(doctype, name)

	from its_erp_review.utils.print_helpers import (
		its_print_company,
		get_its_logo_data_uri,
		get_its_doctype_title,
		get_its_doc_items,
		get_its_doc_totals,
		get_its_field_groups,
		get_its_child_tables,
	)

	company = its_print_company(doc)
	logo_uri = get_its_logo_data_uri()
	doc_title = get_its_doctype_title(doc.doctype)
	items = get_its_doc_items(doc)
	totals = get_its_doc_totals(doc)
	field_groups = get_its_field_groups(doc)
	child_tables = get_its_child_tables(doc)

	context.update({
		"doc": doc,
		"company": company,
		"logo_uri": logo_uri,
		"doc_title": doc_title,
		"items": items,
		"totals": totals,
		"field_groups": field_groups,
		"child_tables": child_tables,
		"show_controls": True,
		"no_sidebar": 1,
		"no_breadcrumbs": 1,
	})
