import frappe
import json

result = {}
result['site'] = frappe.local.site
result['frappe_version'] = frappe.__version__
result['installed_apps'] = frappe.get_installed_apps()

try:
    import erpnext
    result['erpnext_version'] = erpnext.__version__
except Exception as e:
    result['erpnext_version'] = str(e)

result['companies'] = frappe.get_all('Company', fields=['name', 'abbr', 'default_currency', 'country'])
result['default_company'] = frappe.defaults.get_global_default('company')

try:
    nu = frappe.get_doc('User', 'nada.ramy@its-operations.com')
    result['nada_user'] = {'name': nu.name, 'full_name': nu.full_name, 'enabled': nu.enabled, 'roles': [r.role for r in nu.roles]}
except Exception as e:
    result['nada_user'] = {'error': str(e)}

result['nada_employee'] = frappe.get_all('Employee', filters={'user_id': 'nada.ramy@its-operations.com'}, fields=['name', 'employee_name', 'user_id', 'status', 'department', 'designation', 'company', 'date_of_joining'])
result['nada_by_name'] = frappe.get_all('Employee', filters=[['employee_name', 'like', '%Nada%']], fields=['name', 'employee_name', 'user_id', 'status', 'department', 'designation', 'company'])
result['customers'] = frappe.get_all('Customer', fields=['name', 'customer_name', 'customer_type', 'customer_group'], limit=20)
result['suppliers'] = frappe.get_all('Supplier', fields=['name', 'supplier_name', 'supplier_group'], limit=20)
result['items'] = frappe.get_all('Item', fields=['name', 'item_name', 'item_group', 'stock_uom'], limit=20)
result['warehouses'] = frappe.get_all('Warehouse', fields=['name', 'warehouse_type', 'company', 'is_group'], limit=20)
result['projects'] = frappe.get_all('Project', fields=['name', 'project_name', 'status', 'customer', 'company'], limit=10)
result['cost_centers'] = frappe.get_all('Cost Center', fields=['name', 'is_group'], limit=10)
result['departments'] = [d['name'] for d in frappe.get_all('Department', fields=['name'], limit=20)]
result['designations'] = [d['name'] for d in frappe.get_all('Designation', fields=['name'], limit=20)]
result['item_groups'] = [ig['name'] for ig in frappe.get_all('Item Group', fields=['name'], limit=10)]
result['uoms'] = [u['name'] for u in frappe.get_all('UOM', fields=['name'], limit=10)]
result['custom_doctypes'] = [d['name'] for d in frappe.get_all('DocType', filters={'module': 'Its Ui Redesign', 'custom': 0}, fields=['name'])]
result['existing_uat'] = {}
for dt in ['Customer','Supplier','Opportunity','Quotation','Sales Order','Purchase Order','Project']:
    try:
        result['existing_uat'][dt] = [r['name'] for r in frappe.get_all(dt, filters=[['name', 'like', 'UAT-ITS%']], limit=5)]
    except Exception as e:
        result['existing_uat'][dt] = str(e)
result['open_opportunities'] = frappe.get_all('Opportunity', fields=['name','party_name','status'], limit=5)
result['open_quotations'] = frappe.get_all('Quotation', fields=['name','party_name','status','grand_total'], limit=5)
result['open_sales_orders'] = frappe.get_all('Sales Order', fields=['name','customer','status','grand_total'], limit=5)
result['open_purchase_orders'] = frappe.get_all('Purchase Order', fields=['name','supplier','status','grand_total'], limit=5)

print(json.dumps(result, indent=2, default=str))
