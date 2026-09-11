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

    # Get existing chain references
    opp_name = None
    opps = frappe.get_all('Opportunity', filters=[['title', 'like', 'UAT-ITS-G0%']], fields=['name'], limit=1)
    if opps:
        opp_name = opps[0]['name']
    results['ref_opportunity'] = opp_name

    cqtn_name = None
    cqtns = frappe.get_all('Quotation', filters=[['title', 'like', 'UAT-ITS-G3%']], fields=['name', 'status'],
                           order_by='creation asc', limit=1)
    if cqtns:
        cqtn_name = cqtns[0]['name']
    results['ref_customer_quotation'] = cqtn_name

    # =========================================================
    # G3.5: PROJECT CONTRACT (Custom ITS DocType)
    # =========================================================
    contract_name = None
    existing_contract = frappe.get_all('Project Contract',
        filters=[['name', 'like', 'UAT-ITS-CONTRACT%']],
        fields=['name'], limit=1)

    if existing_contract:
        contract_name = existing_contract[0]['name']
        results['project_contract'] = {'status': 'exists', 'name': contract_name}
    else:
        try:
            meta = frappe.get_meta('Project Contract')
            field_names = [f.fieldname for f in meta.fields
                           if f.fieldtype not in ['Section Break', 'Column Break', 'HTML', 'Tab Break']]

            doc_data = {'doctype': 'Project Contract'}

            # Set fields based on what exists
            field_map = {
                'customer': customer,
                'client': customer,
                'party_name': customer,
                'company': company,
                'contract_date': today(),
                'start_date': today(),
                'end_date': add_days(today(), 365),
                'contract_value': 52000,
                'contract_amount': 52000,
                'value': 52000,
                'amount': 52000,
                'status': 'Active',
                'title': 'UAT-ITS-CONTRACT-001: MV Power Skid Supply & Commissioning',
                'name': 'UAT-ITS-CONTRACT-001',
                'description': 'UAT-ITS-G3.5: Project Contract for MV Power Skid Supply, Installation, FAT, IFAT and Commissioning',
                'quotation': cqtn_name,
                'opportunity': opp_name,
                'scope': 'Supply, Installation, Testing and Commissioning of MV Power Skid',
                'warranty_period': '12 Months',
                'payment_terms': '30% Advance, 60% on Delivery, 10% on FAT',
            }

            for fn, val in field_map.items():
                if fn in field_names and val:
                    doc_data[fn] = val

            contract = frappe.get_doc(doc_data)
            contract.insert(ignore_permissions=True)
            frappe.db.commit()
            contract_name = contract.name
            results['project_contract'] = {'status': 'created', 'name': contract.name}
        except Exception as e:
            results['project_contract'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # G5.5: SALES ORDER
    # =========================================================
    so_name = None
    existing_so = frappe.get_all('Sales Order',
        filters=[['title', 'like', 'UAT-ITS-SO%']],
        fields=['name'], limit=1)

    if existing_so:
        so_name = existing_so[0]['name']
        results['sales_order'] = {'status': 'exists', 'name': so_name}
    else:
        try:
            so = frappe.get_doc({
                'doctype': 'Sales Order',
                'customer': customer,
                'title': 'UAT-ITS-SO-001: MV Power Skid',
                'transaction_date': today(),
                'delivery_date': add_days(today(), 90),
                'company': company,
                'currency': 'AED',
                'selling_price_list': 'Standard Selling',
                'order_type': 'Sales',
                'items': [{
                    'item_code': item_code,
                    'qty': 1,
                    'rate': 52000,
                    'delivery_date': add_days(today(), 90),
                    'description': 'UAT-ITS-SO-001: MV Power Skid Supply & Commissioning',
                }],
            })
            so.insert(ignore_permissions=True)
            so.submit()
            frappe.db.commit()
            so_name = so.name
            results['sales_order'] = {
                'status': 'created_submitted',
                'name': so.name,
                'grand_total': so.grand_total,
                'status_val': so.status,
            }
        except Exception as e:
            results['sales_order'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # PROJECT (PSS)
    # =========================================================
    proj_name = None
    existing_proj = frappe.get_all('Project',
        filters=[['project_name', 'like', 'UAT-ITS-PSS%']],
        fields=['name'], limit=1)

    if existing_proj:
        proj_name = existing_proj[0]['name']
        results['project'] = {'status': 'exists', 'name': proj_name}
    else:
        try:
            proj = frappe.get_doc({
                'doctype': 'Project',
                'project_name': 'UAT-ITS-PSS-001: MV Power Skid Project',
                'status': 'Open',
                'company': company,
                'customer': customer,
                'expected_start_date': today(),
                'expected_end_date': add_days(today(), 120),
                'sales_order': so_name,
                'description': 'UAT-ITS-PSS-001: End-to-end UAT project for MV Power Skid supply, FAT, IFAT, delivery and commissioning.',
                'notes': f'Opportunity: {opp_name}\nContract: {contract_name}\nSales Order: {so_name}',
            })
            proj.insert(ignore_permissions=True)
            frappe.db.commit()
            proj_name = proj.name
            results['project'] = {
                'status': 'created', 'name': proj.name,
                'project_name': proj.project_name,
                'linked_so': so_name,
            }
        except Exception as e:
            results['project'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # G7: PURCHASE ORDER
    # =========================================================
    po_name = None
    existing_po = frappe.get_all('Purchase Order',
        filters=[['title', 'like', 'UAT-ITS-PO%']],
        fields=['name'], limit=1)

    if existing_po:
        po_name = existing_po[0]['name']
        results['purchase_order'] = {'status': 'exists', 'name': po_name}
    else:
        try:
            po = frappe.get_doc({
                'doctype': 'Purchase Order',
                'supplier': supplier,
                'title': 'UAT-ITS-PO-001: MV Power Skid from Supplier',
                'transaction_date': today(),
                'schedule_date': add_days(today(), 60),
                'company': company,
                'currency': 'AED',
                'buying_price_list': 'Standard Buying',
                'project': proj_name,
                'items': [{
                    'item_code': item_code,
                    'qty': 1,
                    'rate': 30000,
                    'schedule_date': add_days(today(), 60),
                    'description': 'UAT-ITS-PO-001: MV Power Skid — Purchase from Supplier',
                    'project': proj_name,
                    'cost_center': cost_center,
                    'warehouse': warehouse,
                }],
            })
            po.insert(ignore_permissions=True)
            po.submit()
            frappe.db.commit()
            po_name = po.name
            results['purchase_order'] = {
                'status': 'created_submitted',
                'name': po.name,
                'grand_total': po.grand_total,
                'status_val': po.status,
            }
        except Exception as e:
            results['purchase_order'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # PURCHASE RECEIPT
    # =========================================================
    existing_pr = frappe.get_all('Purchase Receipt',
        filters=[['title', 'like', 'UAT-ITS-RECEIPT%']],
        fields=['name'], limit=1)

    if existing_pr:
        results['purchase_receipt'] = {'status': 'exists', 'name': existing_pr[0]['name']}
    elif po_name:
        try:
            # Use make_purchase_receipt to create from PO
            from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
            pr = make_purchase_receipt(po_name)
            pr.title = 'UAT-ITS-RECEIPT-001: MV Power Skid Received'
            pr.project = proj_name
            for item in pr.items:
                item.qty = 1
                item.accepted_qty = 1
                item.rejected_qty = 0
                item.project = proj_name
            pr.insert(ignore_permissions=True)
            pr.submit()
            frappe.db.commit()
            results['purchase_receipt'] = {
                'status': 'created_submitted',
                'name': pr.name,
                'status_val': pr.status,
            }
        except Exception as e:
            results['purchase_receipt'] = {'status': 'error', 'error': str(e)}
    else:
        results['purchase_receipt'] = {'status': 'skipped', 'reason': 'No PO to make receipt from'}

    print(json.dumps(results, indent=2, default=str))
