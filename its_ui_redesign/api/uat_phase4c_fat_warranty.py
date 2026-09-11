import frappe
import json
from frappe.utils import today, add_days

def run():
    results = {}
    company = 'BetaEdge (Demo)'
    customer = 'UAT-ITS Customer'
    supplier = 'UAT-ITS Supplier'
    item_code = 'UAT-ITS-PSS-SKID-001'
    cost_center = 'Main - BED'
    warehouse = 'Stores - BED'
    nada_user = 'nada.ramy@its-operations.com'

    # Get chain references
    def get_ref(doctype, title_filter):
        recs = frappe.get_all(doctype, filters=[['title', 'like', title_filter]], fields=['name'], limit=1)
        return recs[0]['name'] if recs else None

    def get_ref_any(doctype, name_filter=None, project=None):
        filters = []
        if name_filter:
            filters.append(['name', 'like', name_filter])
        if project:
            filters.append(['project', '=', project])
        recs = frappe.get_all(doctype, filters=filters, fields=['name'], limit=1)
        return recs[0]['name'] if recs else None

    proj_name = None
    proj_recs = frappe.get_all('Project', filters=[['project_name', 'like', 'UAT-ITS-PSS%']], fields=['name'], limit=1)
    if proj_recs:
        proj_name = proj_recs[0]['name']
    results['ref_project'] = proj_name

    so_recs = frappe.get_all('Sales Order', filters=[['title', 'like', 'UAT-ITS-SO%']], fields=['name', 'status'], limit=1)
    so_name = so_recs[0]['name'] if so_recs else None
    results['ref_sales_order'] = so_name

    po_recs = frappe.get_all('Purchase Order', filters=[['title', 'like', 'UAT-ITS-PO%']], fields=['name'], limit=1)
    po_name = po_recs[0]['name'] if po_recs else None
    results['ref_purchase_order'] = po_name

    pr_recs = frappe.get_all('Purchase Receipt', filters=[['title', 'like', 'UAT-ITS-RECEIPT%']], fields=['name'], limit=1)
    pr_name = pr_recs[0]['name'] if pr_recs else None
    results['ref_purchase_receipt'] = pr_name

    # =========================================================
    # FAT — Factory Acceptance Test
    # =========================================================
    fat_name = None
    existing_fat = frappe.get_all('Factory Acceptance Test',
        filters=[['title', 'like', 'UAT-ITS-FAT%']], fields=['name'], limit=1)
    if existing_fat:
        fat_name = existing_fat[0]['name']
        results['fat'] = {'status': 'exists', 'name': fat_name}
    else:
        try:
            fat = frappe.get_doc({
                'doctype': 'Factory Acceptance Test',
                'naming_series': 'FAT-.YYYY.-.#####',
                'title': 'UAT-ITS-FAT-001: MV Power Skid FAT',
                'project': proj_name,
                'purchase_order': po_name,
                'item_code': item_code,
                'supplier': supplier,
                'customer': customer,
                'status': 'Completed',
                'result': 'Pass',
                'inspection_date': today(),
                'inspector': 'Nada Ramy',
                'witness': 'Client Representative',
                'test_location': 'Supplier Factory — UAE Industrial Area',
                'remarks': 'UAT-ITS-FAT-001: All FAT tests completed successfully. Equipment meets specifications.',
            })
            fat.insert(ignore_permissions=True)
            frappe.db.commit()
            fat_name = fat.name
            results['fat'] = {'status': 'created', 'name': fat.name, 'result': 'Pass'}
        except Exception as e:
            results['fat'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # IFAT — Integrated Factory Acceptance Test
    # =========================================================
    ifat_name = None
    existing_ifat = frappe.get_all('Integrated Factory Acceptance Test',
        filters=[['title', 'like', 'UAT-ITS-IFAT%']], fields=['name'], limit=1)
    if existing_ifat:
        ifat_name = existing_ifat[0]['name']
        results['ifat'] = {'status': 'exists', 'name': ifat_name}
    else:
        try:
            ifat = frappe.get_doc({
                'doctype': 'Integrated Factory Acceptance Test',
                'naming_series': 'IFAT-.YYYY.-.#####',
                'title': 'UAT-ITS-IFAT-001: MV Power Skid IFAT',
                'project': proj_name,
                'purchase_order': po_name,
                'sales_order': so_name,
                'item_code': item_code,
                'supplier': supplier,
                'customer': customer,
                'fat_reference': fat_name,
                'status': 'Completed',
                'integration_result': 'Pass',
                'inspection_date': add_days(today(), 7),
                'lead_integrator': 'Nada Ramy',
                'witness': 'Client Representative',
                'test_facility': 'Supplier Integration Test Facility — UAE',
                'system_scope': 'MV Power Skid integration with SCADA and protection systems',
                'remarks': 'UAT-ITS-IFAT-001: Integrated testing completed. All systems function as expected.',
            })
            ifat.insert(ignore_permissions=True)
            frappe.db.commit()
            ifat_name = ifat.name
            results['ifat'] = {'status': 'created', 'name': ifat.name, 'result': 'Pass'}
        except Exception as e:
            results['ifat'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # SNAG / PUNCH LIST — Create open critical item (negative test)
    # =========================================================
    snag_name = None
    existing_snag = frappe.get_all('Snag List',
        filters=[['title', 'like', 'UAT-ITS-PUNCH%']], fields=['name'], limit=1)
    if existing_snag:
        snag_name = existing_snag[0]['name']
        results['snag_list'] = {'status': 'exists', 'name': snag_name}
    else:
        try:
            snag = frappe.get_doc({
                'doctype': 'Snag List',
                'title': 'UAT-ITS-PUNCH-001: Critical Paint Defect on Panel Door',
                'project': proj_name,
                'company': company,
                'status': 'Open',
                'description': 'UAT-ITS-PUNCH-001: CRITICAL — Paint defect found on panel door during FAT. Must be rectified before delivery. Responsible: Nada Ramy. Category: Cosmetic/Critical.',
            })
            snag.insert(ignore_permissions=True)
            frappe.db.commit()
            snag_name = snag.name
            results['snag_list'] = {
                'status': 'created',
                'name': snag.name,
                'punch_status': 'Open',
                'note': 'NEGATIVE TEST: Open punch — delivery should be blocked until resolved'
            }
        except Exception as e:
            results['snag_list'] = {'status': 'error', 'error': str(e)}

    # Close the punch list item (positive resolution)
    if snag_name:
        try:
            snag_doc = frappe.get_doc('Snag List', snag_name)
            if snag_doc.status == 'Open':
                snag_doc.status = 'Closed'
                snag_doc.description = (snag_doc.description or '') + '\n\nRESOLVED: Paint defect rectified by supplier. Verified by Nada Ramy on site visit. Cleared for delivery.'
                snag_doc.save(ignore_permissions=True)
                frappe.db.commit()
                results['snag_list_resolved'] = {
                    'status': 'resolved',
                    'name': snag_name,
                    'new_status': 'Closed',
                    'note': 'POSITIVE TEST: Punch resolved — delivery can now proceed'
                }
        except Exception as e:
            results['snag_list_resolved'] = {'error': str(e)}

    # =========================================================
    # RFI — Request for Information
    # =========================================================
    rfi_name = None
    existing_rfi = frappe.get_all('Request for Information',
        filters=[['title', 'like', 'UAT-ITS-RFI%']], fields=['name'], limit=1)
    if existing_rfi:
        rfi_name = existing_rfi[0]['name']
        results['rfi'] = {'status': 'exists', 'name': rfi_name}
    else:
        try:
            rfi = frappe.get_doc({
                'doctype': 'Request for Information',
                'title': 'UAT-ITS-RFI-001: Clarification on Cable Entry Requirements',
                'project': proj_name,
                'company': company,
                'status': 'Open',
                'description': 'UAT-ITS-RFI-001: Please clarify cable entry gland sizing for main incoming cable. Ref: IEC 60529 IP rating vs site requirements. Responsible: Nada Ramy. Due: ' + add_days(today(), 5),
            })
            rfi.insert(ignore_permissions=True)
            frappe.db.commit()
            rfi_name = rfi.name
            results['rfi'] = {'status': 'created', 'name': rfi.name}
        except Exception as e:
            results['rfi'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # PROJECT HANDOVER
    # =========================================================
    handover_name = None
    existing_handover = frappe.get_all('Project Handover',
        filters=[['title', 'like', 'UAT-ITS-HANDOVER%']], fields=['name'], limit=1)
    if existing_handover:
        handover_name = existing_handover[0]['name']
        results['project_handover'] = {'status': 'exists', 'name': handover_name}
    else:
        try:
            handover = frappe.get_doc({
                'doctype': 'Project Handover',
                'title': 'UAT-ITS-HANDOVER-001: MV Power Skid Site Handover',
                'project': proj_name,
                'company': company,
                'status': 'Completed',
                'description': 'UAT-ITS-HANDOVER-001: Site handover completed. Client representative signed off. All punch items cleared. Commissioning report attached. Responsible: Nada Ramy.',
            })
            handover.insert(ignore_permissions=True)
            frappe.db.commit()
            handover_name = handover.name
            results['project_handover'] = {'status': 'created', 'name': handover.name}
        except Exception as e:
            results['project_handover'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # PROJECT WARRANTY
    # =========================================================
    warranty_name = None
    existing_warranty = frappe.get_all('Project Warranty',
        filters=[['title', 'like', 'UAT-ITS-WARRANTY%']], fields=['name'], limit=1)
    if existing_warranty:
        warranty_name = existing_warranty[0]['name']
        results['project_warranty'] = {'status': 'exists', 'name': warranty_name}
    else:
        try:
            warranty = frappe.get_doc({
                'doctype': 'Project Warranty',
                'title': 'UAT-ITS-WARRANTY-001: MV Power Skid 12-Month Warranty',
                'project': proj_name,
                'company': company,
                'status': 'Active',
                'description': 'UAT-ITS-WARRANTY-001: 12-month warranty period. Warranty start: ' + today() + '. Warranty end: ' + add_days(today(), 365) + '. Covers manufacturing defects and performance guarantees.',
            })
            warranty.insert(ignore_permissions=True)
            frappe.db.commit()
            warranty_name = warranty.name
            results['project_warranty'] = {'status': 'created', 'name': warranty.name}
        except Exception as e:
            results['project_warranty'] = {'status': 'error', 'error': str(e)}

    print(json.dumps(results, indent=2, default=str))
