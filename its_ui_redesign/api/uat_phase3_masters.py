import frappe
import json

def run():
    results = {}
    company = 'BetaEdge (Demo)'
    abbr = 'BED'

    # =========================================================
    # PHASE 3: MASTER DATA VERIFICATION / CREATION
    # =========================================================

    # 1. Verify Customer
    customer_name = 'UAT-ITS Customer'
    if frappe.db.exists('Customer', customer_name):
        cust = frappe.get_doc('Customer', customer_name)
        results['customer'] = {
            'status': 'exists',
            'name': cust.name,
            'customer_name': cust.customer_name,
            'customer_group': cust.customer_group,
            'territory': cust.territory,
        }
    else:
        try:
            cust = frappe.get_doc({
                'doctype': 'Customer',
                'customer_name': customer_name,
                'customer_type': 'Company',
                'customer_group': 'Commercial',
                'territory': 'UAE',
            })
            cust.insert(ignore_permissions=True)
            results['customer'] = {'status': 'created', 'name': cust.name}
        except Exception as e:
            results['customer'] = {'status': 'error', 'error': str(e)}

    # 2. Verify Supplier
    supplier_name = 'UAT-ITS Supplier'
    if frappe.db.exists('Supplier', supplier_name):
        sup = frappe.get_doc('Supplier', supplier_name)
        results['supplier'] = {'status': 'exists', 'name': sup.name, 'supplier_group': sup.supplier_group}
    else:
        try:
            sup = frappe.get_doc({
                'doctype': 'Supplier',
                'supplier_name': supplier_name,
                'supplier_type': 'Company',
                'supplier_group': 'Local',
            })
            sup.insert(ignore_permissions=True)
            results['supplier'] = {'status': 'created', 'name': sup.name}
        except Exception as e:
            results['supplier'] = {'status': 'error', 'error': str(e)}

    # 3. Create/verify UAT Item
    item_code = 'UAT-ITS-PSS-SKID-001'
    if frappe.db.exists('Item', item_code):
        item = frappe.get_doc('Item', item_code)
        results['item'] = {'status': 'exists', 'name': item.name, 'item_name': item.item_name}
    else:
        try:
            item = frappe.get_doc({
                'doctype': 'Item',
                'item_code': item_code,
                'item_name': 'MV Power Skid - UAT',
                'item_group': 'Products',
                'stock_uom': 'Unit',
                'is_stock_item': 1,
                'is_sales_item': 1,
                'is_purchase_item': 1,
                'description': 'UAT-ITS: Medium Voltage Power Skid for end-to-end UAT testing',
                'standard_rate': 50000,
            })
            item.insert(ignore_permissions=True)
            frappe.db.commit()
            results['item'] = {'status': 'created', 'name': item.name}
        except Exception as e:
            # Try with minimal fields
            try:
                item = frappe.get_doc({
                    'doctype': 'Item',
                    'item_code': item_code,
                    'item_name': 'MV Power Skid - UAT',
                    'item_group': 'Products',
                    'stock_uom': 'Unit',
                    'is_stock_item': 1,
                    'description': 'UAT-ITS: MV Power Skid',
                })
                item.insert(ignore_permissions=True)
                frappe.db.commit()
                results['item'] = {'status': 'created_minimal', 'name': item.name}
            except Exception as e2:
                results['item'] = {'status': 'error', 'error': str(e), 'error2': str(e2)}

    # 4. Check Contact for UAT-ITS Customer
    contacts = frappe.get_all('Dynamic Link',
        filters={'link_doctype': 'Customer', 'link_name': customer_name, 'parenttype': 'Contact'},
        fields=['parent'])
    if contacts:
        results['contact'] = {'status': 'exists', 'name': contacts[0]['parent']}
    else:
        try:
            contact = frappe.get_doc({
                'doctype': 'Contact',
                'first_name': 'UAT',
                'last_name': 'Contact',
                'email_ids': [{'email_id': 'uat-contact@its-customer.com', 'is_primary': 1}],
                'phone_nos': [{'phone': '+971-50-000-0001', 'is_primary_phone': 1}],
                'links': [{'link_doctype': 'Customer', 'link_name': customer_name}],
            })
            contact.insert(ignore_permissions=True)
            frappe.db.commit()
            results['contact'] = {'status': 'created', 'name': contact.name}
        except Exception as e:
            results['contact'] = {'status': 'error', 'error': str(e)}

    # 5. Check Address for UAT-ITS Customer
    addresses = frappe.get_all('Dynamic Link',
        filters={'link_doctype': 'Customer', 'link_name': customer_name, 'parenttype': 'Address'},
        fields=['parent'])
    if addresses:
        results['address'] = {'status': 'exists', 'name': addresses[0]['parent']}
    else:
        try:
            addr = frappe.get_doc({
                'doctype': 'Address',
                'address_title': f'{customer_name} - UAE Office',
                'address_type': 'Billing',
                'address_line1': 'UAT Building, Industrial Area',
                'city': 'Abu Dhabi',
                'country': 'United Arab Emirates',
                'links': [{'link_doctype': 'Customer', 'link_name': customer_name}],
            })
            addr.insert(ignore_permissions=True)
            frappe.db.commit()
            results['address'] = {'status': 'created', 'name': addr.name}
        except Exception as e:
            results['address'] = {'status': 'error', 'error': str(e)}

    # 6. Check available Warehouse
    warehouses = frappe.get_all('Warehouse',
        filters={'company': company, 'is_group': 0},
        fields=['name', 'warehouse_name'])
    results['warehouses'] = warehouses

    # 7. Check cost centers
    cost_centers = frappe.get_all('Cost Center',
        filters={'company': company, 'is_group': 0},
        fields=['name'])
    results['cost_centers'] = cost_centers

    # 8. Inspect custom DocTypes fields for key ITS-specific ones
    custom_dt_fields = {}
    for dt in ['Project Contract', 'Factory Acceptance Test', 'Integrated Factory Acceptance Test',
               'Snag List', 'Request for Information', 'Project Handover', 'Project Warranty', 'Progress Claim']:
        try:
            meta = frappe.get_meta(dt)
            custom_dt_fields[dt] = {
                'fields': [{'fieldname': f.fieldname, 'fieldtype': f.fieldtype, 'label': f.label, 'reqd': f.reqd}
                           for f in meta.fields if f.fieldtype not in ['Section Break', 'Column Break', 'HTML', 'Tab Break']],
                'autoname': getattr(meta, 'autoname', None),
                'module': getattr(meta, 'module', None),
            }
        except Exception as e:
            custom_dt_fields[dt] = {'error': str(e)}
    results['custom_doctype_fields'] = custom_dt_fields

    print(json.dumps(results, indent=2, default=str))
