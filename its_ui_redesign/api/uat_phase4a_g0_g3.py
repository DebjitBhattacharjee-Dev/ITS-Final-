import frappe
import json
from frappe.utils import today, add_days

def run():
    """Create G0 Opportunity and G1 RFQ only - no submit"""
    results = {}
    company = 'BetaEdge (Demo)'
    customer = 'UAT-ITS Customer'
    supplier = 'UAT-ITS Supplier'
    item_code = 'UAT-ITS-PSS-SKID-001'
    warehouse = 'Stores - BED'

    # G0: Opportunity
    existing_opp = frappe.get_all('Opportunity',
        filters=[['title', 'like', 'UAT-ITS-G0%']], fields=['name'], limit=1)
    if existing_opp:
        results['opportunity'] = {'status': 'exists', 'name': existing_opp[0]['name']}
    else:
        try:
            opp = frappe.get_doc({
                'doctype': 'Opportunity',
                'opportunity_from': 'Customer',
                'party_name': customer,
                'title': 'UAT-ITS-G0-ENQUIRY: MV Power Skid Supply & Commissioning',
                'opportunity_type': 'Sales',
                'status': 'Open',
                'transaction_date': today(),
                'close_date': add_days(today(), 30),
            })
            opp.insert(ignore_permissions=True)
            frappe.db.commit()
            results['opportunity'] = {'status': 'created', 'name': opp.name}
        except Exception as e:
            results['opportunity'] = {'status': 'error', 'error': str(e)}

    opp_name = results['opportunity'].get('name')

    # G1: Request for Quotation
    existing_rfq = frappe.get_all('Request for Quotation',
        filters=[['title', 'like', 'UAT-ITS-G1%']], fields=['name'], limit=1)
    if existing_rfq:
        results['rfq'] = {'status': 'exists', 'name': existing_rfq[0]['name']}
    else:
        try:
            rfq = frappe.get_doc({
                'doctype': 'Request for Quotation',
                'title': 'UAT-ITS-G1-SUPPLIER-RFQ: MV Power Skid',
                'transaction_date': today(),
                'status': 'Draft',
                'message_for_supplier': f'UAT-ITS-G1-SUPPLIER-RFQ. Opportunity ref: {opp_name}. Please quote for MV Power Skid.',
                'suppliers': [{'supplier': supplier}],
                'items': [{
                    'item_code': item_code,
                    'qty': 1,
                    'description': 'UAT-ITS-G1: MV Power Skid',
                    'warehouse': warehouse,
                }],
            })
            rfq.insert(ignore_permissions=True)
            frappe.db.commit()
            results['rfq'] = {'status': 'created', 'name': rfq.name}
        except Exception as e:
            results['rfq'] = {'status': 'error', 'error': str(e)}

    # G2: Supplier Quotation
    existing_sqtn = frappe.get_all('Supplier Quotation',
        filters=[['title', 'like', 'UAT-ITS-G2%']], fields=['name'], limit=1)
    if existing_sqtn:
        results['supplier_quotation'] = {'status': 'exists', 'name': existing_sqtn[0]['name']}
    else:
        try:
            sqtn = frappe.get_doc({
                'doctype': 'Supplier Quotation',
                'supplier': supplier,
                'title': 'UAT-ITS-G2-SUPPLIER-QTN',
                'transaction_date': today(),
                'valid_till': add_days(today(), 30),
                'company': company,
                'currency': 'AED',
                'buying_price_list': 'Standard Buying',
                'items': [{
                    'item_code': item_code,
                    'qty': 1,
                    'rate': 30000,
                    'description': 'UAT-ITS-G2: MV Power Skid — Supplier Quotation',
                    'schedule_date': add_days(today(), 60),
                    'warehouse': warehouse,
                }],
            })
            sqtn.insert(ignore_permissions=True)
            frappe.db.commit()
            results['supplier_quotation'] = {'status': 'created', 'name': sqtn.name}
        except Exception as e:
            results['supplier_quotation'] = {'status': 'error', 'error': str(e)}

    # G3: Customer Quotation (DO NOT SUBMIT - just save draft)
    existing_cqtn = frappe.get_all('Quotation',
        filters=[['title', 'like', 'UAT-ITS-G3%']], fields=['name', 'status'], limit=1)
    if existing_cqtn:
        results['customer_quotation'] = {'status': 'exists', 'name': existing_cqtn[0]['name'], 'docstatus': existing_cqtn[0]['status']}
    else:
        try:
            cqtn = frappe.get_doc({
                'doctype': 'Quotation',
                'quotation_to': 'Customer',
                'party_name': customer,
                'title': 'UAT-ITS-G3-CUST-QTN: MV Power Skid',
                'transaction_date': today(),
                'valid_till': add_days(today(), 30),
                'company': company,
                'currency': 'AED',
                'selling_price_list': 'Standard Selling',
                'order_type': 'Sales',
                'items': [{
                    'item_code': item_code,
                    'qty': 1,
                    'rate': 50000,
                    'description': 'UAT-ITS-G3: MV Power Skid Supply, Installation & Commissioning',
                }],
            })
            cqtn.insert(ignore_permissions=True)
            frappe.db.commit()
            results['customer_quotation'] = {
                'status': 'created_draft',
                'name': cqtn.name,
                'grand_total': cqtn.grand_total,
            }
        except Exception as e:
            results['customer_quotation'] = {'status': 'error', 'error': str(e)}

    print(json.dumps(results, indent=2, default=str))
