import frappe
from frappe.utils import today, add_days

DEMO_PREFIX = "DEMO-ITS-2026-"
DEMO_CUSTOMER = "Demo Energy Customer"
DEMO_SUPPLIER = "Demo Power Equipment Supplier"
COMPANY = "BetaEdge (Demo)"
WAREHOUSE = "Stores - BED"
COST_CENTER = "Main - BED"
CURRENCY = "AED"

def run_setup():
    """
    Constructs the complete 38-step client demo process flow in ERPNext / its_erp_review.
    All records use the dedicated DEMO-ITS-2026- prefix or designated demo context.
    """
    print("=== STARTING ITS ERP REVIEW COMPLETE DEMO PROCESS SETUP ===")
    results = {}

    # -------------------------------------------------------------
    # 0. Core Demo Context (Customer, Supplier, Items)
    # -------------------------------------------------------------
    print("\n[00] Creating Demo Parties & Items...")
    
    # 0.1 Customer
    if not frappe.db.exists("Customer", DEMO_CUSTOMER):
        cust = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": DEMO_CUSTOMER,
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": "All Territories"
        })
        cust.insert(ignore_permissions=True)
        print(f"Created Customer: {DEMO_CUSTOMER}")
    results["customer"] = DEMO_CUSTOMER

    # 0.2 Supplier
    if not frappe.db.exists("Supplier", DEMO_SUPPLIER):
        supp = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": DEMO_SUPPLIER,
            "supplier_type": "Company",
            "supplier_group": "Local"
        })
        supp.insert(ignore_permissions=True)
        print(f"Created Supplier: {DEMO_SUPPLIER}")
    results["supplier"] = DEMO_SUPPLIER

    # 0.3 Items
    demo_items = [
        ("DEMO-PSS-SKID-400KVA", "400 KVA MV Variable Speed Power Skid Unit", 320000, 480000),
        ("DEMO-VSD-PANEL", "Variable Speed Drive (VSD) & SWF Panel", 120000, 180000),
        ("DEMO-TRANSFORMER-400KVA", "Step-Down Oil Transformer 400 KVA", 90000, 140000),
        ("DEMO-PLC-PANEL", "PLC Automation & Marshalling Control Panel", 60000, 95000),
        ("DEMO-UPS-SYSTEM", "Industrial UPS & Battery Backup Cabinet", 50000, 65000)
    ]
    item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "Products"
    for code, name, b_rate, s_rate in demo_items:
        if not frappe.db.exists("Item", code):
            it = frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": name,
                "item_group": item_group,
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "valuation_rate": b_rate,
                "standard_rate": s_rate
            })
            it.insert(ignore_permissions=True)
            print(f"Created Item: {code}")

    main_item = "DEMO-PSS-SKID-400KVA"

    # -------------------------------------------------------------
    # 01 & 02. Enquiry & Opportunity (G0)
    # -------------------------------------------------------------
    print("\n[01-02] Creating Customer Enquiry & Opportunity (G0)...")
    opp_title = f"{DEMO_PREFIX}OPP-001: 400 KVA MV Power Skid for Well-X402"
    existing_opp = frappe.db.get_value("Opportunity", {"title": opp_title}, "name")
    if not existing_opp:
        opp = frappe.get_doc({
            "doctype": "Opportunity",
            "opportunity_from": "Customer",
            "party_name": DEMO_CUSTOMER,
            "title": opp_title,
            "opportunity_type": "Sales",
            "status": "Open",
            "transaction_date": today(),
            "close_date": add_days(today(), 45),
            "currency": CURRENCY,
            "opportunity_amount": 480000.0,
            "company": COMPANY
        })
        opp.insert(ignore_permissions=True)
        existing_opp = opp.name
        print(f"Created Opportunity: {existing_opp}")
    results["opportunity"] = existing_opp

    # -------------------------------------------------------------
    # 03. Supplier RFQ (G1)
    # -------------------------------------------------------------
    print("\n[03] Creating Supplier RFQ (G1)...")
    existing_rfq = frappe.db.get_value("Request for Quotation", {"opportunity": existing_opp}, "name")
    if not existing_rfq:
        rfq = frappe.get_doc({
            "doctype": "Request for Quotation",
            "transaction_date": today(),
            "status": "Draft",
            "company": COMPANY,
            "opportunity": existing_opp,
            "message_for_supplier": f"{DEMO_PREFIX}RFQ-001: Please quote for 400 KVA MV Skid Package. Opportunity: {existing_opp}",
            "suppliers": [{"supplier": DEMO_SUPPLIER}],
            "items": [{
                "item_code": main_item,
                "qty": 1,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1.0,
                "description": "400 KVA MV Variable Speed Power Skid Unit for Oil Well",
                "warehouse": WAREHOUSE
            }]
        })
        rfq.insert(ignore_permissions=True)
        existing_rfq = rfq.name
        print(f"Created Supplier RFQ: {existing_rfq}")
    results["rfq"] = existing_rfq

    # -------------------------------------------------------------
    # 04. Supplier Quotation / Principal Offer (G2)
    # -------------------------------------------------------------
    print("\n[04] Creating Supplier Quotation (G2)...")
    sqtn_title = f"{DEMO_PREFIX}SQTN-001: Skid Package Supplier Offer"
    existing_sqtn = frappe.db.get_value("Supplier Quotation", {"title": sqtn_title}, "name")
    if not existing_sqtn:
        sqtn = frappe.get_doc({
            "doctype": "Supplier Quotation",
            "supplier": DEMO_SUPPLIER,
            "title": sqtn_title,
            "transaction_date": today(),
            "valid_till": add_days(today(), 60),
            "company": COMPANY,
            "currency": CURRENCY,
            "buying_price_list": "Standard Buying",
            "items": [{
                "item_code": main_item,
                "qty": 1,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1.0,
                "rate": 320000.0,
                "schedule_date": add_days(today(), 60),
                "warehouse": WAREHOUSE,
                "description": "Supplier quotation: 400 KVA Power Skid Unit"
            }]
        })
        sqtn.insert(ignore_permissions=True)
        existing_sqtn = sqtn.name
        print(f"Created Supplier Quotation: {existing_sqtn} (Rate: AED 320,000)")
    results["supplier_quotation"] = existing_sqtn

    # -------------------------------------------------------------
    # 05 & 06. Customer Quotation & Commercial Approval (G3)
    # -------------------------------------------------------------
    print("\n[05-06] Creating Customer Quotation & Approving (G3)...")
    qtn_title = f"{DEMO_PREFIX}QTN-001: 400 KVA Power Skid Proposal"
    existing_qtn = frappe.db.get_value("Quotation", {"title": qtn_title}, "name")
    if not existing_qtn:
        qtn = frappe.get_doc({
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": DEMO_CUSTOMER,
            "title": qtn_title,
            "transaction_date": today(),
            "valid_till": add_days(today(), 30),
            "company": COMPANY,
            "currency": CURRENCY,
            "selling_price_list": "Standard Selling",
            "order_type": "Sales",
            "opportunity": existing_opp,
            "items": [{
                "item_code": main_item,
                "qty": 1,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1.0,
                "rate": 480000.0,
                "description": "400 KVA MV Variable Speed Power Skid Unit (Supply, FAT, Delivery, Commissioning)"
            }]
        })
        qtn.insert(ignore_permissions=True)
        existing_qtn = qtn.name
        print(f"Created Customer Quotation: {existing_qtn} (Amount: AED 480,000, Margin: 33.3%)")
    results["quotation"] = existing_qtn

    # -------------------------------------------------------------
    # 07 & 08. Project Contract (G3.5)
    # -------------------------------------------------------------
    print("\n[07-08] Creating Project Contract Agreement (G3.5)...")
    con_title = f"{DEMO_PREFIX}CON-001: Turnkey Power Skid EPC Agreement"
    existing_con = frappe.db.get_value("Project Contract", {"title": con_title}, "name")
    if not existing_con:
        con = frappe.get_doc({
            "doctype": "Project Contract",
            "title": con_title,
            "status": "Approved",
            "company": COMPANY,
            "description": f"Master turnkey contract for 400 KVA Skid at Well-X402. Value: AED 480,000 + VAT. PBG: 10%, ICV: 62%, Warranty: 18 Months."
        })
        con.insert(ignore_permissions=True)
        existing_con = con.name
        print(f"Created Project Contract: {existing_con} (Status: Approved)")
    results["contract"] = existing_con

    # -------------------------------------------------------------
    # 09, 10 & 11. Sales Order & Client PO Validation (G4 & G5.5)
    # -------------------------------------------------------------
    print("\n[09-11] Creating Sales Order & Client PO Linkage (G4 & G5.5)...")
    so_title = f"{DEMO_PREFIX}SO-001: 400 KVA Power Skid Order"
    existing_so = frappe.db.get_value("Sales Order", {"title": so_title}, "name")
    if not existing_so:
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": DEMO_CUSTOMER,
            "title": so_title,
            "transaction_date": today(),
            "delivery_date": add_days(today(), 90),
            "company": COMPANY,
            "currency": CURRENCY,
            "selling_price_list": "Standard Selling",
            "order_type": "Sales",
            "po_no": "CPO-DE-2026-8801",
            "po_date": today(),
            "items": [{
                "item_code": main_item,
                "qty": 1,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1.0,
                "rate": 480000.0,
                "delivery_date": add_days(today(), 90),
                "warehouse": WAREHOUSE,
                "prevdoc_doctype": "Quotation",
                "prevdoc_docname": existing_qtn,
                "description": "400 KVA MV Variable Speed Power Skid Unit"
            }]
        })
        so.insert(ignore_permissions=True)
        so.submit()
        existing_so = so.name
        print(f"Created & Submitted Sales Order: {existing_so}")
    results["sales_order"] = existing_so

    # -------------------------------------------------------------
    # 12, 13, 14 & 15. Execution Project & PSS Skid (G6)
    # -------------------------------------------------------------
    print("\n[12-15] Creating Execution Project & PSS Skid Records...")
    proj_name = f"{DEMO_PREFIX}PSS-001"
    existing_proj = frappe.db.get_value("Project", {"name": proj_name}, "name")
    if not existing_proj:
        proj = frappe.get_doc({
            "doctype": "Project",
            "name": proj_name,
            "project_name": f"{proj_name}: 400 KVA Power Skid Well-X402",
            "status": "Open",
            "company": COMPANY,
            "customer": DEMO_CUSTOMER,
            "sales_order": existing_so,
            "expected_start_date": today(),
            "expected_end_date": add_days(today(), 120),
            "description": f"Execution project for 400 KVA MV Power Skid supply, FAT, delivery and commissioning at Well-X402."
        })
        proj.insert(ignore_permissions=True)
        existing_proj = proj.name
        print(f"Created Project: {existing_proj}")
    results["project"] = existing_proj

    # Update SO with project link
    frappe.db.set_value("Sales Order", existing_so, "project", existing_proj)
    # Also link project on contract
    frappe.db.set_value("Project Contract", existing_con, "project", existing_proj)

    # 13. ITS Review Project
    if not frappe.db.exists("ITS Review Project", proj_name):
        rev_proj = frappe.get_doc({
            "doctype": "ITS Review Project",
            "name": proj_name,
            "project_name": "400 KVA Power Skid Well-X402",
            "customer": DEMO_CUSTOMER,
            "project_type": "POWERSKID",
            "status": "Active"
        })
        rev_proj.insert(ignore_permissions=True)
        print(f"Created ITS Review Project: {proj_name}")
    results["review_project"] = proj_name

    # 14. ITS Review Skid
    skid_id = "DEMO-SKID-001"
    if not frappe.db.exists("ITS Review Skid", skid_id):
        skid = frappe.get_doc({
            "doctype": "ITS Review Skid",
            "name": skid_id,
            "project_id": proj_name,
            "skid_number": "SKID-400KVA-OIL-01",
            "well_number": "Well-X402",
            "serial_number": "SN-2026-400-001",
            "skid_type": "Power Skid (Oil Well)",
            "rating": "400 KVA",
            "location": "Well-X402 Field Yard",
            "status": "Completed"
        })
        skid.insert(ignore_permissions=True)
        print(f"Created ITS Review Skid: {skid_id} (Rating: 400 KVA, Well: Well-X402)")
    results["skid"] = skid_id

    # -------------------------------------------------------------
    # 16. Finance Commitment Gate (G6)
    # -------------------------------------------------------------
    print("\n[16] Creating Approved Finance Commitment...")
    fc_records = frappe.get_all("Finance Commitment", filters={"project": existing_proj}, fields=["name"])
    if not fc_records:
        fc = frappe.get_doc({
            "doctype": "Finance Commitment",
            "project": existing_proj,
            "supplier": DEMO_SUPPLIER,
            "customer_po": "CPO-DE-2026-8801",
            "payment_terms": "30 Days Net",
            "currency": CURRENCY,
            "advance_amount": 0.0,
            "expected_payable": 320000.0,
            "expected_margin": 33.3,
            "approval_status": "Approved",
            "cash_flow_impact": "Positive cash flow: Customer payment terms aligned with supplier disbursement."
        })
        fc.insert(ignore_permissions=True)
        print(f"Created Finance Commitment: {fc.name} (Approved)")
        results["finance_commitment"] = fc.name
    else:
        results["finance_commitment"] = fc_records[0].name

    # -------------------------------------------------------------
    # 17 & 18. Supplier Purchase Order & Acknowledgement (G7)
    # -------------------------------------------------------------
    print("\n[17-18] Creating Supplier Purchase Order (G7)...")
    po_title = f"{DEMO_PREFIX}PO-001: Power Skid Procurement"
    existing_po = frappe.db.get_value("Purchase Order", {"title": po_title}, "name")
    if not existing_po:
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": DEMO_SUPPLIER,
            "title": po_title,
            "transaction_date": today(),
            "schedule_date": add_days(today(), 45),
            "company": COMPANY,
            "currency": CURRENCY,
            "buying_price_list": "Standard Buying",
            "project": existing_proj,
            "items": [{
                "item_code": main_item,
                "qty": 1,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1.0,
                "rate": 320000.0,
                "schedule_date": add_days(today(), 45),
                "warehouse": WAREHOUSE,
                "project": existing_proj,
                "cost_center": COST_CENTER,
                "description": "400 KVA MV Variable Speed Power Skid Unit from Principal Supplier"
            }]
        })
        po.insert(ignore_permissions=True)
        po.submit()
        existing_po = po.name
        print(f"Created & Submitted Purchase Order: {existing_po}")
    results["purchase_order"] = existing_po

    # -------------------------------------------------------------
    # 19. Goods Receipt / Purchase Receipt (G7.5)
    # -------------------------------------------------------------
    print("\n[19] Creating Goods Receipt / Purchase Receipt...")
    pr_title = f"{DEMO_PREFIX}PR-001: Power Skid Delivery Receipt"
    existing_pr = frappe.db.get_value("Purchase Receipt", {"title": pr_title}, "name")
    if not existing_pr:
        from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
        pr = make_purchase_receipt(existing_po)
        pr.title = pr_title
        pr.supplier_delivery_note = "SP-DN-2026-904"
        pr.insert(ignore_permissions=True)
        pr.submit()
        existing_pr = pr.name
        print(f"Created & Submitted Purchase Receipt: {existing_pr}")
    results["purchase_receipt"] = existing_pr

    # -------------------------------------------------------------
    # 20. Document Register
    # -------------------------------------------------------------
    print("\n[20] Creating Document Register Records...")
    doc_id = f"{DEMO_PREFIX}DOC-001"
    if not frappe.db.exists("ITS Review Document", doc_id):
        rev_doc = frappe.get_doc({
            "doctype": "ITS Review Document",
            "name": doc_id,
            "project_id": proj_name,
            "skid_id": skid_id,
            "title": "General Arrangement Drawing & Single Line Diagram",
            "category": "Engineering Drawing",
            "reference": "GA-SLD-400-01",
            "revision": "B",
            "status": "Approved",
            "discipline": "Electrical",
            "submitted_date": today(),
            "review_comments": "Approved without comments by Client Electrical Lead."
        })
        rev_doc.insert(ignore_permissions=True)
        print(f"Created Document Register Record: {doc_id}")
    results["document_register"] = doc_id

    # -------------------------------------------------------------
    # 21. Request for Information (RFI)
    # -------------------------------------------------------------
    print("\n[21] Creating Technical RFI...")
    rfi_title = f"{DEMO_PREFIX}RFI-001: 11kV Cable Entry Gland Size"
    existing_rfi = frappe.db.get_value("Request for Information", {"title": rfi_title}, "name")
    if not existing_rfi:
        rfi = frappe.get_doc({
            "doctype": "Request for Information",
            "title": rfi_title,
            "project": existing_proj,
            "company": COMPANY,
            "status": "Completed",
            "description": "Technical query: Confirm incoming 11kV armored cable gland size for skid junction box. Response: M63 x 1.5 brass gland approved."
        })
        rfi.insert(ignore_permissions=True)
        existing_rfi = rfi.name
        print(f"Created RFI: {existing_rfi} (Status: Completed)")
    results["rfi"] = existing_rfi

    # -------------------------------------------------------------
    # 22 & 23. Factory Acceptance Test (FAT & IFAT) (G8)
    # -------------------------------------------------------------
    print("\n[22-23] Creating FAT & IFAT Inspection Records (G8)...")
    fat_title = f"{DEMO_PREFIX}FAT-001: Skid Assembly Factory Acceptance Test"
    existing_fat = frappe.db.get_value("Factory Acceptance Test", {"title": fat_title}, "name")
    if not existing_fat:
        fat = frappe.get_doc({
            "doctype": "Factory Acceptance Test",
            "title": fat_title,
            "project": existing_proj,
            "purchase_order": existing_po,
            "item_code": main_item,
            "supplier": DEMO_SUPPLIER,
            "customer": DEMO_CUSTOMER,
            "status": "Approved",
            "result": "Passed",
            "inspection_date": today(),
            "inspector": "QA Inspection Engineer - Demo",
            "witness": "Client Senior Representative",
            "test_location": "Supplier Heavy Industrial Facility - Abu Dhabi",
            "remarks": "All factory acceptance tests (insulation, full load, control loops) completed with PASS result."
        })
        fat.insert(ignore_permissions=True)
        existing_fat = fat.name
        print(f"Created FAT Record: {existing_fat} (Pass)")
    results["fat"] = existing_fat

    ifat_title = f"{DEMO_PREFIX}IFAT-001: Integrated SCADA & Telemetry Test"
    existing_ifat = frappe.db.get_value("Integrated Factory Acceptance Test", {"title": ifat_title}, "name")
    if not existing_ifat:
        ifat = frappe.get_doc({
            "doctype": "Integrated Factory Acceptance Test",
            "title": ifat_title,
            "project": existing_proj,
            "purchase_order": existing_po,
            "sales_order": existing_so,
            "item_code": main_item,
            "supplier": DEMO_SUPPLIER,
            "customer": DEMO_CUSTOMER,
            "fat_reference": existing_fat,
            "status": "Approved",
            "integration_result": "Passed",
            "inspection_date": today(),
            "lead_integrator": "Lead Automation Engineer",
            "witness": "Client Controls Representative",
            "test_facility": "ITS Integrated Testing Yard",
            "system_scope": "Full integration of VSD, PLC, Modbus TCP and Remote Telemetry",
            "remarks": "Integration tests completed. Skid communicates seamlessly with remote station."
        })
        ifat.insert(ignore_permissions=True)
        existing_ifat = ifat.name
        print(f"Created IFAT Record: {existing_ifat} (Pass)")
    results["ifat"] = existing_ifat

    # -------------------------------------------------------------
    # 24. Punch Point & Closure (G8.5)
    # -------------------------------------------------------------
    print("\n[24] Creating Punch Point & Verified Closure (G8.5)...")
    punch_id = f"{DEMO_PREFIX}PUNCH-001"
    if not frappe.db.exists("ITS Review Punch", punch_id):
        p = frappe.get_doc({
            "doctype": "ITS Review Punch",
            "name": punch_id,
            "project_id": proj_name,
            "skid_id": skid_id,
            "source": "FAT Inspection",
            "category": "Critical",
            "priority": "Critical",
            "status": "Closed",
            "responsible": DEMO_SUPPLIER,
            "assigned": "Administrator",
            "raised_date": today(),
            "target_date": add_days(today(), 5),
            "description": "Paint scratch on transformer access door and missing warning label.",
            "closure_remarks": "Surface touched up with epoxy paint, warning label installed. Cleared by QA inspector.",
            "closed_date": today(),
            "evidence": "QC-INSP-REPORT-P01.pdf"
        })
        p.insert(ignore_permissions=True)
        print(f"Created & Closed ITS Review Punch: {punch_id}")
    results["punch"] = punch_id

    # Also record in Snag List
    snag_title = f"{DEMO_PREFIX}SNAG-001: Transformer Access Door Paint"
    if not frappe.db.get_value("Snag List", {"title": snag_title}, "name"):
        snag = frappe.get_doc({
            "doctype": "Snag List",
            "title": snag_title,
            "project": existing_proj,
            "company": COMPANY,
            "status": "Completed",
            "description": "Resolved critical snag: paint touch-up and label verified by QA."
        })
        snag.insert(ignore_permissions=True)
        print(f"Created Snag List Record: {snag.name} (Completed)")

    # -------------------------------------------------------------
    # 25, 26 & 27. Delivery Note & POD Evidence (G9 & G9.5)
    # -------------------------------------------------------------
    print("\n[25-27] Creating Delivery Note & Proof of Delivery (G9 & G9.5)...")
    dn_title = f"{DEMO_PREFIX}DN-001: 400 KVA Power Skid Site Delivery"
    existing_dn = frappe.db.get_value("Delivery Note", {"title": dn_title}, "name")
    if not existing_dn:
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        dn = make_delivery_note(existing_so)
        dn.title = dn_title
        dn.lr_no = "TRK-WAYBILL-2026-904"
        dn.lr_date = today()
        dn.project = existing_proj
        for itm in dn.items:
            itm.project = existing_proj
        dn.insert(ignore_permissions=True)
        dn.submit()
        existing_dn = dn.name
        print(f"Created & Submitted Delivery Note: {existing_dn}")
    results["delivery_note"] = existing_dn

    # -------------------------------------------------------------
    # 28, 29, 30 & 31. Site Mobilization, Commissioning & SAT (G9.6)
    # -------------------------------------------------------------
    print("\n[28-31] Creating Mobilization Compliance & Commissioning...")
    
    # 29. Personnel Certificate
    cert_no = f"{DEMO_PREFIX}CERT-001"
    existing_cert = frappe.db.get_value("Personnel Certificate", {"certificate_number": cert_no}, "name")
    if not existing_cert:
        cert = frappe.get_doc({
            "doctype": "Personnel Certificate",
            "personnel_name": "Rashid Al Nuaimi (Lead FSE)",
            "certificate_number": cert_no,
            "certificate_type": "CICPA Site Pass & H2S Certification",
            "issuing_authority": "CICPA & ADNOC Training Academy",
            "issue_date": today(),
            "expiry_date": add_days(today(), 365),
            "status": "Valid",
            "personnel_type": "FSE"
        })
        cert.insert(ignore_permissions=True)
        existing_cert = cert.name
        print(f"Created Personnel Certificate: {existing_cert} (Valid)")
    results["personnel_certificate"] = existing_cert

    # 28 & 31. ITS Review Commissioning
    comm_id = f"{DEMO_PREFIX}COMM-001"
    if not frappe.db.exists("ITS Review Commissioning", comm_id):
        comm = frappe.get_doc({
            "doctype": "ITS Review Commissioning",
            "name": comm_id,
            "project_id": proj_name,
            "skid_id": skid_id,
            "status": "Commissioned",
            "planned_date": today(),
            "commissioning_date": today(),
            "engineer": "Rashid Al Nuaimi",
            "remarks": "On-site installation, loop testing, full power energization, and SAT completed with client sign-off."
        })
        comm.insert(ignore_permissions=True)
        print(f"Created ITS Review Commissioning: {comm_id} (Commissioned)")
    results["commissioning"] = comm_id

    # -------------------------------------------------------------
    # 32. Project Handover & CEP (G9.7)
    # -------------------------------------------------------------
    print("\n[32] Creating Project Handover & Acceptance (G9.7)...")
    ho_id = f"{DEMO_PREFIX}HO-001"
    if not frappe.db.exists("ITS Review Handover", ho_id):
        ho = frappe.get_doc({
            "doctype": "ITS Review Handover",
            "name": ho_id,
            "project_id": proj_name,
            "skid_id": skid_id,
            "status": "Accepted",
            "cep": "CEP-DEMO-2026-001",
            "date": today(),
            "remarks": "Certificate of Equipment Performance (CEP) signed off by Customer Operations Superintendent."
        })
        ho.insert(ignore_permissions=True)
        print(f"Created ITS Review Handover: {ho_id} (Accepted)")
    results["handover"] = ho_id

    # Also create Project Handover doc
    pho_title = f"{DEMO_PREFIX}HO-001: Well-X402 Skid Site Handover"
    if not frappe.db.get_value("Project Handover", {"title": pho_title}, "name"):
        pho = frappe.get_doc({
            "doctype": "Project Handover",
            "title": pho_title,
            "project": existing_proj,
            "company": COMPANY,
            "status": "Completed",
            "description": "Formal site handover completed. Final dossier and CEP accepted."
        })
        pho.insert(ignore_permissions=True)
        pho.submit()
        print(f"Created & Submitted Project Handover Document: {pho.name}")

    # -------------------------------------------------------------
    # 33 & 34. Invoice Readiness & Sales Invoice (G10 & G10.5)
    # -------------------------------------------------------------
    print("\n[33-34] Creating & Submitting Sales Invoice (G10 & G10.5)...")
    sinv_title = f"{DEMO_PREFIX}SINV-001: Power Skid Final Commercial Invoice"
    existing_sinv = frappe.db.get_value("Sales Invoice", {"title": sinv_title}, "name")
    if not existing_sinv:
        from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
        sinv = make_sales_invoice(existing_dn)
        sinv.title = sinv_title
        sinv.due_date = add_days(today(), 30)
        sinv.project = existing_proj
        for itm in sinv.items:
            itm.project = existing_proj
        sinv.insert(ignore_permissions=True)
        sinv.submit()
        existing_sinv = sinv.name
        print(f"Created & Submitted Sales Invoice: {existing_sinv} (Grand Total: AED {sinv.grand_total:,.2f})")
    results["sales_invoice"] = existing_sinv

    # -------------------------------------------------------------
    # 35. Payment Entry (Settlement)
    # -------------------------------------------------------------
    print("\n[35] Creating Payment Entry Receipt...")
    pay_title = f"{DEMO_PREFIX}PAY-001: Full Payment Receipt for Skid"
    existing_pay = frappe.db.get_value("Payment Entry", {"title": pay_title}, "name")
    if not existing_pay:
        sinv_doc = frappe.get_doc("Sales Invoice", existing_sinv)
        if sinv_doc.outstanding_amount > 0:
            from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
            pe = get_payment_entry("Sales Invoice", existing_sinv)
            pe.title = pay_title
            pe.reference_no = "TXN-DEMO-2026-001"
            pe.reference_date = today()
            pe.remarks = f"{pay_title}: Bank transfer received from {DEMO_CUSTOMER}."
            pe.insert(ignore_permissions=True)
            pe.submit()
            existing_pay = pe.name
            print(f"Created & Submitted Payment Entry: {existing_pay} (Paid: AED {pe.paid_amount:,.2f})")
    results["payment_entry"] = existing_pay

    # -------------------------------------------------------------
    # 36. Project Warranty
    # -------------------------------------------------------------
    print("\n[36] Creating Project Warranty Register...")
    war_title = f"{DEMO_PREFIX}WAR-001: 18-Month Power Skid Performance Warranty"
    existing_war = frappe.db.get_value("Project Warranty", {"title": war_title}, "name")
    if not existing_war:
        war = frappe.get_doc({
            "doctype": "Project Warranty",
            "title": war_title,
            "project": existing_proj,
            "company": COMPANY,
            "status": "Approved",
            "description": f"Comprehensive 18-Month Performance Warranty from commissioning. Covers manufacturing defects, VSD components and performance metrics. End date: {add_days(today(), 540)}."
        })
        war.insert(ignore_permissions=True)
        existing_war = war.name
        print(f"Created Project Warranty: {existing_war} (Status: Approved)")
    results["warranty"] = existing_war

    # -------------------------------------------------------------
    # 37 & 38. Maintenance Case & Final Closure (G11)
    # -------------------------------------------------------------
    print("\n[37-38] Creating Maintenance Case & Service Closure (G11)...")
    issue_subject = f"{DEMO_PREFIX}MAINT-001: Temperature Sensor Calibration"
    existing_issue = frappe.db.get_value("Issue", {"subject": issue_subject}, "name")
    if not existing_issue:
        issue = frappe.get_doc({
            "doctype": "Issue",
            "subject": issue_subject,
            "customer": DEMO_CUSTOMER,
            "status": "Closed",
            "description": "Routine warranty service: transformer PT100 temperature sensor recalibrated. Temperature telemetry verified with central control. Signed by Field Superintendent."
        })
        issue.insert(ignore_permissions=True)
        existing_issue = issue.name
        print(f"Created & Closed Maintenance Issue: {existing_issue}")
    results["maintenance_issue"] = existing_issue

    # Also record in Maintenance Visit
    mv_records = frappe.get_all("Maintenance Visit", filters={"customer": DEMO_CUSTOMER}, fields=["name"])
    if not mv_records:
        sp = frappe.db.get_value("Sales Person", {"is_group": 0}, "name") or "_Test Sales Person"
        mv = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "customer": DEMO_CUSTOMER,
            "mntc_date": today(),
            "maintenance_type": "Unscheduled",
            "completion_status": "Fully Completed",
            "purposes": [{
                "item_code": main_item,
                "item_name": "400 KVA MV Variable Speed Power Skid Unit",
                "service_person": sp,
                "work_done": "Recalibrated transformer PT100 sensors and verified telemetry signals.",
                "description": "Warranty service inspection completed."
            }]
        })
        mv.insert(ignore_permissions=True)
        mv.submit()
        print(f"Created & Submitted Maintenance Visit: {mv.name}")
        results["maintenance_visit"] = mv.name
    else:
        results["maintenance_visit"] = mv_records[0].name

    frappe.db.commit()
    print("\n=== COMPLETE 38-STEP DEMO PROCESS SETUP SUCCESSFULLY FINISHED ===")
    return results

if __name__ == "__main__":
    frappe.init(site="frappe.com", sites_path="sites")
    frappe.connect()
    run_setup()
