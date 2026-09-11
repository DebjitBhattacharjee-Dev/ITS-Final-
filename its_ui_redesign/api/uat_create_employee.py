import frappe
import json

def run():
    results = {}

    # Check if already exists
    existing = frappe.get_all('Employee',
        filters={'user_id': 'nada.ramy@its-operations.com'},
        fields=['name', 'employee_name', 'status', 'department', 'designation', 'company'])

    if existing:
        results['nada_employee'] = {'status': 'already_exists', 'record': existing[0]}
        print(json.dumps(results, indent=2, default=str))
        return

    # Inspect Employee DocType required fields
    meta = frappe.get_meta('Employee')
    required_fields = [f.fieldname for f in meta.fields if f.reqd]
    results['required_fields'] = required_fields

    try:
        emp = frappe.get_doc({
            'doctype': 'Employee',
            'first_name': 'Nada',
            'last_name': 'Ramy',
            'employee_name': 'Nada Ramy',
            'user_id': 'nada.ramy@its-operations.com',
            'company': 'BetaEdge (Demo)',
            'department': 'Operations - BED',
            'designation': 'Engineer',
            'status': 'Active',
            'date_of_joining': '2024-01-01',
            'gender': 'Female',
            'date_of_birth': '1990-01-01',
        })
        emp.insert(ignore_permissions=True)
        frappe.db.commit()
        results['nada_employee'] = {
            'status': 'created',
            'name': emp.name,
            'employee_name': emp.employee_name,
            'user_id': emp.user_id,
            'department': emp.department,
            'designation': emp.designation,
            'company': emp.company,
            'date_of_joining': str(emp.date_of_joining),
        }
    except Exception as e:
        # Try without department if it fails
        try:
            emp = frappe.get_doc({
                'doctype': 'Employee',
                'first_name': 'Nada',
                'last_name': 'Ramy',
                'employee_name': 'Nada Ramy',
                'user_id': 'nada.ramy@its-operations.com',
                'company': 'BetaEdge (Demo)',
                'status': 'Active',
                'date_of_joining': '2024-01-01',
                'gender': 'Female',
                'date_of_birth': '1990-01-01',
            })
            emp.insert(ignore_permissions=True)
            frappe.db.commit()
            results['nada_employee'] = {
                'status': 'created_minimal',
                'name': emp.name,
                'employee_name': emp.employee_name,
                'user_id': emp.user_id,
                'company': emp.company,
            }
        except Exception as e2:
            results['nada_employee'] = {
                'status': 'error',
                'first_error': str(e),
                'second_error': str(e2)
            }

    print(json.dumps(results, indent=2, default=str))
