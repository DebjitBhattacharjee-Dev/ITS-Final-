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

    # Get chain references
    proj_recs = frappe.get_all('Project', filters=[['project_name', 'like', 'UAT-ITS-PSS%']], fields=['name'], limit=1)
    proj_name = proj_recs[0]['name'] if proj_recs else None
    results['ref_project'] = proj_name

    so_recs = frappe.get_all('Sales Order', filters=[['title', 'like', 'UAT-ITS-SO%']], fields=['name', 'status'], limit=1)
    so_name = so_recs[0]['name'] if so_recs else None
    so_status = so_recs[0]['status'] if so_recs else None
    results['ref_sales_order'] = {'name': so_name, 'status': so_status}

    dn_recs = frappe.get_all('Delivery Note', filters=[['title', 'like', 'UAT-ITS-DN%']], fields=['name'], limit=1)
    dn_name = dn_recs[0]['name'] if dn_recs else None
    results['ref_delivery_note'] = dn_name

    # =========================================================
    # DELIVERY NOTE (from Sales Order)
    # =========================================================
    if not dn_name and so_name:
        try:
            # Get SO to check status
            so_doc = frappe.get_doc('Sales Order', so_name)
            if so_doc.docstatus == 1:  # submitted
                from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
                dn = make_delivery_note(so_name)
                dn.title = 'UAT-ITS-DN-001: MV Power Skid Delivery'
                dn.project = proj_name
                dn.lr_no = 'UAT-ITS-DN-001'
                dn.lr_date = today()
                for item in dn.items:
                    item.qty = 1
                    item.project = proj_name
                dn.insert(ignore_permissions=True)
                dn.submit()
                frappe.db.commit()
                dn_name = dn.name
                results['delivery_note'] = {
                    'status': 'created_submitted', 'name': dn.name, 'status_val': dn.status
                }
            else:
                results['delivery_note'] = {'status': 'skipped', 'reason': f'SO status: {so_doc.docstatus}'}
        except Exception as e:
            results['delivery_note'] = {'status': 'error', 'error': str(e)}
    else:
        results['delivery_note'] = {'status': 'exists' if dn_name else 'skipped_no_so', 'name': dn_name}

    # =========================================================
    # SALES INVOICE (from Sales Order + Delivery Note)
    # =========================================================
    sinv_recs = frappe.get_all('Sales Invoice', filters=[['title', 'like', 'UAT-ITS-SINV%']], fields=['name'], limit=1)
    sinv_name = sinv_recs[0]['name'] if sinv_recs else None

    if not sinv_name and so_name:
        try:
            from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
            sinv = make_sales_invoice(so_name)
            sinv.title = 'UAT-ITS-SINV-001: MV Power Skid Invoice'
            sinv.project = proj_name
            sinv.due_date = add_days(today(), 30)
            if dn_name:
                # Update delivery note reference on items
                for item in sinv.items:
                    item.delivery_note = dn_name
                    item.project = proj_name
            sinv.insert(ignore_permissions=True)
            sinv.submit()
            frappe.db.commit()
            sinv_name = sinv.name
            results['sales_invoice'] = {
                'status': 'created_submitted',
                'name': sinv.name,
                'grand_total': sinv.grand_total,
                'outstanding_amount': sinv.outstanding_amount,
                'status_val': sinv.status,
            }
        except Exception as e:
            results['sales_invoice'] = {'status': 'error', 'error': str(e)}
    else:
        results['sales_invoice'] = {'status': 'exists' if sinv_name else 'skipped_no_so', 'name': sinv_name}

    # =========================================================
    # PAYMENT ENTRY (against Sales Invoice)
    # =========================================================
    pay_recs = frappe.get_all('Payment Entry', filters=[['title', 'like', 'UAT-ITS-PAY%']], fields=['name'], limit=1)
    pay_name = pay_recs[0]['name'] if pay_recs else None

    if not pay_name and sinv_name:
        try:
            sinv_doc = frappe.get_doc('Sales Invoice', sinv_name)
            if sinv_doc.outstanding_amount > 0:
                from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
                pe = get_payment_entry('Sales Invoice', sinv_name)
                pe.title = 'UAT-ITS-PAY-001: Payment for MV Power Skid'
                pe.reference_no = 'UAT-ITS-TXN-001'
                pe.reference_date = today()
                pe.remarks = 'UAT-ITS-PAY-001: Full payment received for Sales Invoice ' + sinv_name
                pe.insert(ignore_permissions=True)
                pe.submit()
                frappe.db.commit()
                pay_name = pe.name
                results['payment_entry'] = {
                    'status': 'created_submitted',
                    'name': pe.name,
                    'paid_amount': pe.paid_amount,
                    'status_val': pe.status,
                }
            else:
                results['payment_entry'] = {'status': 'skipped', 'reason': 'No outstanding amount'}
        except Exception as e:
            results['payment_entry'] = {'status': 'error', 'error': str(e)}
    else:
        results['payment_entry'] = {'status': 'exists' if pay_name else 'skipped_no_invoice', 'name': pay_name}

    # =========================================================
    # Verify final Sales Invoice outstanding amount
    # =========================================================
    if sinv_name:
        try:
            sinv_final = frappe.get_doc('Sales Invoice', sinv_name)
            results['invoice_final_status'] = {
                'name': sinv_name,
                'grand_total': sinv_final.grand_total,
                'outstanding_amount': sinv_final.outstanding_amount,
                'status': sinv_final.status,
            }
        except Exception as e:
            results['invoice_final_status'] = {'error': str(e)}

    print(json.dumps(results, indent=2, default=str))
