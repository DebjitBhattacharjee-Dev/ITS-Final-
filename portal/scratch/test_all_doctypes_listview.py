import frappe
import json

def test_all_doctypes_listview():
    frappe.set_user("Administrator")
    print("=== DISCOVERING ALL PORTAL WORKSPACE DOCTYPES ===")

    # Load navigation config
    nav_file = '/home/frappe/frappe-bench/apps/its_ui_redesign/portal/src/config/navigation.js'
    with open(nav_file, 'r') as f:
        text = f.read()

    start_tag = 'export const WORKSPACES = ['
    start = text.find(start_tag)
    json_str = text[start + len('export const WORKSPACES = '):]
    end = json_str.find(';\n\nexport function getWorkspaceById')
    json_str = json_str[:end]
    workspaces = json.loads(json_str)

    results = []
    seen_doctypes = set()

    for ws in workspaces:
        ws_id = ws["id"]
        ws_label = ws["label"]
        for sec in ws.get("sections", []):
            for item in sec.get("items", []):
                doc_type = item.get("docType")
                if not doc_type or doc_type in seen_doctypes:
                    continue
                
                seen_doctypes.add(doc_type)

                # Test get_doctype_meta
                try:
                    from its_ui_redesign.api.common import get_doctype_meta, get_document_list
                    meta_res = get_doctype_meta(doc_type)
                    meta_success = meta_res.get("success", False)
                    meta_data = meta_res.get("data", {}) if meta_success else {}

                    # Test get_document_list
                    list_res = get_document_list(doc_type, page=1, page_length=10)
                    list_success = list_res.get("success", False)
                    list_data = list_res.get("data", []) if list_success else []
                    list_meta = list_res.get("meta", {}) if list_success else {}

                    # Test with search text
                    search_res = get_document_list(doc_type, search_text="a", page=1, page_length=5)
                    search_success = search_res.get("success", False)

                    # Determine type
                    is_custom = frappe.db.get_value("DocType", doc_type, "custom") == 1 or doc_type in ["FAT", "IFAT", "BOQ", "Rate Analysis", "Invoice Dossier"]
                    dt_type = "Custom (ITS)" if is_custom else "Standard (ERPNext)"

                    status = "PASS" if (meta_success and list_success and search_success) else "FAIL"

                    results.append({
                        "workspace": ws_label,
                        "menu": item.get("label"),
                        "docType": doc_type,
                        "type": dt_type,
                        "meta_ok": meta_success,
                        "list_ok": list_success,
                        "search_ok": search_success,
                        "count": list_meta.get("total", len(list_data)),
                        "columns": len(meta_data.get("list_fields", [])),
                        "status": status
                    })
                    print(f"[{status}] DocType: '{doc_type}' | Count: {list_meta.get('total', 0)} | Columns: {len(meta_data.get('list_fields', []))}")
                except Exception as e:
                    results.append({
                        "workspace": ws_label,
                        "menu": item.get("label"),
                        "docType": doc_type,
                        "type": "Error",
                        "meta_ok": False,
                        "list_ok": False,
                        "search_ok": False,
                        "count": 0,
                        "columns": 0,
                        "status": f"FAIL ({str(e)})"
                    })
                    print(f"[FAIL] DocType: '{doc_type}' | Error: {str(e)}")

    print("\n================ SUMMARY REPORT ================")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Total DocTypes Audited: {total}")
    print(f"Passed: {passed} / {total}")

    # Output detailed report json
    with open('/home/frappe/.gemini/antigravity-ide/brain/be0ff608-76ca-488b-afa9-9d6bb2fb6fdc/scratch/listview_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    test_all_doctypes_listview()
