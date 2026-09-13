import frappe
import os
import base64
from frappe import _

LOGO_PATH = os.path.join(
    frappe.get_app_path("its_ui_redesign"),
    "public",
    "images",
    "its_logo.png"
)

TITLE_MAP = {
    "Sales Order": "Sales Order / Order Acknowledgement",
    "Quotation": "Quotation / Commercial Proposal",
    "Sales Invoice": "Tax Invoice",
    "Purchase Order": "Purchase Order",
    "Delivery Note": "Delivery Note",
    "Purchase Receipt": "Purchase Receipt",
    "Request for Quotation": "Request for Quotation",
    "Project Contract": "Project Contract / Agreement",
    "BOQ": "Bill of Quantities (BOQ)",
    "FAT": "Factory Acceptance Test (FAT)",
    "Factory Acceptance Test": "Factory Acceptance Test (FAT)",
    "IFAT": "Integrated Factory Acceptance Test (IFAT)",
    "Integrated Factory Acceptance Test": "Integrated Factory Acceptance Test (IFAT)",
    "RFI": "Request for Information (RFI)",
    "Project Variation": "Project Variation Order",
    "Snag List": "Snag List & Inspection Report",
    "Project Handover": "Project Handover Certificate",
    "Project Warranty": "Project Warranty Certificate",
    "Progress Claim": "Progress Claim & Billing",
    "Payment Certificate": "Payment Certificate",
    "Invoice Dossier": "Invoice Dossier"
}

def get_its_logo_data_uri():
    """
    Returns base64 Data URI for canonical ITS logo to guarantee wkhtmltopdf PDF rendering without HTTP network requests.
    """
    candidate_paths = [
        os.path.join(frappe.get_site_path("public", "files"), "ITS Logo png.png"),
        LOGO_PATH,
        os.path.join(frappe.get_site_path("public", "images"), "its_logo.png"),
        os.path.join(frappe.get_site_path("public"), "its_logo.png"),
    ]
    for path in candidate_paths:
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    return f"data:image/png;base64,{encoded}"
        except Exception:
            pass
    return "/files/ITS Logo png.png"


def its_print_company(doc):
    """
    Returns company details for print header.
    """
    company_name = getattr(doc, "company", None) or "Independent Technical Services LLC"
    tax_id = "100034567800003"
    
    if getattr(doc, "company", None) and frappe.db.exists("Company", doc.company):
        c_doc = frappe.get_doc("Company", doc.company)
        company_name = c_doc.company_name or c_doc.name
        if getattr(c_doc, "tax_id", None):
            tax_id = c_doc.tax_id

    return {
        "company_name": company_name,
        "name": company_name,
        "tax_id": tax_id,
        "trn": tax_id,
        "location": "Abu Dhabi, United Arab Emirates",
        "po_box": "PO Box 45174, Abu Dhabi, UAE",
        "phone": "+971 (2) 6210650",
        "fax": "+971 (2) 6210640",
        "email": "indptech@emirates.net.ae"
    }

def its_print_sections(doc):
    """
    Compatibility wrapper returning section structures for universal master Jinja.
    """
    fg = get_its_field_groups(doc)
    all_fields = fg.get("col1", []) + fg.get("col2", [])
    return [
        {
            "title": "Document Information & Metadata",
            "label": "Document Information & Metadata",
            "fields": all_fields,
            "col1": fg.get("col1", []),
            "col2": fg.get("col2", [])
        }
    ]

def its_print_tables(doc):
    """
    Compatibility wrapper returning table structures for universal master Jinja.
    """
    return get_its_child_tables(doc)

def get_its_doctype_title(doctype):
    """
    Maps native and custom DocTypes to official ITS corporate title.
    """
    return TITLE_MAP.get(doctype, str(doctype).upper())

def get_its_doc_items(doc):
    """
    Normalizes item table rows across transaction DocTypes.
    """
    raw_rows = []
    for field in ["items", "po_items", "so_items", "invoice_items", "entries", "details"]:
        if hasattr(doc, field) and isinstance(getattr(doc, field), list) and len(getattr(doc, field)) > 0:
            raw_rows = getattr(doc, field)
            break

    items = []
    for idx, r in enumerate(raw_rows, 1):
        item_code = getattr(r, "item_code", None) or getattr(r, "item", None) or getattr(r, "item_name", None) or f"ITEM-{idx:03d}"
        item_name = getattr(r, "item_name", None) or getattr(r, "description", None) or item_code
        description = getattr(r, "description", None) or item_name
        part_no = getattr(r, "part_no", None) or getattr(r, "supplier_part_no", None) or getattr(r, "manufacturer_part_no", None) or "—"
        
        qty = float(getattr(r, "qty", 0) or getattr(r, "quantity", 0) or 1)
        uom = getattr(r, "uom", None) or getattr(r, "stock_uom", None) or getattr(r, "unit", None) or "Pcs"
        rate = float(getattr(r, "rate", 0) or getattr(r, "price", 0) or getattr(r, "unit_price", 0) or 0)
        amount = float(getattr(r, "amount", 0) or (qty * rate))
        
        tax_rate = float(getattr(r, "tax_rate", 0) or getattr(r, "vat_percent", 0) or 0)
        
        items.append({
            "idx": idx,
            "item_code": item_code,
            "item_name": item_name,
            "part_no": part_no,
            "description": description,
            "qty": qty,
            "uom": uom,
            "rate": rate,
            "amount": amount,
            "tax_rate": tax_rate
        })

    return items

def get_its_doc_totals(doc):
    """
    Computes financial totals and amount in words.
    """
    net_total = float(getattr(doc, "net_total", 0) or getattr(doc, "total", 0) or 0)
    vat_amount = float(getattr(doc, "total_taxes_and_charges", 0) or getattr(doc, "vat_amount", 0) or getattr(doc, "tax_amount", 0) or 0)
    grand_total = float(getattr(doc, "grand_total", 0) or (net_total + vat_amount))
    currency = getattr(doc, "currency", None) or "AED"

    in_words = getattr(doc, "in_words", None)
    if not in_words and grand_total > 0:
        try:
            from frappe.utils.data import money_in_words
            in_words = money_in_words(grand_total, currency)
        except Exception:
            in_words = ""

    return {
        "net_total": net_total,
        "vat_amount": vat_amount,
        "grand_total": grand_total,
        "currency": currency,
        "in_words": in_words or ""
    }

def get_its_field_groups(doc):
    """
    Discovers non-empty scalar fields for general DocType layout.
    """
    meta = frappe.get_meta(doc.doctype)
    excluded_fields = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "user_image", "items", "po_items", "so_items", "invoice_items", "entries"}
    
    fields = []
    for f in meta.fields:
        if f.fieldtype not in ["Section Break", "Column Break", "Tab Break", "Table", "HTML", "Button", "Heading", "Fold"]:
            val = getattr(doc, f.fieldname, None)
            if val is not None and str(val).strip() != "" and f.fieldname not in excluded_fields:
                fields.append({
                    "label": f.label or f.fieldname.replace("_", " ").title(),
                    "value": str(val),
                    "fieldtype": f.fieldtype
                })

    # Group into two columns
    mid = (len(fields) + 1) // 2
    return {
        "col1": fields[:mid],
        "col2": fields[mid:]
    }

def get_its_child_tables(doc):
    """
    Discovers child tables for general non-item DocTypes.
    """
    meta = frappe.get_meta(doc.doctype)
    tables = []
    
    for f in meta.fields:
        if f.fieldtype == "Table":
            child_rows = getattr(doc, f.fieldname, None)
            if child_rows and isinstance(child_rows, list) and len(child_rows) > 0:
                child_meta = frappe.get_meta(f.options)
                col_fields = [cf for cf in child_meta.fields if cf.in_list_view and cf.fieldtype not in ["Section Break", "Column Break", "Table", "HTML"]]
                if not col_fields:
                    col_fields = [cf for cf in child_meta.fields if cf.fieldtype not in ["Section Break", "Column Break", "Table", "HTML", "Fold"]][:5]
                
                rows_data = []
                for idx, r in enumerate(child_rows, 1):
                    row_dict = {"idx": idx}
                    for cf in col_fields:
                        row_dict[cf.fieldname] = getattr(r, cf.fieldname, "")
                    rows_data.append(row_dict)

                tables.append({
                    "title": f.label or f.fieldname.replace("_", " ").title(),
                    "columns": [{"fieldname": cf.fieldname, "label": cf.label or cf.fieldname.replace("_", " ").title()} for cf in col_fields],
                    "rows": rows_data
                })

    return tables
