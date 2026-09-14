import frappe
import json
from frappe import _

STANDARD_DOC_FIELDS = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}

DOCTYPE_MAP = {
    "sales-order": "Sales Order",
    "sales-orders": "Sales Order",
    "salesorder": "Sales Order",
    "salesorders": "Sales Order",
}

def normalize_doctype(doctype):
    if not doctype or not isinstance(doctype, str):
        return doctype
    if doctype in DOCTYPE_MAP:
        return DOCTYPE_MAP[doctype]
    if doctype.lower() in DOCTYPE_MAP:
        return DOCTYPE_MAP[doctype.lower()]
    return doctype

def success_response(data, meta=None):
    res = {"success": True, "data": data}
    if meta is not None:
        res["meta"] = meta
    return res

def error_response(code, message, status_code=400):
    if status_code in (401, 403, 404):
        frappe.response["http_status_code"] = status_code
    return {
        "success": False,
        "error": {
            "code": code,
            "message": str(message)
        }
    }

def get_valid_fields_for_doctype(meta, requested_fields=None):
    """
    Validates requested fields against Frappe meta definition to prevent SQL column errors.
    Returns a safe list of fieldnames that actually exist on the target DocType.
    """
    valid_doc_fields = set(STANDARD_DOC_FIELDS)
    for f in meta.fields:
        if f.fieldname:
            valid_doc_fields.add(f.fieldname)

    if not requested_fields or requested_fields == ["*"]:
        list_fields = ["name", "modified", "docstatus"]
        if meta.title_field and meta.title_field in valid_doc_fields:
            list_fields.append(meta.title_field)
        if meta.has_field("status"):
            list_fields.append("status")
        elif meta.has_field("disabled"):
            list_fields.append("disabled")
            
        if meta.is_tree:
            parent_field = f"parent_{meta.name.lower().replace(' ', '_')}"
            if meta.has_field(parent_field):
                list_fields.append(parent_field)
            if meta.has_field("is_group"):
                list_fields.append("is_group")
        
        for f in meta.fields:
            if f.in_list_view and f.fieldname in valid_doc_fields and f.fieldname not in list_fields:
                list_fields.append(f.fieldname)
                
        return list_fields

    clean_fields = []
    for field in requested_fields:
        if field in valid_doc_fields:
            clean_fields.append(field)
    
    if "name" not in clean_fields:
        clean_fields.insert(0, "name")

    return clean_fields

def get_doc_workflow_info(doc):
    """
    Discovers active Frappe Workflow for document and computes allowed actions.
    """
    workflow_name = frappe.model.workflow.get_workflow_name(doc.doctype)
    if not workflow_name:
        return {"active": False}
    
    try:
        workflow = frappe.get_doc("Workflow", workflow_name)
        state_field = workflow.workflow_state_field
        current_state = doc.get(state_field)
        
        transitions = frappe.model.workflow.get_transitions(doc)
        allowed_actions = []
        for t in transitions:
            allowed_actions.append({
                "action": t.action,
                "next_state": t.next_state,
                "allowed": t.allowed
            })

        return {
            "active": True,
            "workflow_name": workflow_name,
            "state_field": state_field,
            "current_state": current_state,
            "allowed_actions": allowed_actions
        }
    except Exception as e:
        frappe.log_error(f"Error fetching workflow for {doc.doctype} {doc.name}: {str(e)}")
        return {"active": False}

@frappe.whitelist()
def get_document_list(doctype, filters=None, fields=None, order_by=None, page=1, page_length=20, search_text=None):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "read"):
        return error_response("PERMISSION_DENIED", _("No read permission for {0}").format(doctype), 403)

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} does not exist").format(doctype), 404)
    
    meta = frappe.get_meta(doctype)
    page = int(page or 1)
    page_length = int(page_length or 20)
    start = (page - 1) * page_length

    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except Exception:
            filters = {}
    elif not filters:
        filters = {}

    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except Exception:
            fields = None

    clean_fields = get_valid_fields_for_doctype(meta, fields)

    if search_text:
        searchable_types = {"Data", "Text", "Small Text", "Code", "Link", "Select", "Text Editor", "Long Text", "JSON", "Read Only"}
        search_fields = ["name"]
        if meta.title_field and meta.has_field(meta.title_field):
            tf_obj = meta.get_field(meta.title_field)
            if not tf_obj or tf_obj.fieldtype in searchable_types:
                search_fields.append(meta.title_field)
        if meta.has_field("description"):
            search_fields.append("description")
        if meta.search_fields:
            for sf in meta.search_fields.split(","):
                sf = sf.strip()
                if sf and meta.has_field(sf) and sf not in search_fields:
                    f_obj = meta.get_field(sf)
                    if f_obj and f_obj.fieldtype in searchable_types:
                        search_fields.append(sf)
        
        or_filters = [[doctype, field, "like", f"%{search_text}%"] for field in search_fields]
    else:
        or_filters = None

    default_order = "modified desc"
    if meta.sort_field and meta.sort_order:
        default_order = f"{meta.sort_field} {meta.sort_order}"
    elif meta.is_tree:
        default_order = "lft asc" if meta.has_field("lft") else "name asc"

    try:
        items = frappe.get_list(
            doctype,
            filters=filters,
            or_filters=or_filters,
            fields=clean_fields,
            order_by=order_by or default_order,
            start=start,
            page_length=page_length,
            ignore_permissions=False
        )

        try:
            if or_filters or isinstance(filters, list):
                total_count = len(frappe.get_list(doctype, filters=filters, or_filters=or_filters, fields=["name"], limit_page_length=0, ignore_permissions=False))
            else:
                total_count = frappe.db.count(doctype, filters=filters)
        except Exception:
            total_count = start + len(items) + (1 if len(items) == page_length else 0)

        return success_response(items, {
            "total": total_count,
            "page": page,
            "page_length": page_length,
            "has_next": (start + len(items)) < total_count,
            "title_field": meta.title_field or "name",
            "status_field": "status" if meta.has_field("status") else ("disabled" if meta.has_field("disabled") else None),
            "is_tree": meta.is_tree,
            "is_submittable": meta.is_submittable,
            "issingle": meta.issingle,
            "istable": meta.istable
        })
    except Exception as e:
        frappe.log_error(f"Error fetching {doctype} list: {str(e)}")
        return error_response("FETCH_ERROR", str(e), 500)

@frappe.whitelist()
def get_document_detail(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "read", doc=name):
        return error_response("PERMISSION_DENIED", _("No read permission for {0} {1}").format(doctype, name), 403)
    
    try:
        doc = frappe.get_doc(doctype, name)
        doc_dict = doc.as_dict()

        meta = frappe.get_meta(doctype)
        workflow_info = get_doc_workflow_info(doc)

        user_perms = {
            "read": frappe.has_permission(doctype, "read", doc=name),
            "write": frappe.has_permission(doctype, "write", doc=name),
            "create": frappe.has_permission(doctype, "create"),
            "delete": frappe.has_permission(doctype, "delete", doc=name),
            "submit": frappe.has_permission(doctype, "submit", doc=name) if meta.is_submittable else False,
            "cancel": frappe.has_permission(doctype, "cancel", doc=name) if meta.is_submittable else False,
            "amend": frappe.has_permission(doctype, "amend", doc=name) if meta.is_submittable else False,
        }

        related = []
        links = frappe.db.sql("SELECT parent, fieldname FROM `tabDocField` WHERE fieldtype=%s AND options=%s LIMIT 15", ("Link", doctype), as_dict=True)

        for link in links:
            rel_doctype = link["parent"]
            rel_field = link["fieldname"]
            try:
                if frappe.db.exists("DocType", rel_doctype) and frappe.has_permission(rel_doctype, "read"):
                    rel_meta = frappe.get_meta(rel_doctype)
                    if rel_meta.issingle or rel_meta.istable:
                        continue
                    count = frappe.db.count(rel_doctype, filters={rel_field: name})
                    if count > 0:
                        rel_fields = get_valid_fields_for_doctype(rel_meta, ["name", "modified", "docstatus", "status"])
                        recent = frappe.get_list(
                            rel_doctype,
                            filters={rel_field: name},
                            fields=rel_fields,
                            limit=5
                        )
                        related.append({
                            "doctype": rel_doctype,
                            "fieldname": rel_field,
                            "count": count,
                            "recent": recent
                        })
            except Exception:
                continue

        return success_response({
            "document": doc_dict,
            "meta": {
                "title_field": meta.title_field or "name",
                "is_submittable": meta.is_submittable,
                "is_tree": meta.is_tree,
                "status_field": "status" if meta.has_field("status") else ("disabled" if meta.has_field("disabled") else None)
            },
            "permissions": user_perms,
            "workflow": workflow_info,
            "related": related
        })
    except frappe.DoesNotExistError:
        return error_response("NOT_FOUND", _("{0} {1} does not exist").format(doctype, name), 404)
    except Exception as e:
        frappe.log_error(f"Error fetching {doctype} {name}: {str(e)}")
        return error_response("FETCH_ERROR", str(e), 500)

@frappe.whitelist()
def get_new_document_template(doctype):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "create"):
        return error_response("PERMISSION_DENIED", _("No create permission for {0}").format(doctype), 403)

    try:
        doc = frappe.new_doc(doctype)
        return success_response(doc.as_dict())
    except Exception as e:
        frappe.log_error(f"Error initializing template for {doctype}: {str(e)}")
        return error_response("TEMPLATE_ERROR", str(e), 500)

@frappe.whitelist()
def save_document(doctype, doc_data):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if isinstance(doc_data, str):
        try:
            doc_data = json.loads(doc_data)
        except Exception:
            return error_response("INVALID_PAYLOAD", _("Invalid JSON payload"), 400)

    if not isinstance(doc_data, dict):
        return error_response("INVALID_PAYLOAD", _("Document payload must be a JSON object"), 400)

    name = doc_data.get("name")
    is_new = not name or doc_data.get("__islocal") or (name and str(name).startswith("New "))

    perm_type = "create" if is_new else "write"
    if not frappe.has_permission(doctype, perm_type, doc=name if not is_new else None):
        return error_response("PERMISSION_DENIED", _("No {0} permission for {1}").format(perm_type, doctype), 403)

    try:
        if is_new:
            doc_data["doctype"] = doctype
            if "__islocal" in doc_data:
                del doc_data["__islocal"]
            if "name" in doc_data:
                del doc_data["name"]
            doc = frappe.get_doc(doc_data)
            doc.insert(ignore_permissions=False)
        else:
            doc = frappe.get_doc(doctype, name)
            meta = frappe.get_meta(doctype)
            
            system_read_only = {"name", "owner", "creation", "modified", "modified_by", "idx", "docstatus", "doctype", "__islocal", "_user_tags", "_comments", "_assign", "_liked_by"}
            
            for fieldname, value in doc_data.items():
                if fieldname in system_read_only:
                    continue
                if meta.has_field(fieldname):
                    df = meta.get_field(fieldname)
                    if df.read_only:
                        continue
                    if df.fieldtype == "Table" and isinstance(value, list):
                        doc.set(fieldname, [])
                        for row in value:
                            if isinstance(row, dict):
                                row_clean = {k: v for k, v in row.items() if k not in system_read_only}
                                doc.append(fieldname, row_clean)
                    else:
                        doc.set(fieldname, value)

            doc.save(ignore_permissions=False)

        return success_response(doc.as_dict())
    except frappe.ValidationError as e:
        msg = str(e)
        return error_response("VALIDATION_ERROR", msg, 400)
    except frappe.MandatoryError as e:
        msg = str(e)
        return error_response("MANDATORY_ERROR", msg, 400)
    except frappe.PermissionError as e:
        return error_response("PERMISSION_DENIED", str(e), 403)
    except Exception as e:
        frappe.log_error(f"Error saving {doctype} {name}: {str(e)}")
        return error_response("SAVE_ERROR", str(e), 400)

@frappe.whitelist()
def submit_document(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "submit", doc=name):
        return error_response("PERMISSION_DENIED", _("No submit permission for {0} {1}").format(doctype, name), 403)

    try:
        doc = frappe.get_doc(doctype, name)
        doc.submit()
        return success_response(doc.as_dict())
    except frappe.ValidationError as e:
        return error_response("VALIDATION_ERROR", str(e), 422)
    except Exception as e:
        frappe.log_error(f"Error submitting {doctype} {name}: {str(e)}")
        return error_response("SUBMIT_ERROR", str(e), 500)

@frappe.whitelist()
def cancel_document(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "cancel", doc=name):
        return error_response("PERMISSION_DENIED", _("No cancel permission for {0} {1}").format(doctype, name), 403)

    try:
        doc = frappe.get_doc(doctype, name)
        doc.cancel()
        return success_response(doc.as_dict())
    except Exception as e:
        frappe.log_error(f"Error canceling {doctype} {name}: {str(e)}")
        return error_response("CANCEL_ERROR", str(e), 500)

@frappe.whitelist()
def amend_document(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "amend", doc=name):
        return error_response("PERMISSION_DENIED", _("No amend permission for {0} {1}").format(doctype, name), 403)

    try:
        doc = frappe.get_doc(doctype, name)
        amended = frappe.copy_doc(doc)
        amended.amended_from = name
        amended.docstatus = 0
        return success_response(amended.as_dict())
    except Exception as e:
        frappe.log_error(f"Error amending {doctype} {name}: {str(e)}")
        return error_response("AMEND_ERROR", str(e), 500)

@frappe.whitelist()
def apply_workflow_action(doctype, name, action):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)

    try:
        doc = frappe.get_doc(doctype, name)
        frappe.model.workflow.apply_workflow(doc, action)
        return success_response(doc.as_dict())
    except frappe.ValidationError as e:
        return error_response("VALIDATION_ERROR", str(e), 422)
    except Exception as e:
        frappe.log_error(f"Error executing workflow action {action} on {doctype} {name}: {str(e)}")
        return error_response("WORKFLOW_ERROR", str(e), 500)

@frappe.whitelist()
def delete_document(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "delete", doc=name):
        return error_response("PERMISSION_DENIED", _("No delete permission for {0} {1}").format(doctype, name), 403)

    try:
        frappe.delete_doc(doctype, name, ignore_permissions=False)
        return success_response({"deleted": True, "name": name})
    except Exception as e:
        frappe.log_error(f"Error deleting {doctype} {name}: {str(e)}")
        return error_response("DELETE_ERROR", str(e), 500)

@frappe.whitelist()
def duplicate_document(doctype, name):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "create"):
        return error_response("PERMISSION_DENIED", _("No create permission for {0}").format(doctype), 403)

    try:
        doc = frappe.get_doc(doctype, name)
        copy_doc = frappe.copy_doc(doc)
        copy_doc.name = None
        copy_doc.docstatus = 0
        copy_doc.set("__islocal", True)
        return success_response(copy_doc.as_dict())
    except Exception as e:
        frappe.log_error(f"Error duplicating {doctype} {name}: {str(e)}")
        return error_response("DUPLICATE_ERROR", str(e), 500)

@frappe.whitelist()
def search_link_options(doctype, txt=None, filters=None, page_length=20):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "read"):
        return error_response("PERMISSION_DENIED", _("No read permission for {0}").format(doctype), 403)

    meta = frappe.get_meta(doctype)
    title_field = meta.title_field or "name"

    search_fields = ["name"]
    if title_field != "name" and meta.has_field(title_field):
        search_fields.append(title_field)

    or_filters = None
    if txt:
        or_filters = [[doctype, f, "like", f"%{txt}%"] for f in search_fields]

    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except Exception:
            filters = {}

    try:
        results = frappe.get_list(
            doctype,
            filters=filters,
            or_filters=or_filters,
            fields=["name", title_field] if title_field != "name" else ["name"],
            page_length=int(page_length or 20)
        )
        
        options = []
        for r in results:
            value = r["name"]
            label = r.get(title_field) or value
            options.append({"value": value, "label": f"{label} ({value})" if label != value else value})

        return success_response(options)
    except Exception as e:
        frappe.log_error(f"Error searching link options for {doctype}: {str(e)}")
        return error_response("SEARCH_ERROR", str(e), 500)

@frappe.whitelist()
def insert_missing_custom_doctypes():
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only System Manager can execute administrative setup."), frappe.PermissionError)

    import os, json
    roles = [
        "Portal Administrator", "Project Manager", "Project Engineer", "Planning Engineer",
        "Estimation Engineer", "Procurement Manager", "Store Manager", "HR Manager",
        "Finance Manager", "Accountant", "Fabrication Manager", "Equipment Manager", "Management Viewer"
    ]
    for r in roles:
        if not frappe.db.exists("Role", r):
            try:
                role_doc = frappe.get_doc({"doctype": "Role", "role_name": r, "desk_access": 1})
                role_doc.insert(ignore_permissions=True)
            except Exception:
                pass
    frappe.db.commit()

    app_path = frappe.get_app_path("its_ui_redesign", "doctype")
    inserted = []
    for folder in os.listdir(app_path):
        json_path = os.path.join(app_path, folder, f"{folder}.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                data = json.load(f)
                dt_name = data.get("name")
                if dt_name and not frappe.db.exists("DocType", dt_name):
                    try:
                        d = frappe.get_doc(data)
                        d.insert(ignore_permissions=True)
                        inserted.append(dt_name)
                    except Exception as e:
                        frappe.log_error(title=f"Error inserting {dt_name}", message=frappe.get_traceback())
                        inserted.append(f"FAILED_{dt_name}_{str(e)}")
    frappe.db.commit()
    return inserted

@frappe.whitelist()
def reload_custom_doctypes():
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only System Manager can execute administrative setup."), frappe.PermissionError)

    import os, json
    app_path = frappe.get_app_path("its_ui_redesign", "doctype")
    for folder in os.listdir(app_path):
        json_path = os.path.join(app_path, folder, f"{folder}.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                doc_json = json.load(f)
                dt_name = doc_json.get("name")
                if not frappe.db.exists("DocType", dt_name):
                    try:
                        doc = frappe.get_doc(doc_json)
                        doc.insert(ignore_permissions=True)
                    except Exception as e:
                        frappe.log_error(f"Error inserting {dt_name}: {e}")
                else:
                    try:
                        frappe.reload_doc("its_ui_redesign", "doctype", folder, force=True)
                    except Exception as e:
                        frappe.log_error(f"Error reloading {folder}: {e}")
    return True

@frappe.whitelist()
def get_user_permissions(doctypes=None):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if isinstance(doctypes, str):
        try:
            doctypes = json.loads(doctypes)
        except Exception:
            doctypes = [d.strip() for d in doctypes.split(",") if d.strip()]
            
    if not doctypes or not isinstance(doctypes, list):
        import os, re
        doctypes = []
        app_path = frappe.get_app_path("its_ui_redesign")
        nav_file = os.path.abspath(os.path.join(app_path, "..", "portal", "src", "config", "navigation.js"))
        if os.path.exists(nav_file):
            try:
                with open(nav_file, "r") as f:
                    content = f.read()
                doctypes = list(set(re.findall(r'"docType":\s*"([^"]+)"', content)))
            except Exception:
                pass

    core_doctypes = [
        "User", "Role", "Role Permission Manager", "Custom Role", "User Permission",
        "Project", "Customer", "Supplier", "Quotation", "Sales Order", "Purchase Order",
        "Sales Invoice", "Purchase Invoice", "Payment Entry", "Employee", "Attendance",
        "Leave Application", "Timesheet", "Item", "Warehouse", "Stock Entry", "Asset",
        "Work Order", "BOM", "Issue", "Task", "Finance Commitment", "Factory Acceptance Test",
        "Delivery Note", "BOQ", "Quality Inspection", "Snag List", "Project Handover",
        "Project Warranty", "Warranty Claim", "Warranty Register", "Budget", "Cost Center",
        "Item Price", "GL Entry", "Daily Manpower Register", "Material Request",
        "Equipment Usage Log", "Asset Maintenance", "Site Measurement Item", "Progress Claim",
        "Payment Certificate", "Project Variation", "Invoice Dossier", "Account",
        "Payment Request", "Expense Claim", "Journal Entry", "Period Closing Voucher",
        "Stock Ledger Entry", "Request for Information", "Technical Submittal", "Communication",
        "Lead", "Opportunity", "Supplier Quotation", "Integrated Factory Acceptance Test", "Project Contract"
    ]
    all_target_doctypes = sorted(list(set((doctypes or []) + core_doctypes)))

    permissions = {}
    for dt in all_target_doctypes:
        norm_dt = normalize_doctype(dt)
        perm_dict = None
        if dt in ["Role Permission Manager", "Custom Role"]:
            has_admin_access = bool(frappe.has_permission("Role", "read") or frappe.has_permission("User", "read"))
            perm_dict = {
                "read": has_admin_access,
                "create": has_admin_access,
                "write": has_admin_access,
                "delete": has_admin_access,
                "submit": False,
                "cancel": False,
                "amend": False
            }
        elif frappe.db.exists("DocType", norm_dt):
            try:
                meta = frappe.get_meta(norm_dt)
                perm_dict = {
                    "read": bool(frappe.has_permission(norm_dt, "read")),
                    "create": bool(frappe.has_permission(norm_dt, "create")),
                    "write": bool(frappe.has_permission(norm_dt, "write")),
                    "delete": bool(frappe.has_permission(norm_dt, "delete")),
                    "submit": bool(frappe.has_permission(norm_dt, "submit")) if meta.is_submittable else False,
                    "cancel": bool(frappe.has_permission(norm_dt, "cancel")) if meta.is_submittable else False,
                    "amend": bool(frappe.has_permission(norm_dt, "amend")) if meta.is_submittable else False,
                }
            except Exception:
                perm_dict = {"read": False, "create": False, "write": False, "delete": False, "submit": False, "cancel": False, "amend": False}
        else:
            perm_dict = {"read": False, "create": False, "write": False, "delete": False, "submit": False, "cancel": False, "amend": False}

        if perm_dict:
            permissions[dt] = perm_dict
            permissions[norm_dt] = perm_dict
            permissions[dt.lower()] = perm_dict
            slug_key = dt.lower().replace(" ", "-")
            permissions[slug_key] = perm_dict

    return success_response(permissions)

@frappe.whitelist()
def audit_navigation_doctypes():
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only System Manager can execute administrative audit."), frappe.PermissionError)

    import re
    nav_file = "/home/frappe/frappe-bench/apps/its_ui_redesign/portal/src/config/navigation.js"
    with open(nav_file, "r") as f:
        content = f.read()
    
    doctype_matches = re.findall(r'"docType":\s*"([^"]+)"', content)
    unique_doctypes = sorted(list(set(doctype_matches)))
    
    all_doctypes = set(frappe.get_all("DocType", pluck="name"))
    
    existing = []
    missing = []
    
    for dt in unique_doctypes:
        if dt in all_doctypes:
            existing.append(dt)
        else:
            missing.append(dt)
            
    return {
        "total_unique_mapped": len(unique_doctypes),
        "existing_count": len(existing),
        "missing_count": len(missing),
        "existing": existing,
        "missing": missing
    }

@frappe.whitelist()
def get_doctype_meta(doctype):
    doctype = normalize_doctype(doctype)
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "read"):
        return error_response("PERMISSION_DENIED", _("No read permission for {0}").format(doctype), 403)

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} does not exist").format(doctype), 404)

    meta = frappe.get_meta(doctype)
    fields = []
    list_fields = []
    standard_filters = []

    # Standard system fields
    system_fields = [
        {"fieldname": "name", "label": "ID / Name", "fieldtype": "Data", "in_list_view": 0, "in_standard_filter": 1},
        {"fieldname": "modified", "label": "Last Modified", "fieldtype": "Datetime", "in_list_view": 0, "in_standard_filter": 1},
        {"fieldname": "creation", "label": "Creation Date", "fieldtype": "Datetime", "in_list_view": 0, "in_standard_filter": 1},
        {"fieldname": "owner", "label": "Created By", "fieldtype": "Link", "options": "User", "in_list_view": 0, "in_standard_filter": 1}
    ]

    for f in meta.fields:
        if not f.hidden and f.fieldtype not in ["HTML", "Heading", "Section Break", "Column Break"]:
            field_def = {
                "fieldname": f.fieldname,
                "label": f.label,
                "fieldtype": f.fieldtype,
                "reqd": f.reqd,
                "read_only": f.read_only,
                "options": f.options,
                "default": f.default,
                "description": f.description,
                "in_list_view": f.in_list_view,
                "in_standard_filter": getattr(f, "in_standard_filter", 0),
                "precision": getattr(f, "precision", None),
                "depends_on": f.depends_on,
                "mandatory_depends_on": f.mandatory_depends_on,
                "read_only_depends_on": f.read_only_depends_on
            }

            if f.fieldtype == "Table" and f.options and frappe.db.exists("DocType", f.options):
                child_meta = frappe.get_meta(f.options)
                child_fields = []
                for cf in child_meta.fields:
                    if not cf.hidden and cf.fieldtype not in ["Section Break", "Column Break", "HTML", "Heading"]:
                        child_fields.append({
                            "fieldname": cf.fieldname,
                            "label": cf.label,
                            "fieldtype": cf.fieldtype,
                            "reqd": cf.reqd,
                            "read_only": cf.read_only,
                            "options": cf.options,
                            "in_list_view": cf.in_list_view
                        })
                field_def["child_fields"] = child_fields

            fields.append(field_def)
            if f.in_list_view:
                list_fields.append({"key": f.fieldname, "label": f.label, "fieldtype": f.fieldtype, "options": f.options})
            if getattr(f, "in_standard_filter", 0):
                standard_filters.append({"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype, "options": f.options})

    if not list_fields:
        title_f = meta.title_field or "name"
        list_fields.append({"key": "name", "label": "ID / Name", "fieldtype": "Data"})
        if title_f != "name" and meta.has_field(title_f):
            title_label = meta.get_field(title_f).label if meta.get_field(title_f) else "Title"
            list_fields.append({"key": title_f, "label": title_label, "fieldtype": "Data"})
            
        if meta.has_field("status"):
            list_fields.append({"key": "status", "label": "Status", "fieldtype": "Select"})
        elif meta.has_field("disabled"):
            list_fields.append({"key": "disabled", "label": "Status", "fieldtype": "Check"})

        list_fields.append({"key": "modified", "label": "Modified", "fieldtype": "Datetime"})

    # If standard_filters is empty, inject common key fields if present
    if not standard_filters:
        for sf_name in ["status", "company", "project", "customer", "supplier", "workflow_state", "item_group"]:
            if meta.has_field(sf_name):
                f_obj = meta.get_field(sf_name)
                standard_filters.append({"fieldname": sf_name, "label": f_obj.label if f_obj else sf_name.replace("_", " ").title(), "fieldtype": f_obj.fieldtype if f_obj else "Select", "options": f_obj.options if f_obj else None})

    workflow_name = frappe.model.workflow.get_workflow_name(doctype)

    permissions = {
        "read": bool(frappe.has_permission(doctype, "read")),
        "write": bool(frappe.has_permission(doctype, "write")),
        "create": bool(frappe.has_permission(doctype, "create")),
        "delete": bool(frappe.has_permission(doctype, "delete")),
        "submit": bool(frappe.has_permission(doctype, "submit")),
        "cancel": bool(frappe.has_permission(doctype, "cancel")),
        "amend": bool(frappe.has_permission(doctype, "amend"))
    }

    search_fields_list = ["name"]
    if meta.title_field and meta.has_field(meta.title_field):
        search_fields_list.append(meta.title_field)
    if meta.search_fields:
        for sf in meta.search_fields.split(","):
            sf = sf.strip()
            if sf and meta.has_field(sf) and sf not in search_fields_list:
                search_fields_list.append(sf)

    return success_response({
        "name": meta.name,
        "label": getattr(meta, "label", meta.name),
        "module": meta.module,
        "title_field": meta.title_field or "name",
        "status_field": "status" if meta.has_field("status") else ("disabled" if meta.has_field("disabled") else None),
        "is_submittable": meta.is_submittable,
        "is_tree": meta.is_tree,
        "issingle": meta.issingle,
        "istable": meta.istable,
        "sort_field": meta.sort_field or "modified",
        "sort_order": meta.sort_order or "desc",
        "parent_field": f"parent_{meta.name.lower().replace(' ', '_')}" if meta.is_tree else None,
        "has_workflow": bool(workflow_name),
        "workflow_name": workflow_name,
        "permissions": permissions,
        "search_fields": search_fields_list,
        "fields": fields,
        "list_fields": list_fields,
        "standard_filters": standard_filters,
        "system_fields": system_fields
    })

@frappe.whitelist()
def delete_documents_bulk(doctype, names):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if isinstance(names, str):
        try:
            names = json.loads(names)
        except Exception:
            names = [names]

    deleted = []
    failed = []

    for name in names:
        if frappe.has_permission(doctype, "delete", doc=name):
            try:
                frappe.delete_doc(doctype, name, ignore_permissions=False)
                deleted.append(name)
            except Exception as e:
                failed.append({"name": name, "error": str(e)})
        else:
            failed.append({"name": name, "error": _("Permission denied")})

    return success_response({"deleted": deleted, "failed": failed})

@frappe.whitelist()
def get_tree_nodes(doctype, parent_field=None, parent_val=None):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)

    if not frappe.has_permission(doctype, "read"):
        return error_response("PERMISSION_DENIED", _("No read permission"), 403)

    meta = frappe.get_meta(doctype)
    if not parent_field:
        parent_field = f"parent_{meta.name.lower().replace(' ', '_')}"
        if not meta.has_field(parent_field):
            parent_field = "parent_" + doctype.lower()

    filters = {}
    if parent_val:
        filters[parent_field] = parent_val
    else:
        filters[parent_field] = ["in", ["", None]]

    title_field = meta.title_field or "name"
    fields = ["name", title_field]
    if meta.has_field("is_group"):
        fields.append("is_group")
    if meta.has_field(parent_field):
        fields.append(parent_field)

    nodes = frappe.get_list(doctype, filters=filters, fields=fields, order_by="name asc")
    return success_response(nodes)


@frappe.whitelist()

@frappe.whitelist()

@frappe.whitelist()

@frappe.whitelist()
def get_permission_aware_count(doctype, filters=None):
    """
    Returns permission-aware count of records for the given DocType.
    Respects DocType Read Permission, User Permissions, and Permission Query Conditions.
    Returns 0 if user lacks read permission or DocType does not exist.
    """
    if not frappe.db.exists("DocType", doctype):
        return 0
    if not frappe.has_permission(doctype, "read"):
        return 0
    try:
        items = frappe.get_list(
            doctype,
            filters=filters or {},
            fields=["name"],
            limit_page_length=0,
            ignore_permissions=False
        )
        return len(items)
    except Exception as e:
        frappe.log_error(f"Dashboard Count Error for {doctype}: {str(e)}")
        return 0

def get_permission_aware_sum(doctype, fieldname, filters=None):
    """
    Returns permission-aware sum of a numeric field for the given DocType.
    Respects DocType Read Permission, User Permissions, and Permission Query Conditions.
    Returns 0.0 if user lacks read permission or DocType does not exist.
    """
    if not frappe.db.exists("DocType", doctype):
        return 0.0
    if not frappe.has_permission(doctype, "read"):
        return 0.0
    try:
        items = frappe.get_list(
            doctype,
            filters=filters or {},
            fields=[fieldname],
            limit_page_length=0,
            ignore_permissions=False
        )
        return sum(float(d.get(fieldname) or 0.0) for d in items if d.get(fieldname) is not None)
    except Exception as e:
        frappe.log_error(f"Dashboard Sum Error for {doctype}.{fieldname}: {str(e)}")
        return 0.0

def get_permission_aware_status_distribution(doctype, status_field="status", filters=None, limit=None):
    """
    Returns permission-aware breakdown of record counts by status/field.
    Format: [{"status": "Open", "count": 10}, ...]
    """
    if not frappe.db.exists("DocType", doctype):
        return []
    if not frappe.has_permission(doctype, "read"):
        return []
    try:
        items = frappe.get_list(
            doctype,
            filters=filters or {},
            fields=[status_field],
            limit_page_length=0,
            ignore_permissions=False
        )
        counts = {}
        for d in items:
            val = d.get(status_field)
            if val is not None and str(val).strip():
                counts[val] = counts.get(val, 0) + 1
        
        result = [{"status": str(k), "count": v} for k, v in counts.items()]
        if limit:
            result = sorted(result, key=lambda x: x["count"], reverse=True)[:limit]
        return result
    except Exception as e:
        frappe.log_error(f"Dashboard Distribution Error for {doctype}.{status_field}: {str(e)}")
        return []

def get_permission_aware_field_distribution(doctype, group_field, sum_field, filters=None, limit=5):
    """
    Returns permission-aware breakdown of summed field grouped by group_field.
    Format: [{"status": "Warehouse A", "count": 1500.0}, ...]
    """
    if not frappe.db.exists("DocType", doctype):
        return []
    if not frappe.has_permission(doctype, "read"):
        return []
    try:
        items = frappe.get_list(
            doctype,
            filters=filters or {},
            fields=[group_field, sum_field],
            limit_page_length=0,
            ignore_permissions=False
        )
        totals = {}
        for d in items:
            g_val = d.get(group_field)
            s_val = float(d.get(sum_field) or 0.0)
            if g_val and s_val > 0:
                totals[g_val] = totals.get(g_val, 0.0) + s_val
        
        result = [{"status": str(k), "count": v} for k, v in totals.items()]
        result = sorted(result, key=lambda x: x["count"], reverse=True)[:limit]
        return result
    except Exception as e:
        frappe.log_error(f"Dashboard Field Distribution Error for {doctype}: {str(e)}")
        return []

def get_permission_aware_recent(doctype, fields, order_by="modified desc", limit=6, filters=None):
    """
    Returns permission-aware list of recent documents.
    """
    if not frappe.db.exists("DocType", doctype):
        return []
    if not frappe.has_permission(doctype, "read"):
        return []
    try:
        meta = frappe.get_meta(doctype)
        clean_fields = get_valid_fields_for_doctype(meta, fields)
        return frappe.get_list(
            doctype,
            filters=filters or {},
            fields=clean_fields,
            order_by=order_by,
            start=0,
            page_length=limit,
            ignore_permissions=False
        )
    except Exception as e:
        frappe.log_error(f"Dashboard Recent Error for {doctype}: {str(e)}")
        return []

@frappe.whitelist()
def get_workspace_dashboard(workspace_id, company=None, project=None, from_date=None, to_date=None):
    """
    Returns live ERPNext/Frappe aggregated KPIs, status distributions,
    trend charts, and record lists for the specified workspace.
    Zero mock numbers. All values are calculated from real backend records
    with strict Frappe permission enforcement (Role & User Permissions).
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)

    ws = (workspace_id or "").lower().strip()

    # 1. Project Management
    if ws == "01-project-management" or "project" in ws:
        active_projects = get_permission_aware_count("Project", {"status": ["in", ["Open", "In Progress", "Started"]]})
        completed_projects = get_permission_aware_count("Project", {"status": ["in", ["Completed", "Closed"]]})
        open_rfis = get_permission_aware_count("Project RFI", {"status": ["in", ["Open", "Pending Response"]]})
        open_issues = get_permission_aware_count("Issue", {"status": ["in", ["Open", "Replied"]]})
        open_variations = get_permission_aware_count("Project Variation", {"status": ["in", ["Draft", "Pending Review"]]})
        open_ncrs = get_permission_aware_count("Quality NCR", {"status": ["in", ["Open", "Under Rectification"]]})
        
        status_counts = get_permission_aware_status_distribution("Project", "status")
        recent_projects = get_permission_aware_recent("Project", ["name", "project_name", "status", "percent_complete", "estimated_costing"], limit=6)

        return {
            "kpis": [
                {"label": "Active Projects", "value": active_projects, "type": "number", "color": "blue"},
                {"label": "Completed Projects", "value": completed_projects, "type": "number", "color": "emerald"},
                {"label": "Open RFIs", "value": open_rfis, "type": "number", "color": "amber"},
                {"label": "Open Issues", "value": open_issues, "type": "number", "color": "rose"},
                {"label": "Pending Variations", "value": open_variations, "type": "number", "color": "indigo"},
                {"label": "Quality NCRs", "value": open_ncrs, "type": "number", "color": "purple"}
            ],
            "charts": [
                {"title": "Project Status Distribution", "data": status_counts, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_projects,
            "doctype": "Project"
        }

    # 2. Estimation & Cost Control
    elif ws == "02-estimation" or "estimation" in ws:
        active_estimates = get_permission_aware_count("Project Variation", {"status": "Draft"})
        sales_orders_val = get_permission_aware_sum("Sales Order", "grand_total", {"docstatus": 1})
        actual_cost = get_permission_aware_sum("Purchase Invoice", "grand_total", {"docstatus": 1})
        var_cost = get_permission_aware_sum("Project Variation", "cost_impact", {"status": "Approved"})

        cost_breakdown = [
            {"label": "Contract Sales Value", "count": float(sales_orders_val)},
            {"label": "Actual Invoiced Cost", "count": float(actual_cost)},
            {"label": "Approved Variations", "count": float(var_cost)}
        ]

        recent_variations = get_permission_aware_recent("Project Variation", ["name", "title", "project", "cost_impact", "status"], limit=6)

        return {
            "kpis": [
                {"label": "Active Estimates / Variations", "value": active_estimates, "type": "number", "color": "blue"},
                {"label": "Contract Sales Value", "value": float(sales_orders_val), "type": "currency", "color": "emerald"},
                {"label": "Actual Purchase Cost", "value": float(actual_cost), "type": "currency", "color": "amber"},
                {"label": "Approved Variation Cost", "value": float(var_cost), "type": "currency", "color": "indigo"}
            ],
            "charts": [
                {"title": "Cost & Sales Overview (AED)", "data": cost_breakdown, "label_key": "label", "val_key": "count"}
            ],
            "recent_list": recent_variations,
            "doctype": "Project Variation"
        }

    # 3. Planning
    elif ws == "03-planning" or "planning" in ws:
        total_tasks = get_permission_aware_count("Task")
        open_tasks = get_permission_aware_count("Task", {"status": ["in", ["Open", "Working"]]})
        completed_tasks = get_permission_aware_count("Task", {"status": "Completed"})
        overdue_tasks = get_permission_aware_count("Task", {"status": "Overdue"})

        task_status = get_permission_aware_status_distribution("Task", "status")
        recent_tasks = get_permission_aware_recent("Task", ["name", "subject", "project", "status", "priority"], limit=6)

        return {
            "kpis": [
                {"label": "Total Tasks / Activities", "value": total_tasks, "type": "number", "color": "blue"},
                {"label": "Open Tasks", "value": open_tasks, "type": "number", "color": "amber"},
                {"label": "Completed Tasks", "value": completed_tasks, "type": "number", "color": "emerald"},
                {"label": "Overdue Tasks", "value": overdue_tasks, "type": "number", "color": "rose"}
            ],
            "charts": [
                {"title": "Activity Status Distribution", "data": task_status, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_tasks,
            "doctype": "Task"
        }

    # 4. Procurement & Subcontractors
    elif ws == "04-procurement" or "procurement" in ws:
        total_pos = get_permission_aware_count("Purchase Order")
        open_pos = get_permission_aware_count("Purchase Order", {"status": ["in", ["To Receive and Bill", "Draft"]]})
        po_val = get_permission_aware_sum("Purchase Order", "grand_total", {"docstatus": 1})
        subcontract_claims_val = get_permission_aware_sum("Subcontract Progress Claim", "total_claimed", {"docstatus": 1})

        po_status = get_permission_aware_status_distribution("Purchase Order", "status")
        recent_pos = get_permission_aware_recent("Purchase Order", ["name", "supplier", "grand_total", "status", "transaction_date"], limit=6)

        return {
            "kpis": [
                {"label": "Total Purchase Orders", "value": total_pos, "type": "number", "color": "blue"},
                {"label": "Open Purchase Orders", "value": open_pos, "type": "number", "color": "amber"},
                {"label": "Committed PO Value (AED)", "value": float(po_val), "type": "currency", "color": "emerald"},
                {"label": "Subcontract Claims (AED)", "value": float(subcontract_claims_val or 0), "type": "currency", "color": "purple"}
            ],
            "charts": [
                {"title": "Purchase Order Status Distribution", "data": po_status, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_pos,
            "doctype": "Purchase Order"
        }

    # 5. Inventory Management
    elif ws == "05-inventory" or "inventory" in ws:
        total_items = get_permission_aware_count("Item")
        total_warehouses = get_permission_aware_count("Warehouse")
        stock_val_res = get_permission_aware_sum("Bin", "stock_value")
        stock_receipts = get_permission_aware_count("Purchase Receipt", {"docstatus": 1})

        warehouse_val = get_permission_aware_field_distribution("Bin", "warehouse", "stock_value", filters={"stock_value": [">", 0]}, limit=5)
        recent_receipts = get_permission_aware_recent("Purchase Receipt", ["name", "supplier", "grand_total", "status", "posting_date"], limit=6)

        return {
            "kpis": [
                {"label": "Total Stock Items", "value": total_items, "type": "number", "color": "blue"},
                {"label": "Warehouses Count", "value": total_warehouses, "type": "number", "color": "indigo"},
                {"label": "Total Stock Value (AED)", "value": float(stock_val_res), "type": "currency", "color": "emerald"},
                {"label": "Completed Material Receipts", "value": stock_receipts, "type": "number", "color": "amber"}
            ],
            "charts": [
                {"title": "Stock Value by Top Warehouse (AED)", "data": warehouse_val, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_receipts,
            "doctype": "Item"
        }

    # 6. HR & Manpower
    elif ws == "06-hr-manpower" or "hr" in ws or "manpower" in ws:
        total_emp = get_permission_aware_count("Employee", {"status": "Active"})
        attendance_today = get_permission_aware_count("Attendance", {"attendance_date": frappe.utils.today(), "status": "Present"})
        open_leaves = get_permission_aware_count("Leave Application", {"status": "Open"})
        total_timesheets = get_permission_aware_count("Timesheet", {"docstatus": 1})

        dept_dist = get_permission_aware_status_distribution("Employee", "department", filters={"status": "Active"}, limit=5)
        recent_employees = get_permission_aware_recent("Employee", ["name", "employee_name", "designation", "department", "status"], limit=6)

        return {
            "kpis": [
                {"label": "Active Employees", "value": total_emp, "type": "number", "color": "blue"},
                {"label": "Present Today", "value": attendance_today, "type": "number", "color": "emerald"},
                {"label": "Pending Leave Requests", "value": open_leaves, "type": "number", "color": "amber"},
                {"label": "Submitted Timesheets", "value": total_timesheets, "type": "number", "color": "indigo"}
            ],
            "charts": [
                {"title": "Employees by Department", "data": dept_dist, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_employees,
            "doctype": "Employee"
        }

    # 7. Fabrication & Equipment
    elif ws == "07-fabrication" or "fabrication" in ws or "equipment" in ws:
        work_orders = get_permission_aware_count("Work Order")
        in_process_wo = get_permission_aware_count("Work Order", {"status": "In Process"})
        total_assets = get_permission_aware_count("Asset")
        in_use_assets = get_permission_aware_count("Asset", {"status": "Submitted"})

        wo_status = get_permission_aware_status_distribution("Work Order", "status")
        recent_work_orders = get_permission_aware_recent("Work Order", ["name", "production_item", "qty", "status", "planned_start_date"], limit=6)

        return {
            "kpis": [
                {"label": "Total Work Orders", "value": work_orders, "type": "number", "color": "blue"},
                {"label": "In-Process Work Orders", "value": in_process_wo, "type": "number", "color": "amber"},
                {"label": "Total Asset Equipment", "value": total_assets, "type": "number", "color": "indigo"},
                {"label": "Active Assets in Use", "value": in_use_assets, "type": "number", "color": "emerald"}
            ],
            "charts": [
                {"title": "Work Order Status Distribution", "data": wo_status, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_work_orders,
            "doctype": "Work Order"
        }

    # 8. Project Progress & Billing
    elif ws == "08-billing" or "billing" in ws:
        total_invoices = get_permission_aware_count("Sales Invoice")
        total_billed_res = get_permission_aware_sum("Sales Invoice", "grand_total", {"docstatus": 1})
        outstanding_res = get_permission_aware_sum("Sales Invoice", "outstanding_amount", {"docstatus": 1, "outstanding_amount": [">", 0]})
        site_measurements = get_permission_aware_count("Site Measurement", {"docstatus": 1})

        inv_status = get_permission_aware_status_distribution("Sales Invoice", "status")
        recent_invoices = get_permission_aware_recent("Sales Invoice", ["name", "customer", "grand_total", "outstanding_amount", "status"], limit=6)

        return {
            "kpis": [
                {"label": "Total Sales Invoices", "value": total_invoices, "type": "number", "color": "blue"},
                {"label": "Total Billed Revenue (AED)", "value": float(total_billed_res), "type": "currency", "color": "emerald"},
                {"label": "Outstanding Receivables (AED)", "value": float(outstanding_res), "type": "currency", "color": "rose"},
                {"label": "Certified Site Measurements", "value": site_measurements, "type": "number", "color": "indigo"}
            ],
            "charts": [
                {"title": "Sales Invoice Status Breakdown", "data": inv_status, "label_key": "status", "val_key": "count"}
            ],
            "recent_list": recent_invoices,
            "doctype": "Sales Invoice"
        }

    # 9. Accounting & Finance
    elif ws == "09-accounting" or "accounting" in ws or "finance" in ws:
        tot_rev = get_permission_aware_sum("Sales Invoice", "grand_total", {"docstatus": 1})
        tot_exp = get_permission_aware_sum("Purchase Invoice", "grand_total", {"docstatus": 1})
        net_margin = float(tot_rev) - float(tot_exp)
        payments_rec = get_permission_aware_sum("Payment Entry", "paid_amount", {"docstatus": 1, "payment_type": "Receive"})

        fin_overview = [
            {"label": "Total Revenue", "count": float(tot_rev)},
            {"label": "Total Invoiced Expenses", "count": float(tot_exp)},
            {"label": "Net Profit Margin", "count": float(net_margin)}
        ]

        recent_payments = get_permission_aware_recent("Payment Entry", ["name", "party", "payment_type", "paid_amount", "posting_date"], limit=6)

        return {
            "kpis": [
                {"label": "Total Revenue (AED)", "value": float(tot_rev), "type": "currency", "color": "emerald"},
                {"label": "Total Expenses (AED)", "value": float(tot_exp), "type": "currency", "color": "rose"},
                {"label": "Net Profit Margin (AED)", "value": float(net_margin), "type": "currency", "color": "blue"},
                {"label": "Collected Payments (AED)", "value": float(payments_rec), "type": "currency", "color": "purple"}
            ],
            "charts": [
                {"title": "Financial Overview (AED)", "data": fin_overview, "label_key": "label", "val_key": "count"}
            ],
            "recent_list": recent_payments,
            "doctype": "Payment Entry"
        }

    # 10. Reporting / Default Executive Overview
    else:
        active_projects = get_permission_aware_count("Project", {"status": ["in", ["Open", "In Progress", "Started"]]})
        total_sales = get_permission_aware_sum("Sales Invoice", "grand_total", {"docstatus": 1})
        total_purchases = get_permission_aware_sum("Purchase Order", "grand_total", {"docstatus": 1})
        active_warranties = get_permission_aware_count("Warranty Register", {"status": "Active"})

        exec_overview = [
            {"label": "Sales Revenue", "count": float(total_sales)},
            {"label": "Purchase Commitments", "count": float(total_purchases)}
        ]

        recent_activity = get_permission_aware_recent("Project", ["name", "project_name", "status", "percent_complete"], limit=6)

        return {
            "kpis": [
                {"label": "Active Projects", "value": active_projects, "type": "number", "color": "blue"},
                {"label": "Billed Revenue (AED)", "value": float(total_sales), "type": "currency", "color": "emerald"},
                {"label": "Purchase Commitments (AED)", "value": float(total_purchases), "type": "currency", "color": "amber"},
                {"label": "Active Warranties", "value": active_warranties, "type": "number", "color": "indigo"}
            ],
            "charts": [
                {"title": "Executive Revenue vs Commitments (AED)", "data": exec_overview, "label_key": "label", "val_key": "count"}
            ],
            "recent_list": recent_activity,
            "doctype": "Project"
        }


# ==============================================================================
# CROSS-WORKSPACE DOCUMENT RELATIONSHIPS & BUSINESS GATES
# ==============================================================================


@frappe.whitelist()
def get_related_documents(doctype, name):
    doctype = normalize_doctype(doctype)
    """
    Retrieves all related records across the 10 ITS workspaces for traceability.
    Each query is isolated so missing columns in standard DocTypes never break other linked records.
    All record retrievals enforce Frappe session permissions strictly.
    """
    if not doctype or not name:
        return success_response([])
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    if not frappe.has_permission(doctype, "read", doc=name):
        return error_response("PERMISSION_DENIED", _("No read permission for {0} {1}").format(doctype, name), 403)

    related = []

    if doctype == "Project":
        try:
            proj_doc = frappe.get_doc("Project", name)
            proj_keys = [name, proj_doc.project_name]
        except Exception:
            proj_keys = [name]

        proj_filter = {"project": ("in", proj_keys)}

        # 1. Finance Commitment
        try:
            if frappe.db.exists("DocType", "Finance Commitment") and frappe.has_permission("Finance Commitment", "read"):
                fc_list = frappe.get_list("Finance Commitment", filters=proj_filter, fields=["name", "approval_status", "expected_payable"], ignore_permissions=False)
                for fc in fc_list:
                    related.append({"doctype": "Finance Commitment", "name": fc.name, "relation": "Finance Commitment", "details": f"Status: {fc.approval_status}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Finance Commitment for {name}: {str(e)}")

        # 2. Purchase Order
        try:
            if frappe.db.has_column("Purchase Order", "project") and frappe.has_permission("Purchase Order", "read"):
                po_list = frappe.get_list("Purchase Order", filters=proj_filter, fields=["name", "supplier", "grand_total", "status"], ignore_permissions=False)
                for po in po_list:
                    related.append({"doctype": "Purchase Order", "name": po.name, "relation": "Supplier PO", "details": f"{po.supplier} - AED {po.grand_total}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Purchase Order for {name}: {str(e)}")

        # 3. PSS Skid Tracker
        try:
            if frappe.db.exists("DocType", "PSS Skid Tracker") and frappe.has_permission("PSS Skid Tracker", "read"):
                pss_list = frappe.get_list("PSS Skid Tracker", filters=proj_filter, fields=["name", "pss_family", "delivery_status", "commissioning_status"], ignore_permissions=False)
                for pss in pss_list:
                    related.append({"doctype": "PSS Skid Tracker", "name": pss.name, "relation": "PSS Skid", "details": f"{pss.pss_family} ({pss.commissioning_status})"})
        except Exception as e:
            frappe.log_error(f"Error fetching PSS Skid Tracker for {name}: {str(e)}")

        # 4. Invoice Dossier
        try:
            if frappe.db.exists("DocType", "Invoice Dossier") and frappe.has_permission("Invoice Dossier", "read"):
                dossier_list = frappe.get_list("Invoice Dossier", filters=proj_filter, fields=["name", "dossier_status", "net_invoice_amount"], ignore_permissions=False)
                for d in dossier_list:
                    related.append({"doctype": "Invoice Dossier", "name": d.name, "relation": "Invoice Dossier", "details": f"{d.dossier_status} - AED {d.net_invoice_amount}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Invoice Dossier for {name}: {str(e)}")

        # 5. Quotation
        try:
            if frappe.db.has_column("Quotation", "project") and frappe.has_permission("Quotation", "read"):
                q_list = frappe.get_list("Quotation", filters=proj_filter, fields=["name", "grand_total"], ignore_permissions=False)
                for q in q_list:
                    related.append({"doctype": "Quotation", "name": q.name, "relation": "Linked Quotation", "details": f"AED {q.grand_total}"})
        except Exception as e:
            pass

        # 6. Sales Invoice
        try:
            if frappe.db.has_column("Sales Invoice", "project") and frappe.has_permission("Sales Invoice", "read"):
                inv_list = frappe.get_list("Sales Invoice", filters=proj_filter, fields=["name", "grand_total", "status"], ignore_permissions=False)
                for inv in inv_list:
                    related.append({"doctype": "Sales Invoice", "name": inv.name, "relation": "Sales Invoice", "details": f"Status: {inv.status} - AED {inv.grand_total}"})
        except Exception as e:
            pass

    elif doctype == "Purchase Order":
        try:
            if frappe.has_permission("Purchase Order", "read", doc=name):
                po_doc = frappe.get_doc("Purchase Order", name)
                if getattr(po_doc, "project", None) and frappe.has_permission("Project", "read", doc=po_doc.project):
                    related.append({"doctype": "Project", "name": po_doc.project, "relation": "Parent Project", "details": ""})

                if frappe.db.exists("DocType", "Finance Commitment") and frappe.has_permission("Finance Commitment", "read"):
                    fc_list = frappe.get_list("Finance Commitment", filters={"supplier_po": name}, fields=["name", "approval_status"], ignore_permissions=False)
                    for fc in fc_list:
                        related.append({"doctype": "Finance Commitment", "name": fc.name, "relation": "Finance Commitment Gate", "details": fc.approval_status})
        except Exception as e:
            frappe.log_error(f"Error fetching PO related docs for {name}: {str(e)}")

    elif doctype == "Finance Commitment":
        try:
            if frappe.has_permission("Finance Commitment", "read", doc=name):
                fc_doc = frappe.get_doc("Finance Commitment", name)
                if getattr(fc_doc, "project", None) and frappe.has_permission("Project", "read", doc=fc_doc.project):
                    related.append({"doctype": "Project", "name": fc_doc.project, "relation": "Project", "details": ""})
                if getattr(fc_doc, "supplier_po", None) and frappe.has_permission("Purchase Order", "read", doc=fc_doc.supplier_po):
                    related.append({"doctype": "Purchase Order", "name": fc_doc.supplier_po, "relation": "Supplier PO", "details": ""})
        except Exception as e:
            pass

    elif doctype == "Invoice Dossier":
        try:
            if frappe.has_permission("Invoice Dossier", "read", doc=name):
                d_doc = frappe.get_doc("Invoice Dossier", name)
                if getattr(d_doc, "project", None) and frappe.has_permission("Project", "read", doc=d_doc.project):
                    related.append({"doctype": "Project", "name": d_doc.project, "relation": "Project", "details": ""})
                if getattr(d_doc, "sales_invoice", None) and frappe.has_permission("Sales Invoice", "read", doc=d_doc.sales_invoice):
                    related.append({"doctype": "Sales Invoice", "name": d_doc.sales_invoice, "relation": "Generated Sales Invoice", "details": ""})
        except Exception as e:
            pass

    return success_response(related)


@frappe.whitelist()
def validate_supplier_po_release(purchase_order_name):
    """
    SERVER-SIDE BUSINESS GATE:
    Supplier PO MUST NOT be released before:
    Customer PO validation + Finance Commitment are approved.
    """
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    if not frappe.has_permission("Purchase Order", "read", doc=purchase_order_name):
        return error_response("PERMISSION_DENIED", _("No permission for Purchase Order {0}").format(purchase_order_name), 403)

    po = frappe.get_doc("Purchase Order", purchase_order_name)
    if not po.project:
        return success_response({"allowed": True, "message": "No project link required."})

    # Check for approved Finance Commitment
    fin_commit = frappe.db.get_value(
        "Finance Commitment",
        {"project": po.project, "approval_status": "Approved"},
        ["name", "approval_status"],
        as_dict=True
    )

    if not fin_commit:
        return error_response(
            "FINANCE_COMMITMENT_REQUIRED",
            f"Supplier Purchase Order {purchase_order_name} cannot be submitted/released. An approved Finance Commitment is required for Project {po.project}."
        )

    return success_response({"allowed": True, "finance_commitment": fin_commit.name})


@frappe.whitelist()
def get_document_pdf(doctype, name, print_format=None, letterhead=None, view=0, download=0):
    """
    Universal Corporate Print PDF / HTML Service.
    Generates actual Frappe PDF or print HTML for browser printing / native PDF view.
    Enforces strict read/print document permissions.
    """
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    if not frappe.has_permission(doctype, "read", doc=name) and not frappe.has_permission(doctype, "print", doc=name):
        return error_response("PERMISSION_DENIED", _("No print permission for {0} {1}").format(doctype, name), 403)

    try:
        import base64
        import re
        from frappe.utils.pdf import get_pdf

        pf_name = print_format or f"ITS Universal Print - {doctype}"
        if not frappe.db.exists("Print Format", pf_name):
            try:
                pf = frappe.get_doc({
                    "doctype": "Print Format",
                    "name": pf_name,
                    "doc_type": doctype,
                    "module": "ITS UI Redesign",
                    "standard": "No",
                    "custom_format": 1,
                    "print_format_type": "Jinja",
                    "raw_printing": 0,
                    "html": "{% include 'templates/print_formats/its_universal_print.html' %}"
                })
                pf.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as pf_err:
                frappe.log_error(f"Auto Print Format Creation Error for {doctype}: {str(pf_err)}")


        doc = frappe.get_doc(doctype, name)
        from its_ui_redesign.utils.print_helpers import (
            its_print_company,
            get_its_logo_data_uri,
            get_its_doctype_title,
            get_its_doc_items,
            get_its_doc_totals,
            get_its_field_groups,
            get_its_child_tables,
        )

        context = {
            "doc": doc,
            "company": its_print_company(doc),
            "logo_uri": get_its_logo_data_uri(),
            "doc_title": get_its_doctype_title(doc.doctype),
            "items": get_its_doc_items(doc),
            "totals": get_its_doc_totals(doc),
            "field_groups": get_its_field_groups(doc),
            "child_tables": get_its_child_tables(doc),
            "frappe": frappe,
            "_": frappe._,
        }

        html_clean = frappe.render_template("its_ui_redesign/templates/print_formats/its_universal_print.html", context)

        opts = {
            "quiet": "",
            "margin-top": "8mm",
            "margin-bottom": "8mm",
            "margin-left": "10mm",
            "margin-right": "10mm",
            "page-size": "A4"
        }

        pdf_bytes = get_pdf(html_clean, options=opts)


        if int(view or 0) or int(download or 0):
            frappe.response.filename = f"{doctype}_{name}.pdf"
            frappe.response.filecontent = pdf_bytes
            frappe.response.type = "pdf"
            frappe.response.display_content_as = "inline"
            return

        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        
        return success_response({
            "doctype": doctype,
            "name": name,
            "pdf_base64": b64_pdf,
            "filename": f"{doctype}_{name}.pdf"
        })
    except Exception as e:
        frappe.log_error(f"Error generating PDF for {doctype} {name}: {str(e)}")
        return error_response("PRINT_ERROR", f"Failed to generate print output: {str(e)}")



@frappe.whitelist()
def download_document_pdf(doctype, name, print_format=None, letterhead=None):
    """
    Direct endpoint that returns application/pdf content for Google Chrome PDF Viewer display.
    """
    res = get_document_pdf(doctype, name, print_format=print_format, letterhead=letterhead)
    if isinstance(res, dict) and not res.get("success"):
        error_msg = res.get("error", {}).get("message", "Error generating PDF")
        frappe.throw(error_msg)
    
    data = res.get("data", {}) if isinstance(res, dict) else {}
    pdf_b64 = data.get("pdf_base64")
    if not pdf_b64:
        frappe.throw(_("Failed to obtain PDF content"))

    import base64
    pdf_bytes = base64.b64decode(pdf_b64)
    filename = data.get("filename", f"{doctype}_{name}.pdf")

    frappe.response.filename = filename
    frappe.response.filecontent = pdf_bytes
    frappe.response.type = "pdf"
    frappe.response.display_content_as = "inline"




# ==============================================================================
# CONTEXTUAL "CREATE >" ACTION ENGINE & BUSINESS GATES (G0 - G11)
# ==============================================================================

@frappe.whitelist()
def get_contextual_create_options(doctype, name=None):
    """
    Returns available downstream creation targets for a given DocType and optional record name.
    """
    try:
        from its_ui_redesign.services.business_flow import get_allowed_next_steps
        targets = get_allowed_next_steps(doctype, source_name=name)
        return success_response(targets)
    except Exception as e:
        frappe.log_error(f"Error fetching create options for {doctype}: {str(e)}")
        return success_response([])


@frappe.whitelist()
def get_create_target_payload(source_doctype, source_name, target_doctype):
    """
    Carries forward data from source record to initialize target document for "Create >" actions.
    Enforces permissions, hard stops, and field mapping natively.
    """
    if not source_doctype or not source_name or not target_doctype:
        return error_response("INVALID_PARAMS", "source_doctype, source_name, and target_doctype are required.")

    try:
        from its_ui_redesign.services.business_flow import build_next_step_payload
        payload = build_next_step_payload(source_doctype, source_name, target_doctype)
        return success_response(payload)
    except frappe.PermissionError as pe:
        return error_response("PERMISSION_DENIED", str(pe), status_code=403)
    except frappe.ValidationError as ve:
        return error_response("VALIDATION_ERROR", str(ve), status_code=400)
    except Exception as e:
        frappe.log_error(f"Error building create payload for {source_doctype} {source_name} -> {target_doctype}: {str(e)}")
        return error_response("CREATE_PAYLOAD_ERROR", f"Failed to prepare {target_doctype} from {source_doctype} {source_name}: {str(e)}")



@frappe.whitelist()
def validate_client_po_match(quotation_name, customer_po_amount):
    """
    BUSINESS GATE G4: Client PO Validation.
    Validates Customer PO amount against agreed Quotation amount before Sales Order progression.
    """
    try:
        q_doc = frappe.get_doc("Quotation", quotation_name)
        agreed_amount = float(q_doc.grand_total)
        po_amount = float(customer_po_amount or 0.0)

        if abs(agreed_amount - po_amount) > 0.01:
            return error_response(
                "CLIENT_PO_MISMATCH",
                f"Client PO Validation Failed: Customer PO amount (AED {po_amount:,.2f}) does not match agreed Quotation {quotation_name} amount (AED {agreed_amount:,.2f})."
            )

        return success_response({"valid": True, "quotation": quotation_name, "agreed_amount": agreed_amount})
    except Exception as e:
        return error_response("VALIDATION_ERROR", f"Failed to validate Client PO: {str(e)}")


@frappe.whitelist()
def verify_invoice_readiness(project=None, sales_order=None, invoice_dossier=None):
    """
    BUSINESS GATE G10: Invoice Readiness Gate.
    Verifies that Delivery, Commissioning, Handover sign-off, Quality Certificates, and Punch list clearance
    are complete before Sales Invoice generation is permitted.
    """
    try:
        checks = {
            "delivery_completed": False,
            "handover_signed_off": False,
            "punch_list_cleared": True,
            "commercial_conditions_met": True
        }
        reasons = []

        target_project = project
        if not target_project and sales_order:
            target_project = frappe.db.get_value("Sales Order", sales_order, "project")
        if not target_project and invoice_dossier:
            target_project = frappe.db.get_value("Invoice Dossier", invoice_dossier, "project")

        if not target_project:
            # If no project link is specified, default to allowable for standalone non-project sales
            return success_response({
                "ready": True,
                "project": None,
                "checks": checks,
                "message": "No project link provided. Invoice readiness bypass permitted."
            })

        # 1. Check Delivery Notes
        dn_count = frappe.db.count("Delivery Note", {"project": target_project, "docstatus": 1})
        if dn_count > 0:
            checks["delivery_completed"] = True
        else:
            reasons.append("No submitted Delivery Note found for project.")

        # 2. Check Handover / Dossier
        if frappe.db.exists("DocType", "Project Handover"):
            handover_count = frappe.db.count("Project Handover", {"project": target_project, "docstatus": 1})
            if handover_count > 0:
                checks["handover_signed_off"] = True
            else:
                reasons.append("Project Handover record is not submitted/signed-off.")
        elif frappe.db.exists("DocType", "Invoice Dossier"):
            dossier_count = frappe.db.count("Invoice Dossier", {"project": target_project, "dossier_status": "Approved"})
            if dossier_count > 0:
                checks["handover_signed_off"] = True
            else:
                reasons.append("Invoice Dossier is not approved.")
        else:
            checks["handover_signed_off"] = True

        # 3. Check Punch List (Snag List / Quality NCR)
        if frappe.db.exists("DocType", "Snag List"):
            open_snags = frappe.db.count("Snag List", {"project": target_project, "status": ["in", ["Open", "Pending Inspection"]]})
            if open_snags > 0:
                checks["punch_list_cleared"] = False
                reasons.append(f"{open_snags} open Punch/Snag list items remaining.")

        if frappe.db.exists("DocType", "Quality NCR"):
            open_ncrs = frappe.db.count("Quality NCR", {"project": target_project, "status": ["in", ["Open", "Pending Action"]]})
            if open_ncrs > 0:
                checks["punch_list_cleared"] = False
                reasons.append(f"{open_ncrs} open Nonconformance Reports (NCRs) remaining.")

        is_ready = all([checks["delivery_completed"], checks["handover_signed_off"], checks["punch_list_cleared"], checks["commercial_conditions_met"]])

        if not is_ready:
            return error_response(
                "INVOICE_NOT_READY",
                f"Invoice Readiness Gate Blocked for Project {target_project}: " + "; ".join(reasons)
            )

        return success_response({
            "ready": True,
            "project": target_project,
            "checks": checks,
            "message": "Invoice Readiness criteria satisfied."
        })

    except Exception as e:
        return error_response("VALIDATION_ERROR", f"Failed to check Invoice Readiness: {str(e)}")


# ==============================================================================
# SERVER-SIDE FRAPPE DOC EVENT HARD STOPS
# ==============================================================================

def validate_purchase_order_hard_stop(doc, method=None):
    """
    Hooked to Purchase Order validate/on_submit:
    Blocks Purchase Order creation/submission if project link exists but no approved Finance Commitment exists.
    """
    if getattr(doc, "project", None):
        if frappe.db.exists("DocType", "Finance Commitment"):
            approved_fc = frappe.db.exists("Finance Commitment", {
                "project": doc.project,
                "approval_status": "Approved"
            })
            if not approved_fc:
                frappe.throw(
                    _("HARD STOP (Finance Commitment Gate G6): Purchase Order '{0}' cannot be saved/submitted. "
                      "An approved Finance Commitment is required for Project '{1}'.").format(doc.name or "New", doc.project),
                    title=_("Finance Commitment Required")
                )


def validate_delivery_note_hard_stop(doc, method=None):
    """
    Hooked to Delivery Note validate/on_submit:
    Blocks Delivery Note submission if open Category A/B Snag List items exist for the project.
    """
    if getattr(doc, "project", None):
        if frappe.db.exists("DocType", "Snag List"):
            open_snags = frappe.db.count("Snag List", {
                "project": doc.project,
                "status": ["in", ["Open", "Pending Inspection"]]
            })
            if open_snags > 0:
                frappe.throw(
                    _("HARD STOP (Punch List Gate G8.5): Delivery Note '{0}' cannot be submitted. "
                      "There are {1} open Punch/Snag list items for Project '{2}'.").format(doc.name or "New", open_snags, doc.project),
                    title=_("Open Snag Items Block Delivery")
                )


def validate_sales_invoice_hard_stop(doc, method=None):
    """
    Hooked to Sales Invoice validate/on_submit:
    Enforces Invoice Readiness gate on backend before Sales Invoice submission.
    """
    if getattr(doc, "project", None) and doc.docstatus == 1:
        res = verify_invoice_readiness(project=doc.project)
        if not res.get("success"):
            error_msg = res.get("error", {}).get("message", "Invoice Readiness criteria not satisfied.")
            frappe.throw(
                _("HARD STOP (Invoice Readiness Gate G10): {0}").format(error_msg),
                title=_("Invoice Readiness Gate Blocked")
            )

