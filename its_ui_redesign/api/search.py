import frappe
from frappe import _

SYNONYMS = {
    "fat": ["Factory Acceptance Test"],
    "ifat": ["Integrated Factory Acceptance Test"],
    "po": ["Purchase Order"],
    "so": ["Sales Order"],
    "rfi": ["Request for Information"],
    "si": ["Sales Invoice"],
    "pi": ["Purchase Invoice"],
    "pr": ["Purchase Receipt", "Material Request"],
    "dn": ["Delivery Note"],
    "boq": ["BOQ"],
    "ncr": ["Nonconformance Report"],
    "wbs": ["Task"]
}

@frappe.whitelist()
def global_search(query=""):
    """
    Production-grade permission-aware global search API for ITS Project Operations Portal.
    Discovers DocTypes, Actions, Documents, and Reports with strict Frappe session permissions.
    """
    if frappe.session.user == "Guest":
        return {
            "doctypes": [],
            "actions": [],
            "documents": [],
            "reports": []
        }

    query = (query or "").strip()
    if not query or len(query) < 2:
        return {
            "doctypes": [],
            "actions": [],
            "documents": [],
            "reports": []
        }

    query_lower = query.lower()

    results = {
        "doctypes": [],
        "actions": [],
        "documents": [],
        "reports": []
    }

    synonym_target_dts = SYNONYMS.get(query_lower, [])

    # 1. Accessible DocTypes
    try:
        all_doctypes = frappe.get_all(
            "DocType",
            filters={
                "issingle": 0,
                "istable": 0,
                "is_virtual": 0
            },
            fields=["name", "module", "custom", "is_submittable"]
        )

        for dt_info in all_doctypes:
            dt_name = dt_info["name"]
            
            # Match query against DocType name or Synonyms
            matches_name = query_lower in dt_name.lower()
            matches_synonym = dt_name in synonym_target_dts

            if matches_name or matches_synonym:
                # Permission check
                if not frappe.has_permission(dt_name, "read"):
                    continue

                has_create = frappe.has_permission(dt_name, "create")

                results["doctypes"].append({
                    "doctype": dt_name,
                    "label": dt_name,
                    "module": dt_info["module"],
                    "custom": dt_info["custom"],
                    "can_create": has_create
                })

                if has_create and len(results["actions"]) < 5:
                    results["actions"].append({
                        "doctype": dt_name,
                        "label": f"New {dt_name}",
                        "action": "new",
                        "module": dt_info["module"]
                    })

                if len(results["doctypes"]) >= 8:
                    break
    except Exception as e:
        frappe.log_error(f"Global search doctype discovery error: {str(e)}")

    # 2. Search Existing Documents across Priority / Matched DocTypes
    target_doctypes = [d["doctype"] for d in results["doctypes"]]
    
    priority_defaults = [
        "Project", "Sales Order", "Purchase Order", "Sales Invoice", "Purchase Invoice",
        "Factory Acceptance Test", "Integrated Factory Acceptance Test", "Finance Commitment",
        "Invoice Dossier", "Snag List", "Customer", "Supplier", "Item", "Work Order",
        "BOQ", "Request for Information", "Technical Submittal", "Project Contract",
        "Project Variation", "Project Warranty", "Subcontract Agreement", "Subcontract Progress Claim"
    ]

    for p_dt in priority_defaults:
        if p_dt not in target_doctypes and frappe.db.exists("DocType", p_dt) and frappe.has_permission(p_dt, "read"):
            target_doctypes.append(p_dt)

    doc_results = []
    
    for dt in target_doctypes[:10]:
        try:
            meta = frappe.get_meta(dt)
            title_field = meta.title_field or "name"
            
            # Use frappe.get_list with OR filters to enforce permissions strictly
            or_filters = {
                "name": ["like", f"%{query}%"]
            }
            if title_field != "name":
                or_filters[title_field] = ["like", f"%{query}%"]

            fields = ["name", "modified", "docstatus"]
            if title_field != "name" and title_field not in fields:
                fields.append(title_field)
            
            meta_fieldnames = [f.fieldname for f in meta.fields]
            if "status" in meta_fieldnames:
                fields.append("status")
            if "project" in meta_fieldnames:
                fields.append("project")

            records = frappe.get_list(
                dt,
                or_filters=or_filters,
                fields=fields,
                limit_page_length=5,
                ignore_permissions=False
            )

            for r in records:
                disp_title = r.get(title_field) or r.get("name")
                status_val = r.get("status")
                if status_val is None:
                    docstatus = r.get("docstatus")
                    if docstatus == 0:
                        status_val = "Draft"
                    elif docstatus == 1:
                        status_val = "Submitted"
                    elif docstatus == 2:
                        status_val = "Cancelled"

                doc_results.append({
                    "doctype": dt,
                    "name": r.get("name"),
                    "title": str(disp_title),
                    "status": status_val,
                    "project": r.get("project"),
                    "modified": str(r.get("modified"))
                })

                if len(doc_results) >= 12:
                    break
        except Exception:
            continue

        if len(doc_results) >= 12:
            break

    results["documents"] = doc_results[:12]

    # 3. Search Reports
    try:
        reports = frappe.get_list(
            "Report",
            filters={"disabled": 0, "report_name": ["like", f"%{query}%"]},
            fields=["name", "report_name", "ref_doctype"],
            limit_page_length=5,
            ignore_permissions=False
        )
        for rep in reports:
            ref_dt = rep.get("ref_doctype")
            if not ref_dt or frappe.has_permission(ref_dt, "read"):
                results["reports"].append({
                    "name": rep.get("name"),
                    "label": rep.get("report_name"),
                    "ref_doctype": ref_dt
                })
    except Exception:
        pass

    return results
