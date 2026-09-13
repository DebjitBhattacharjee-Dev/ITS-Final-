"""
ITS Universal Print Page
Renders the ITS branded print layout by calling helper functions directly in Python,
bypassing the Frappe Jinja sandbox entirely.

URL: /its-print?doctype=<DocType>&name=<DocumentName>
"""
import frappe
from frappe import _

no_cache = 1
base_template_path = "its_ui_redesign/www/its_print.html"


def get_context(context):
    doctype = frappe.form_dict.get("doctype")
    name = frappe.form_dict.get("name")

    if not doctype or not name:
        frappe.throw(_("DocType and Document Name are required"))

    # Enforce read permission — uses the logged-in user's session
    frappe.has_permission(doctype, "read", name, throw=True)

    doc = frappe.get_doc(doctype, name)

    # Call all helpers directly in Python — no Jinja sandbox involved
    from its_ui_redesign.utils.print_helpers import (
        its_print_company,
        get_its_logo_data_uri,
        get_its_doctype_title,
        get_its_doc_items,
        get_its_doc_totals,
        get_its_field_groups,
        get_its_child_tables,
    )

    company     = its_print_company(doc)
    logo_uri    = get_its_logo_data_uri()
    doc_title   = get_its_doctype_title(doc.doctype)
    items       = get_its_doc_items(doc)
    totals      = get_its_doc_totals(doc)
    field_groups = get_its_field_groups(doc)
    child_tables = get_its_child_tables(doc)

    context.update({
        "doc":          doc,
        "company":      company,
        "logo_uri":     logo_uri,
        "doc_title":    doc_title,
        "items":        items,
        "totals":       totals,
        "field_groups": field_groups,
        "child_tables": child_tables,
        "no_sidebar":   1,
        "no_breadcrumbs": 1,
    })
