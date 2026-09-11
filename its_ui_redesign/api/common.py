import frappe
import json
from frappe import _

STANDARD_DOC_FIELDS = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}

def success_response(data, meta=None):
    res = {"success": True, "data": data}
    if meta is not None:
        res["meta"] = meta
    return res

def error_response(code, message, status_code=400):
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
        search_fields = ["name"]
        if meta.title_field and meta.has_field(meta.title_field):
            search_fields.append(meta.title_field)
        if meta.has_field("description"):
            search_fields.append("description")
        
        or_filters = [[doctype, field, "like", f"%{search_text}%"] for field in search_fields if meta.has_field(field) or field == "name"]
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

        total_count = frappe.db.count(doctype, filters=filters)

        return success_response(items, {
            "total": total_count,
            "page": page,
            "page_length": page_length,
            "has_next": (start + len(items)) < total_count,
            "title_field": meta.title_field or "name",
            "status_field": "status" if meta.has_field("status") else ("disabled" if meta.has_field("disabled") else None),
            "is_tree": meta.is_tree,
            "is_submittable": meta.is_submittable
        })
    except Exception as e:
        frappe.log_error(f"Error fetching {doctype} list: {str(e)}")
        return error_response("FETCH_ERROR", str(e), 500)

@frappe.whitelist()
def get_document_detail(doctype, name):
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
            if frappe.db.exists("DocType", rel_doctype) and frappe.has_permission(rel_doctype, "read"):
                count = frappe.db.count(rel_doctype, filters={rel_field: name})
                if count > 0:
                    rel_meta = frappe.get_meta(rel_doctype)
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
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if isinstance(doc_data, str):
        doc_data = json.loads(doc_data)

    name = doc_data.get("name")
    is_new = not name or doc_data.get("__islocal")

    perm_type = "create" if is_new else "write"
    if not frappe.has_permission(doctype, perm_type, doc=name if not is_new else None):
        return error_response("PERMISSION_DENIED", _("No {0} permission for {1}").format(perm_type, doctype), 403)

    try:
        if is_new:
            doc_data["doctype"] = doctype
            doc = frappe.get_doc(doc_data)
            doc.insert(ignore_permissions=False)
        else:
            doc = frappe.get_doc(doctype, name)
            doc.update(doc_data)
            doc.save(ignore_permissions=False)

        return success_response(doc.as_dict())
    except frappe.ValidationError as e:
        return error_response("VALIDATION_ERROR", str(e), 422)
    except frappe.MandatoryError as e:
        return error_response("MANDATORY_ERROR", str(e), 422)
    except frappe.PermissionError as e:
        return error_response("PERMISSION_DENIED", str(e), 403)
    except Exception as e:
        frappe.log_error(f"Error saving {doctype}: {str(e)}")
        return error_response("SAVE_ERROR", str(e), 500)

@frappe.whitelist()
def submit_document(doctype, name):
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
def get_doctype_meta(doctype):
    if frappe.session.user == "Guest":
        return error_response("UNAUTHENTICATED", _("Authentication required"), 401)
    
    if not frappe.has_permission(doctype, "read"):
        return error_response("PERMISSION_DENIED", _("No read permission for {0}").format(doctype), 403)

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} does not exist").format(doctype), 404)

    meta = frappe.get_meta(doctype)
    fields = []
    list_fields = []

    for f in meta.fields:
        if not f.hidden and f.fieldtype not in ["HTML", "Heading"]:
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
                "depends_on": f.depends_on,
                "mandatory_depends_on": f.mandatory_depends_on,
                "read_only_depends_on": f.read_only_depends_on
            }

            # If fieldtype is Table (child table), attach child fields metadata
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
                list_fields.append({"key": f.fieldname, "label": f.label, "fieldtype": f.fieldtype})

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

    workflow_name = frappe.model.workflow.get_workflow_name(doctype)

    return success_response({
        "name": meta.name,
        "module": meta.module,
        "title_field": meta.title_field or "name",
        "status_field": "status" if meta.has_field("status") else ("disabled" if meta.has_field("disabled") else None),
        "is_submittable": meta.is_submittable,
        "is_tree": meta.is_tree,
        "parent_field": f"parent_{meta.name.lower().replace(' ', '_')}" if meta.is_tree else None,
        "has_workflow": bool(workflow_name),
        "workflow_name": workflow_name,
        "fields": fields,
        "list_fields": list_fields
    })


@frappe.whitelist()

@frappe.whitelist()

@frappe.whitelist()

@frappe.whitelist()
def get_workspace_dashboard(workspace_id, company=None, project=None, from_date=None, to_date=None):
    """
    Returns live ERPNext/Frappe aggregated KPIs, status distributions,
    trend charts, and record lists for the specified workspace.
    Zero mock numbers. All values are calculated from real backend records.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)

    ws = (workspace_id or "").lower().strip()

    # 1. Project Management
    if ws == "01-project-management" or "project" in ws:
        active_projects = frappe.db.count("Project", filters={"status": ["in", ["Open", "In Progress", "Started"]]}) or 0
        completed_projects = frappe.db.count("Project", filters={"status": ["in", ["Completed", "Closed"]]}) or 0
        open_rfis = frappe.db.count("Project RFI", filters={"status": ["in", ["Open", "Pending Response"]]}) if frappe.db.exists("DocType", "Project RFI") else 0
        open_issues = frappe.db.count("Issue", filters={"status": ["in", ["Open", "Replied"]]}) or 0
        open_variations = frappe.db.count("Project Variation", filters={"status": ["in", ["Draft", "Pending Review"]]}) if frappe.db.exists("DocType", "Project Variation") else 0
        open_ncrs = frappe.db.count("Quality NCR", filters={"status": ["in", ["Open", "Under Rectification"]]}) if frappe.db.exists("DocType", "Quality NCR") else 0
        
        status_counts = frappe.db.sql("SELECT status, COUNT(name) as count FROM `tabProject` GROUP BY status", as_dict=True)
        recent_projects = frappe.get_all("Project", fields=["name", "project_name", "status", "percent_complete", "estimated_costing"], order_by="modified desc", limit=6)

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
        active_estimates = frappe.db.count("Project Variation", filters={"status": "Draft"}) if frappe.db.exists("DocType", "Project Variation") else 0
        sales_orders_val = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Order` WHERE docstatus=1")[0][0] or 0.0
        actual_cost = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Invoice` WHERE docstatus=1")[0][0] or 0.0
        var_cost = 0.0
        if frappe.db.exists("DocType", "Project Variation"):
            var_res = frappe.db.sql("SELECT SUM(cost_impact) FROM `tabProject Variation` WHERE status='Approved'")[0][0]
            var_cost = float(var_res or 0)

        cost_breakdown = [
            {"label": "Contract Sales Value", "count": float(sales_orders_val)},
            {"label": "Actual Invoiced Cost", "count": float(actual_cost)},
            {"label": "Approved Variations", "count": float(var_cost)}
        ]

        recent_variations = frappe.get_all("Project Variation", fields=["name", "title", "project", "cost_impact", "status"], order_by="modified desc", limit=6) if frappe.db.exists("DocType", "Project Variation") else []

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
        total_tasks = frappe.db.count("Task") or 0
        open_tasks = frappe.db.count("Task", filters={"status": ["in", ["Open", "Working"]]}) or 0
        completed_tasks = frappe.db.count("Task", filters={"status": "Completed"}) or 0
        overdue_tasks = frappe.db.count("Task", filters={"status": "Overdue"}) or 0

        task_status = frappe.db.sql("SELECT status, COUNT(name) as count FROM `tabTask` GROUP BY status", as_dict=True)
        recent_tasks = frappe.get_all("Task", fields=["name", "subject", "project", "status", "priority"], order_by="modified desc", limit=6)

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
        total_pos = frappe.db.count("Purchase Order") or 0
        open_pos = frappe.db.count("Purchase Order", filters={"status": ["in", ["To Receive and Bill", "Draft"]]}) or 0
        po_val = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Order` WHERE docstatus=1")[0][0] or 0.0
        subcontract_claims_val = frappe.db.sql("SELECT SUM(total_claimed) FROM `tabSubcontract Progress Claim` WHERE docstatus=1")[0][0] if frappe.db.exists("DocType", "Subcontract Progress Claim") else 0.0

        po_status = frappe.db.sql("SELECT status, COUNT(name) as count FROM `tabPurchase Order` GROUP BY status", as_dict=True)
        recent_pos = frappe.get_all("Purchase Order", fields=["name", "supplier", "grand_total", "status", "transaction_date"], order_by="modified desc", limit=6)

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
        total_items = frappe.db.count("Item") or 0
        total_warehouses = frappe.db.count("Warehouse") or 0
        stock_val_res = frappe.db.sql("SELECT SUM(stock_value) FROM `tabBin`")[0][0] or 0.0
        stock_receipts = frappe.db.count("Purchase Receipt", filters={"docstatus": 1}) or 0

        warehouse_val = frappe.db.sql("SELECT warehouse as status, SUM(stock_value) as count FROM `tabBin` WHERE stock_value > 0 GROUP BY warehouse LIMIT 5", as_dict=True)
        recent_receipts = frappe.get_all("Purchase Receipt", fields=["name", "supplier", "grand_total", "status", "posting_date"], order_by="modified desc", limit=6)

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
        total_emp = frappe.db.count("Employee", filters={"status": "Active"}) or 0
        attendance_today = frappe.db.count("Attendance", filters={"attendance_date": frappe.utils.today(), "status": "Present"}) or 0
        open_leaves = frappe.db.count("Leave Application", filters={"status": "Open"}) or 0
        total_timesheets = frappe.db.count("Timesheet", filters={"docstatus": 1}) or 0

        dept_dist = frappe.db.sql("SELECT department as status, COUNT(name) as count FROM `tabEmployee` WHERE status='Active' AND department IS NOT NULL GROUP BY department LIMIT 5", as_dict=True)
        recent_employees = frappe.get_all("Employee", fields=["name", "employee_name", "designation", "department", "status"], order_by="modified desc", limit=6)

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
        work_orders = frappe.db.count("Work Order") or 0
        in_process_wo = frappe.db.count("Work Order", filters={"status": "In Process"}) or 0
        total_assets = frappe.db.count("Asset") or 0
        in_use_assets = frappe.db.count("Asset", filters={"status": "Submitted"}) or 0

        wo_status = frappe.db.sql("SELECT status, COUNT(name) as count FROM `tabWork Order` GROUP BY status", as_dict=True)
        recent_work_orders = frappe.get_all("Work Order", fields=["name", "production_item", "qty", "status", "planned_start_date"], order_by="modified desc", limit=6)

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
        total_invoices = frappe.db.count("Sales Invoice") or 0
        total_billed_res = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE docstatus=1")[0][0] or 0.0
        outstanding_res = frappe.db.sql("SELECT SUM(outstanding_amount) FROM `tabSales Invoice` WHERE docstatus=1 AND outstanding_amount > 0")[0][0] or 0.0
        site_measurements = frappe.db.count("Site Measurement", filters={"docstatus": 1}) if frappe.db.exists("DocType", "Site Measurement") else 0

        inv_status = frappe.db.sql("SELECT status, COUNT(name) as count FROM `tabSales Invoice` GROUP BY status", as_dict=True)
        recent_invoices = frappe.get_all("Sales Invoice", fields=["name", "customer", "grand_total", "outstanding_amount", "status"], order_by="modified desc", limit=6)

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
        tot_rev = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE docstatus=1")[0][0] or 0.0
        tot_exp = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Invoice` WHERE docstatus=1")[0][0] or 0.0
        net_margin = float(tot_rev) - float(tot_exp)
        payments_rec = frappe.db.sql("SELECT SUM(paid_amount) FROM `tabPayment Entry` WHERE docstatus=1 AND payment_type='Receive'")[0][0] or 0.0

        fin_overview = [
            {"label": "Total Revenue", "count": float(tot_rev)},
            {"label": "Total Invoiced Expenses", "count": float(tot_exp)},
            {"label": "Net Profit Margin", "count": float(net_margin)}
        ]

        recent_payments = frappe.get_all("Payment Entry", fields=["name", "party", "payment_type", "paid_amount", "posting_date"], order_by="modified desc", limit=6)

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
        active_projects = frappe.db.count("Project", filters={"status": ["in", ["Open", "In Progress", "Started"]]}) or 0
        total_sales = frappe.db.sql("SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE docstatus=1")[0][0] or 0.0
        total_purchases = frappe.db.sql("SELECT SUM(grand_total) FROM `tabPurchase Order` WHERE docstatus=1")[0][0] or 0.0
        active_warranties = frappe.db.count("Warranty Register", filters={"status": "Active"}) if frappe.db.exists("DocType", "Warranty Register") else 0

        exec_overview = [
            {"label": "Sales Revenue", "count": float(total_sales)},
            {"label": "Purchase Commitments", "count": float(total_purchases)}
        ]

        recent_activity = frappe.get_all("Project", fields=["name", "project_name", "status", "percent_complete"], order_by="modified desc", limit=6)

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
    """
    Retrieves all related records across the 10 ITS workspaces for traceability.
    Each query is isolated so missing columns in standard DocTypes never break other linked records.
    """
    if not doctype or not name:
        return success_response([])

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
            if frappe.db.exists("DocType", "Finance Commitment"):
                fc_list = frappe.get_all("Finance Commitment", filters=proj_filter, fields=["name", "approval_status", "expected_payable"])
                for fc in fc_list:
                    related.append({"doctype": "Finance Commitment", "name": fc.name, "relation": "Finance Commitment", "details": f"Status: {fc.approval_status}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Finance Commitment for {name}: {str(e)}")

        # 2. Purchase Order
        try:
            if frappe.db.has_column("Purchase Order", "project"):
                po_list = frappe.get_all("Purchase Order", filters=proj_filter, fields=["name", "supplier", "grand_total", "status"])
                for po in po_list:
                    related.append({"doctype": "Purchase Order", "name": po.name, "relation": "Supplier PO", "details": f"{po.supplier} - AED {po.grand_total}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Purchase Order for {name}: {str(e)}")

        # 3. PSS Skid Tracker
        try:
            if frappe.db.exists("DocType", "PSS Skid Tracker"):
                pss_list = frappe.get_all("PSS Skid Tracker", filters=proj_filter, fields=["name", "pss_family", "delivery_status", "commissioning_status"])
                for pss in pss_list:
                    related.append({"doctype": "PSS Skid Tracker", "name": pss.name, "relation": "PSS Skid", "details": f"{pss.pss_family} ({pss.commissioning_status})"})
        except Exception as e:
            frappe.log_error(f"Error fetching PSS Skid Tracker for {name}: {str(e)}")

        # 4. Invoice Dossier
        try:
            if frappe.db.exists("DocType", "Invoice Dossier"):
                dossier_list = frappe.get_all("Invoice Dossier", filters=proj_filter, fields=["name", "dossier_status", "net_invoice_amount"])
                for d in dossier_list:
                    related.append({"doctype": "Invoice Dossier", "name": d.name, "relation": "Invoice Dossier", "details": f"{d.dossier_status} - AED {d.net_invoice_amount}"})
        except Exception as e:
            frappe.log_error(f"Error fetching Invoice Dossier for {name}: {str(e)}")

        # 5. Quotation
        try:
            if frappe.db.has_column("Quotation", "project"):
                q_list = frappe.get_all("Quotation", filters=proj_filter, fields=["name", "grand_total"])
                for q in q_list:
                    related.append({"doctype": "Quotation", "name": q.name, "relation": "Linked Quotation", "details": f"AED {q.grand_total}"})
        except Exception as e:
            pass

        # 6. Sales Invoice
        try:
            if frappe.db.has_column("Sales Invoice", "project"):
                inv_list = frappe.get_all("Sales Invoice", filters=proj_filter, fields=["name", "grand_total", "status"])
                for inv in inv_list:
                    related.append({"doctype": "Sales Invoice", "name": inv.name, "relation": "Sales Invoice", "details": f"Status: {inv.status} - AED {inv.grand_total}"})
        except Exception as e:
            pass

    elif doctype == "Purchase Order":
        try:
            po_doc = frappe.get_doc("Purchase Order", name)
            if getattr(po_doc, "project", None):
                related.append({"doctype": "Project", "name": po_doc.project, "relation": "Parent Project", "details": ""})

            if frappe.db.exists("DocType", "Finance Commitment"):
                fc_list = frappe.get_all("Finance Commitment", filters={"supplier_po": name}, fields=["name", "approval_status"])
                for fc in fc_list:
                    related.append({"doctype": "Finance Commitment", "name": fc.name, "relation": "Finance Commitment Gate", "details": fc.approval_status})
        except Exception as e:
            frappe.log_error(f"Error fetching PO related docs for {name}: {str(e)}")

    elif doctype == "Finance Commitment":
        try:
            fc_doc = frappe.get_doc("Finance Commitment", name)
            if getattr(fc_doc, "project", None):
                related.append({"doctype": "Project", "name": fc_doc.project, "relation": "Project", "details": ""})
            if getattr(fc_doc, "supplier_po", None):
                related.append({"doctype": "Purchase Order", "name": fc_doc.supplier_po, "relation": "Supplier PO", "details": ""})
        except Exception as e:
            pass

    elif doctype == "Invoice Dossier":
        try:
            d_doc = frappe.get_doc("Invoice Dossier", name)
            if getattr(d_doc, "project", None):
                related.append({"doctype": "Project", "name": d_doc.project, "relation": "Project", "details": ""})
            if getattr(d_doc, "sales_invoice", None):
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
def get_document_pdf(doctype, name, print_format=None, letterhead=None):
    """
    Universal Corporate Print PDF / HTML Service.
    Generates actual Frappe PDF or print HTML for browser printing / native PDF view.
    """
    try:
        import base64
        try:
            pdf_bytes = frappe.get_print(
                doctype=doctype,
                name=name,
                print_format=print_format,
                letterhead=letterhead,
                as_pdf=True
            )
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            return success_response({
                "doctype": doctype,
                "name": name,
                "pdf_base64": b64_pdf,
                "is_html": False,
                "filename": f"{doctype}_{name}.pdf"
            })
        except Exception as pdf_err:
            # Fallback to rendered corporate HTML print format for native browser printing
            html = frappe.get_print(
                doctype=doctype,
                name=name,
                print_format=print_format,
                letterhead=letterhead,
                as_pdf=False
            )
            b64_html = base64.b64encode(html.encode("utf-8")).decode("utf-8")
            return success_response({
                "doctype": doctype,
                "name": name,
                "html_base64": b64_html,
                "is_html": True,
                "filename": f"{doctype}_{name}.html"
            })
    except Exception as e:
        return error_response("PRINT_ERROR", f"Failed to generate print output: {str(e)}")


# ==============================================================================
# CONTEXTUAL "CREATE >" ACTION ENGINE & BUSINESS GATES (G0 - G11)
# ==============================================================================

@frappe.whitelist()
def get_contextual_create_options(doctype):
    """
    Returns available downstream creation targets for a given DocType.
    """
    mapping = {
        "Opportunity": ["Quotation", "Project"],
        "Quotation": ["Sales Order", "Finance Commitment", "Project"],
        "Sales Order": ["Finance Commitment", "Delivery Note"],
        "Finance Commitment": ["Purchase Order"],
        "Purchase Order": ["PSS Skid Tracker", "Purchase Receipt"],
        "PSS Skid Tracker": ["Invoice Dossier", "Quality NCR"],
        "Invoice Dossier": ["Sales Invoice"],
        "Delivery Note": ["Invoice Dossier", "Sales Invoice"],
        "Project": ["Project Task", "Finance Commitment", "PSS Skid Tracker", "Invoice Dossier"]
    }
    targets = mapping.get(doctype, [])
    return success_response(targets)


@frappe.whitelist()
def get_create_target_payload(source_doctype, source_name, target_doctype):
    """
    Carries forward data from source record to initialize target document for "Create >" actions.
    """
    if not source_doctype or not source_name or not target_doctype:
        return error_response("INVALID_PARAMS", "source_doctype, source_name, and target_doctype are required.")

    try:
        source_doc = frappe.get_doc(source_doctype, source_name)
        payload = {}

        # 1. Quotation -> Sales Order / Contract / Finance Commitment / Project
        if source_doctype == "Quotation":
            payload["customer"] = getattr(source_doc, "party_name", None) or getattr(source_doc, "customer", None)
            payload["project"] = getattr(source_doc, "project", None)
            payload["company"] = getattr(source_doc, "company", None)
            payload["currency"] = getattr(source_doc, "currency", "AED")
            if target_doctype == "Finance Commitment":
                payload["expected_payable"] = getattr(source_doc, "grand_total", 0.0)

        # 2. Sales Order -> Finance Commitment / Delivery Note
        elif source_doctype == "Sales Order":
            payload["customer"] = getattr(source_doc, "customer", None)
            payload["project"] = getattr(source_doc, "project", None)
            payload["company"] = getattr(source_doc, "company", None)
            payload["customer_po"] = getattr(source_doc, "po_no", None)
            if target_doctype == "Finance Commitment":
                payload["expected_payable"] = getattr(source_doc, "grand_total", 0.0)

        # 3. Finance Commitment -> Purchase Order
        elif source_doctype == "Finance Commitment":
            payload["supplier"] = getattr(source_doc, "supplier", None)
            payload["project"] = getattr(source_doc, "project", None)
            payload["company"] = frappe.db.get_value("Company", {}) or "ITS"
            payload["schedule_date"] = frappe.utils.nowdate()

        # 4. Purchase Order -> PSS Skid Tracker / Purchase Receipt
        elif source_doctype == "Purchase Order":
            payload["supplier"] = getattr(source_doc, "supplier", None)
            payload["project"] = getattr(source_doc, "project", None)
            payload["supplier_po"] = source_doc.name
            payload["company"] = getattr(source_doc, "company", None)

        # 5. PSS Skid Tracker -> Invoice Dossier
        elif source_doctype == "PSS Skid Tracker":
            payload["project"] = getattr(source_doc, "project", None)
            payload["customer"] = getattr(source_doc, "customer", None)
            payload["customer_po"] = getattr(source_doc, "customer_po", None)
            payload["punch_list_clearance"] = 1 if getattr(source_doc, "punch_closure_status", "") == "Closed" else 0

        # 6. Invoice Dossier -> Sales Invoice
        elif source_doctype == "Invoice Dossier":
            payload["customer"] = getattr(source_doc, "customer", None)
            payload["project"] = getattr(source_doc, "project", None)
            payload["company"] = frappe.db.get_value("Company", {}) or "ITS"
            payload["grand_total"] = getattr(source_doc, "net_invoice_amount", 0.0)

        # 7. Project -> Any
        elif source_doctype == "Project":
            payload["project"] = source_doc.name
            payload["customer"] = getattr(source_doc, "customer", None)
            payload["company"] = getattr(source_doc, "company", None)

        return success_response(payload)

    except Exception as e:
        return error_response("CREATE_PAYLOAD_ERROR", f"Failed to build payload from {source_doctype} {source_name}: {str(e)}")


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
