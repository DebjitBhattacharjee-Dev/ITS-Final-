import frappe
from frappe import _

FLOW_REGISTRY = {
    "Lead": [
        {
            "target_doctype": "Opportunity",
            "label": "Opportunity",
            "stage": "G1",
            "field_map": {
                "party_name": "lead_name",
                "opportunity_from": lambda doc: "Lead",
                "company": "company",
                "title": lambda doc: f"Opportunity from Lead {doc.name}",
            }
        }
    ],
    "Opportunity": [
        {
            "target_doctype": "Quotation",
            "label": "Quotation",
            "stage": "G3",
            "field_map": {
                "quotation_to": lambda doc: "Customer",
                "party_name": "party_name",
                "customer_name": "customer_name",
                "opportunity": "name",
                "company": "company",
                "currency": "currency",
                "order_type": lambda doc: "Sales",
                "transaction_date": lambda doc: frappe.utils.today(),
                "valid_till": lambda doc: frappe.utils.add_days(frappe.utils.today(), 30),
            },
            "child_map": {
                "items": {
                    "source_field": "items",
                    "fields": ["item_code", "item_name", "qty", "rate", "uom", "description"]
                }
            }
        },
        {
            "target_doctype": "Project",
            "label": "Project",
            "stage": "G3.5",
            "field_map": {
                "project_name": lambda doc: doc.title or f"Project for {doc.party_name or doc.name}",
                "customer": "party_name",
                "company": "company",
            }
        }
    ],
    "Supplier Quotation": [
        {
            "target_doctype": "Quotation",
            "label": "Quotation",
            "stage": "G3",
            "field_map": {
                "supplier": "supplier",
                "company": "company",
                "currency": "currency",
            },
            "child_map": {
                "items": {
                    "source_field": "items",
                    "fields": ["item_code", "item_name", "qty", "rate", "uom", "description"]
                }
            }
        }
    ],
    "Quotation": [
        {
            "target_doctype": "Project Contract",
            "label": "Project Contract",
            "stage": "G3.5",
            "field_map": {
                "title": lambda doc: f"Contract for {doc.name}",
                "customer": "party_name",
                "project": "project",
                "company": "company",
                "contract_value": "grand_total",
                "quotation": "name",
                "opportunity": "opportunity",
            }
        },
        {
            "target_doctype": "Sales Order",
            "label": "Sales Order",
            "stage": "G5.5",
            "prerequisites": [
                {
                    "check": lambda doc: doc.docstatus == 1 or getattr(doc, "status", "") in ["Submitted", "Open"],
                    "message": "Quotation must be Submitted before creating a Sales Order."
                },
                {
                    "check": lambda doc: bool(getattr(doc, "party_name", None) or getattr(doc, "customer", None)),
                    "message": "Quotation is missing a valid Customer."
                }
            ],
            "field_map": {
                "customer": lambda doc: getattr(doc, "party_name", None) or getattr(doc, "customer", None),
                "customer_name": "customer_name",
                "project": "project",
                "company": "company",
                "currency": "currency",
                "order_type": lambda doc: getattr(doc, "order_type", "Sales") or "Sales",
                "transaction_date": lambda doc: frappe.utils.today(),
                "delivery_date": lambda doc: frappe.utils.add_days(frappe.utils.today(), 30),
                "po_no": lambda doc: getattr(doc, "customer_po", None) or getattr(doc, "po_no", None),
                "custom_payment_type": lambda doc: getattr(doc, "custom_payment_type", None) or "Milestone",
            },
            "child_map": {
                "items": {
                    "source_field": "items",
                    "fields": ["item_code", "item_name", "qty", "rate", "amount", "uom", "description", "warehouse"],
                    "extra": lambda row, doc: {"prevdoc_docname": doc.name, "quotation_item": row.get("name")}
                }
            }
        },
        {
            "target_doctype": "Finance Commitment",
            "label": "Finance Commitment",
            "stage": "G6",
            "field_map": {
                "project": "project",
                "customer_po": lambda doc: getattr(doc, "customer_po", None) or getattr(doc, "po_no", None) or doc.name,
                "supplier": lambda doc: getattr(doc, "supplier", None),
                "expected_payable": "grand_total",
                "currency": "currency",
                "approval_status": lambda doc: "Draft"
            }
        },
        {
            "target_doctype": "Project",
            "label": "Project",
            "stage": "G3.5",
            "field_map": {
                "project_name": lambda doc: doc.title or f"Project {doc.name}",
                "customer": lambda doc: getattr(doc, "party_name", None) or getattr(doc, "customer", None),
                "company": "company",
                "estimated_costing": "grand_total"
            }
        }
    ],
    "Project Contract": [
        {
            "target_doctype": "Sales Order",
            "label": "Sales Order",
            "stage": "G5.5",
            "field_map": {
                "customer": "customer",
                "project": "project",
                "company": "company",
                "order_type": lambda doc: "Sales",
                "transaction_date": lambda doc: frappe.utils.today(),
                "delivery_date": lambda doc: frappe.utils.add_days(frappe.utils.today(), 30),
            }
        }
    ],
    "Sales Order": [
        {
            "target_doctype": "Finance Commitment",
            "label": "Finance Commitment",
            "stage": "G6",
            "field_map": {
                "project": "project",
                "customer_po": "po_no",
                "currency": "currency",
                "expected_payable": "grand_total",
                "supplier_po": "name",
                "approval_status": lambda doc: "Draft"
            }
        },
        {
            "target_doctype": "Factory Acceptance Test",
            "label": "Factory Acceptance Test",
            "stage": "G8",
            "field_map": {
                "title": lambda doc: f"FAT for {doc.name}",
                "project": "project",
                "sales_order": "name",
                "customer": "customer",
                "company": "company",
                "status": lambda doc: "Draft"
            }
        },
        {
            "target_doctype": "Delivery Note",
            "label": "Delivery Note",
            "stage": "G9.5",
            "prerequisites": [
                {
                    "check": lambda doc: doc.docstatus == 1,
                    "message": "Sales Order must be Submitted before creating a Delivery Note."
                }
            ],
            "field_map": {
                "customer": "customer",
                "project": "project",
                "company": "company",
                "currency": "currency",
                "posting_date": lambda doc: frappe.utils.today(),
            },
            "child_map": {
                "items": {
                    "source_field": "items",
                    "fields": ["item_code", "item_name", "qty", "rate", "amount", "uom", "description", "warehouse"],
                    "extra": lambda row, doc: {"against_sales_order": doc.name, "so_detail": row.get("name")}
                }
            }
        }
    ],
    "Finance Commitment": [
        {
            "target_doctype": "Purchase Order",
            "label": "Purchase Order",
            "stage": "G7",
            "prerequisites": [
                {
                    "check": lambda doc: getattr(doc, "approval_status", "") == "Approved" or doc.docstatus == 1,
                    "message": "Finance Commitment must be Approved before creating a Purchase Order."
                },
                {
                    "check": lambda doc: bool(getattr(doc, "supplier", None)),
                    "message": "Supplier is missing on Finance Commitment."
                }
            ],
            "field_map": {
                "title": lambda doc: f"PO from Commitment {doc.name}",
                "supplier": "supplier",
                "project": "project",
                "company": lambda doc: getattr(doc, "company", None) or frappe.db.get_value("Company", {}) or "ITS",
                "currency": "currency",
                "transaction_date": lambda doc: frappe.utils.today(),
                "schedule_date": lambda doc: frappe.utils.add_days(frappe.utils.today(), 15),
            }
        }
    ],
    "Purchase Order": [
        {
            "target_doctype": "Factory Acceptance Test",
            "label": "Factory Acceptance Test",
            "stage": "G8",
            "field_map": {
                "title": lambda doc: f"FAT for PO {doc.name}",
                "project": "project",
                "purchase_order": "name",
                "supplier": "supplier",
                "company": "company",
                "status": lambda doc: "Draft"
            }
        },
        {
            "target_doctype": "PSS Skid Tracker",
            "label": "PSS Skid Tracker",
            "stage": "G8",
            "field_map": {
                "project": "project",
                "supplier": "supplier",
                "supplier_po": "name",
                "pss_family": lambda doc: "MV Power Skid"
            }
        },
        {
            "target_doctype": "Quality NCR",
            "label": "Quality NCR",
            "stage": "G8",
            "field_map": {
                "title": lambda doc: f"NCR for PO {doc.name}",
                "project": "project",
                "date_issued": lambda doc: frappe.utils.today()
            }
        }
    ],
    "Factory Acceptance Test": [
        {
            "target_doctype": "Integrated Factory Acceptance Test",
            "label": "Integrated Factory Acceptance Test",
            "stage": "G8.5",
            "prerequisites": [
                {
                    "check": lambda doc: getattr(doc, "result", "") in ["Pass", "Passed", "Completed"] or getattr(doc, "status", "") in ["Completed", "Approved"],
                    "message": "FAT must be Passed/Completed before creating IFAT."
                }
            ],
            "field_map": {
                "title": lambda doc: f"IFAT from {doc.name}",
                "project": "project",
                "purchase_order": "purchase_order",
                "sales_order": "sales_order",
                "fat_reference": "name",
                "customer": "customer",
                "supplier": "supplier",
                "item_code": "item_code"
            }
        },
        {
            "target_doctype": "Snag List",
            "label": "Snag List",
            "stage": "G8.5",
            "field_map": {
                "title": lambda doc: f"Snag List for {doc.name}",
                "project": "project",
                "company": lambda doc: getattr(doc, "company", None) or "ITS",
                "status": lambda doc: "Open"
            }
        }
    ],
    "Integrated Factory Acceptance Test": [
        {
            "target_doctype": "Snag List",
            "label": "Snag List",
            "stage": "G8.5",
            "field_map": {
                "title": lambda doc: f"Snag List for {doc.name}",
                "project": "project",
                "company": lambda doc: getattr(doc, "company", None) or "ITS",
                "status": lambda doc: "Open"
            }
        },
        {
            "target_doctype": "PSS Skid Tracker",
            "label": "PSS Skid Tracker",
            "stage": "G8.5",
            "field_map": {
                "project": "project",
                "supplier": "supplier",
                "ifat_status": lambda doc: getattr(doc, "integration_result", "Passed")
            }
        }
    ],
    "Snag List": [
        {
            "target_doctype": "Project Handover",
            "label": "Project Handover",
            "stage": "G9.7",
            "prerequisites": [
                {
                    "check": lambda doc: getattr(doc, "status", "") in ["Closed", "Resolved", "Cleared"],
                    "message": "Snag List / Punch List must be Resolved before Project Handover."
                }
            ],
            "field_map": {
                "title": lambda doc: f"Handover from Snag List {doc.name}",
                "project": "project",
                "company": "company",
                "status": lambda doc: "Draft"
            }
        }
    ],
    "PSS Skid Tracker": [
        {
            "target_doctype": "Invoice Dossier",
            "label": "Invoice Dossier",
            "stage": "G10",
            "prerequisites": [
                {
                    "check": lambda doc: getattr(doc, "punch_closure_status", "") in ["Closed", "Cleared", "1", 1] or getattr(doc, "punch_list_clearance", 0) == 1,
                    "message": "Punch list must be closed/cleared before creating Invoice Dossier."
                }
            ],
            "field_map": {
                "project": "project",
                "customer": "customer",
                "customer_po": "customer_po",
                "punch_list_clearance": lambda doc: 1 if getattr(doc, "punch_closure_status", "") in ["Closed", "Cleared"] else 0
            }
        }
    ],
    "Delivery Note": [
        {
            "target_doctype": "Project Handover",
            "label": "Project Handover",
            "stage": "G9.7",
            "field_map": {
                "title": lambda doc: f"Handover for Delivery {doc.name}",
                "project": "project",
                "company": "company",
                "status": lambda doc: "Draft"
            }
        },
        {
            "target_doctype": "Invoice Dossier",
            "label": "Invoice Dossier",
            "stage": "G10",
            "field_map": {
                "project": "project",
                "customer": "customer",
                "customer_po": lambda doc: getattr(doc, "po_no", None) or getattr(doc, "lr_no", None)
            }
        },
        {
            "target_doctype": "Sales Invoice",
            "label": "Sales Invoice",
            "stage": "G10.5",
            "prerequisites": [
                {
                    "check": lambda doc: doc.docstatus == 1,
                    "message": "Delivery Note must be Submitted before creating Sales Invoice."
                }
            ],
            "field_map": {
                "customer": "customer",
                "project": "project",
                "company": "company",
                "posting_date": lambda doc: frappe.utils.today(),
                "due_date": lambda doc: frappe.utils.add_days(frappe.utils.today(), 30),
            },
            "child_map": {
                "items": {
                    "source_field": "items",
                    "fields": ["item_code", "item_name", "qty", "rate", "amount", "uom", "description"],
                    "extra": lambda row, doc: {"delivery_note": doc.name, "dn_detail": row.get("name")}
                }
            }
        }
    ],
    "Invoice Dossier": [
        {
            "target_doctype": "Sales Invoice",
            "label": "Sales Invoice",
            "stage": "G10.5",
            "prerequisites": [
                {
                    "check": lambda doc: getattr(doc, "dossier_status", "") in ["Approved", "Validated", "Cleared"] or doc.docstatus == 1,
                    "message": "Invoice Dossier must be Approved/Validated before creating Sales Invoice."
                }
            ],
            "field_map": {
                "customer": "customer",
                "project": "project",
                "company": lambda doc: getattr(doc, "company", None) or frappe.db.get_value("Company", {}) or "ITS",
                "posting_date": lambda doc: frappe.utils.today(),
                "due_date": lambda doc: frappe.utils.add_days(frappe.utils.today(), 30),
                "grand_total": lambda doc: getattr(doc, "net_invoice_amount", 0.0) or getattr(doc, "total_claim_amount", 0.0)
            }
        }
    ],
    "Project Handover": [
        {
            "target_doctype": "Warranty Register",
            "label": "Warranty Register",
            "stage": "G11",
            "field_map": {
                "project": "project",
                "equipment_name": lambda doc: doc.title or f"Warranty for Project {doc.project}",
                "warranty_start": lambda doc: frappe.utils.today(),
                "warranty_end": lambda doc: frappe.utils.add_days(frappe.utils.today(), 365),
                "status": lambda doc: "Active"
            }
        }
    ],
    "Sales Invoice": [
        {
            "target_doctype": "Warranty Register",
            "label": "Warranty Register",
            "stage": "G11",
            "field_map": {
                "project": "project",
                "equipment_name": lambda doc: f"Warranty for Invoice {doc.name}",
                "warranty_start": lambda doc: frappe.utils.today(),
                "warranty_end": lambda doc: frappe.utils.add_days(frappe.utils.today(), 365),
                "status": lambda doc: "Active"
            }
        },
        {
            "target_doctype": "Maintenance Visit",
            "label": "Maintenance Visit",
            "stage": "G11",
            "field_map": {
                "customer": "customer",
                "company": "company",
                "mntc_date": lambda doc: frappe.utils.today(),
                "completion_status": lambda doc: "Draft",
                "maintenance_type": lambda doc: "Scheduled"
            }
        }
    ],
    "Project": [
        {
            "target_doctype": "Finance Commitment",
            "label": "Finance Commitment",
            "stage": "G6",
            "field_map": {"project": "name", "customer_po": lambda doc: f"PO-{doc.name}"}
        },
        {
            "target_doctype": "Sales Order",
            "label": "Sales Order",
            "stage": "G5.5",
            "field_map": {"project": "name", "customer": "customer", "company": "company"}
        },
        {
            "target_doctype": "Factory Acceptance Test",
            "label": "Factory Acceptance Test",
            "stage": "G8",
            "field_map": {"project": "name", "customer": "customer", "title": lambda doc: f"FAT for {doc.name}"}
        },
        {
            "target_doctype": "Invoice Dossier",
            "label": "Invoice Dossier",
            "stage": "G10",
            "field_map": {"project": "name", "customer": "customer"}
        },
        {
            "target_doctype": "PSS Skid Tracker",
            "label": "PSS Skid Tracker",
            "stage": "G8",
            "field_map": {"project": "name", "customer": "customer", "pss_family": lambda doc: "MV Power Skid"}
        }
    ]
}

def get_allowed_next_steps(source_doctype, source_name=None):
    """
    Evaluates allowed next step options for source_doctype and optional source_name.
    Performs security permission check on target DocTypes.
    Returns list of target names.
    """
    if not source_doctype or source_doctype not in FLOW_REGISTRY:
        return []

    source_doc = None
    if source_name:
        try:
            source_doc = frappe.get_doc(source_doctype, source_name)
        except Exception:
            return []

    rules = FLOW_REGISTRY.get(source_doctype, [])
    allowed = []

    for rule in rules:
        target_dt = rule["target_doctype"]
        
        # Check target creation permission for session user
        if not frappe.has_permission(target_dt, "create"):
            continue
            
        # Check doc status / condition if doc present
        if source_doc and "condition" in rule:
            try:
                if not rule["condition"](source_doc):
                    continue
            except Exception:
                pass

        allowed.append(target_dt)

    return allowed

def build_next_step_payload(source_doctype, source_name, target_doctype):
    """
    Evaluates prerequisites, permissions, and builds initial UNSAVED field payload for target_doctype.
    """
    if not source_doctype or not source_name or not target_doctype:
        raise frappe.ValidationError(_("source_doctype, source_name, and target_doctype are required."))

    rules = FLOW_REGISTRY.get(source_doctype, [])
    matching_rule = next((r for r in rules if r["target_doctype"] == target_doctype), None)

    if not matching_rule:
        raise frappe.ValidationError(_("Invalid next step target {0} for source {1}").format(target_doctype, source_doctype))

    if not frappe.has_permission(target_doctype, "create"):
        raise frappe.PermissionError(_("You do not have permission to create {0}").format(target_doctype))

    source_doc = frappe.get_doc(source_doctype, source_name)

    # Validate prerequisites / hard stops
    if "prerequisites" in matching_rule:
        for prereq in matching_rule["prerequisites"]:
            try:
                if not prereq["check"](source_doc):
                    raise frappe.ValidationError(prereq.get("message", _("Prerequisite validation failed.")))
            except frappe.ValidationError:
                raise
            except Exception as e:
                raise frappe.ValidationError(_("Prerequisite check error: {0}").format(str(e)))

    target_meta = frappe.get_meta(target_doctype)
    target_field_names = {f.fieldname for f in target_meta.fields if f.fieldname}

    payload = {}

    # Direct / Lambda Field mapping
    field_map = matching_rule.get("field_map", {})
    for target_field, source_spec in field_map.items():
        if target_field not in target_field_names and not target_field.startswith("custom_"):
            continue

        if callable(source_spec):
            try:
                val = source_spec(source_doc)
                if val is not None:
                    payload[target_field] = val
            except Exception:
                pass
        elif isinstance(source_spec, str):
            val = getattr(source_doc, source_spec, None)
            if val is not None:
                payload[target_field] = val

    # Child Table mapping
    child_map = matching_rule.get("child_map", {})
    for target_table_field, config in child_map.items():
        if target_table_field not in target_field_names:
            continue

        source_table_field = config.get("source_field", "items")
        source_rows = getattr(source_doc, source_table_field, []) or []
        allowed_fields = config.get("fields", [])
        extra_fn = config.get("extra")

        mapped_rows = []
        for row in source_rows:
            row_dict = {}
            for f in allowed_fields:
                val = getattr(row, f, None)
                if val is not None:
                    row_dict[f] = val
            
            if extra_fn and callable(extra_fn):
                try:
                    extra_data = extra_fn(row, source_doc)
                    if isinstance(extra_data, dict):
                        row_dict.update(extra_data)
                except Exception:
                    pass

            if row_dict:
                mapped_rows.append(row_dict)

        if mapped_rows:
            payload[target_table_field] = mapped_rows

    return payload
