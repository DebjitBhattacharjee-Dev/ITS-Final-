import frappe
from frappe import _

DEMO_PREFIX = "DEMO-ITS-2026-"
DEMO_CUSTOMER = "Demo Energy Customer"
DEMO_SUPPLIER = "Demo Power Equipment Supplier"

def run_cleanup(confirm=True):
    """
    Safely deletes ONLY demo records created for the ITS ERP Review Demo.
    Never deletes or alters live production records.
    Respects dependency order and cancels submittable documents first.
    """
    print("=== STARTING ITS ERP REVIEW DEMO CLEANUP ===")
    
    cleaned = {}
    
    def safe_delete_records(doctype, filters):
        recs = frappe.get_all(doctype, filters=filters, fields=["name", "docstatus"])
        deleted_count = 0
        for r in recs:
            try:
                name = r["name"]
                # If submitted, cancel first
                if r.get("docstatus") == 1:
                    doc = frappe.get_doc(doctype, name)
                    doc.cancel()
                    frappe.db.commit()
                
                frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
                frappe.db.commit()
                deleted_count += 1
            except Exception as e:
                print(f"Warning deleting {doctype} {r['name']}: {str(e)}")
        if deleted_count > 0:
            cleaned[doctype] = deleted_count
            print(f"Cleaned {deleted_count} record(s) from {doctype}")

    # 1. Financial & Settlement Transactions
    safe_delete_records("Payment Entry", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Payment Entry", [["remarks", "like", f"%{DEMO_PREFIX}%"]])
    safe_delete_records("Sales Invoice", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Sales Invoice", {"customer": DEMO_CUSTOMER})
    
    # 2. Logistics & Delivery Transactions
    safe_delete_records("Delivery Note", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Delivery Note", {"customer": DEMO_CUSTOMER})
    safe_delete_records("Purchase Receipt", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Purchase Receipt", {"supplier": DEMO_SUPPLIER})
    
    # 3. Purchasing & Orders
    safe_delete_records("Purchase Order", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Purchase Order", {"supplier": DEMO_SUPPLIER})
    safe_delete_records("Finance Commitment", [["project", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Finance Commitment", {"supplier": DEMO_SUPPLIER})
    safe_delete_records("Finance Commitment", {"customer_po": "CPO-DE-2026-8801"})
    safe_delete_records("Sales Order", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Sales Order", {"customer": DEMO_CUSTOMER})
    
    # 4. Contracts & Commercial Quotations
    safe_delete_records("Project Contract", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Project Contract", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Quotation", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Quotation", {"party_name": DEMO_CUSTOMER})
    safe_delete_records("Supplier Quotation", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Supplier Quotation", {"supplier": DEMO_SUPPLIER})
    
    # RFQs linked to demo items or demo opportunities
    demo_opps = frappe.get_all("Opportunity", filters={"party_name": DEMO_CUSTOMER}, pluck="name")
    if demo_opps:
        safe_delete_records("Request for Quotation", {"opportunity": ["in", demo_opps]})
    try:
        rfq_from_items = frappe.db.sql_list("select distinct parent from `tabRequest for Quotation Item` where item_code like 'DEMO-%'")
        for rfq_n in rfq_from_items:
            safe_delete_records("Request for Quotation", {"name": rfq_n})
    except Exception:
        pass
    
    safe_delete_records("Opportunity", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Opportunity", {"party_name": DEMO_CUSTOMER})

    # 5. Quality, Handover, Warranty & Maintenance
    safe_delete_records("Maintenance Visit", {"customer": DEMO_CUSTOMER})
    safe_delete_records("Issue", [["subject", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Project Warranty", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Project Handover", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Snag List", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Request for Information", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Integrated Factory Acceptance Test", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Factory Acceptance Test", [["title", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Personnel Certificate", [["certificate_number", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Personnel Certificate", [["personnel_name", "like", "DEMO-%"]])

    # 6. Specialized Review DocTypes
    safe_delete_records("ITS Review Handover", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("ITS Review Handover", {"project_id": "DEMO-ITS-2026-PSS-001"})
    safe_delete_records("ITS Review Commissioning", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("ITS Review Commissioning", {"project_id": "DEMO-ITS-2026-PSS-001"})
    safe_delete_records("ITS Review Punch", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("ITS Review Punch", {"project_id": "DEMO-ITS-2026-PSS-001"})
    safe_delete_records("ITS Review Document", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("ITS Review Document", {"project_id": "DEMO-ITS-2026-PSS-001"})
    safe_delete_records("ITS Review Skid", [["name", "like", "DEMO-%"]])
    safe_delete_records("ITS Review Skid", {"project_id": "DEMO-ITS-2026-PSS-001"})
    safe_delete_records("ITS Review Project", [["name", "like", f"{DEMO_PREFIX}%"]])
    
    # 7. ERPNext Projects & Items
    safe_delete_records("Project", [["name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Project", [["project_name", "like", f"{DEMO_PREFIX}%"]])
    safe_delete_records("Project", {"customer": DEMO_CUSTOMER})
    safe_delete_records("Item", [["item_code", "like", "DEMO-%"]])
    
    # 8. Demo Parties
    safe_delete_records("Customer", {"name": DEMO_CUSTOMER})
    safe_delete_records("Supplier", {"name": DEMO_SUPPLIER})

    frappe.db.commit()
    print("=== DEMO CLEANUP COMPLETE ===")
    print(f"Total DocTypes affected: {len(cleaned)}")
    return cleaned

if __name__ == "__main__":
    frappe.init(site="frappe.com", sites_path="sites")
    frappe.connect()
    run_cleanup()
