import frappe
import json

def run():
    results = {}

    # =========================================================
    # PHASE 0: CLEANUP ORPHAN RECORDS
    # =========================================================

    # 1. Delete orphan Nada Ramy employees (null user_id)
    orphan_emps = frappe.get_all('Employee',
        filters=[['employee_name', 'like', '%Nada Ramy%'], ['user_id', 'is', 'not set']],
        fields=['name', 'employee_name'])
    deleted_emps = []
    for emp in orphan_emps:
        try:
            frappe.delete_doc('Employee', emp['name'], force=True, ignore_permissions=True)
            deleted_emps.append(emp['name'])
        except Exception as e:
            deleted_emps.append(f"ERROR deleting {emp['name']}: {str(e)}")
    results['deleted_orphan_employees'] = deleted_emps

    # 2. Delete orphan UAT projects with random suffixes (not UAT-ITS-PSS-001 etc)
    orphan_projects = frappe.get_all('Project',
        filters=[['project_name', 'like', 'UAT-ITS Project %']],
        fields=['name', 'project_name'])
    deleted_projects = []
    for proj in orphan_projects:
        try:
            frappe.delete_doc('Project', proj['name'], force=True, ignore_permissions=True)
            deleted_projects.append(proj['name'])
        except Exception as e:
            deleted_projects.append(f"ERROR deleting {proj['name']}: {str(e)}")
    results['deleted_orphan_projects'] = deleted_projects

    # 3. Delete orphan UAT customers with non-standard names
    orphan_customers = frappe.get_all('Customer',
        filters=[['customer_name', 'like', 'UAT-ITS-Client%']],
        fields=['name', 'customer_name'])
    deleted_customers = []
    for cust in orphan_customers:
        try:
            frappe.delete_doc('Customer', cust['name'], force=True, ignore_permissions=True)
            deleted_customers.append(cust['name'])
        except Exception as e:
            deleted_customers.append(f"ERROR deleting {cust['name']}: {str(e)}")
    results['deleted_orphan_customers'] = deleted_customers

    # =========================================================
    # PHASE 1: CREATE NADA RAMY EMPLOYEE
    # =========================================================

    # Check if already exists properly
    existing = frappe.get_all('Employee',
        filters={'user_id': 'nada.ramy@its-operations.com'},
        fields=['name', 'employee_name', 'status'])

    if existing:
        results['nada_employee'] = {'status': 'already_exists', 'record': existing[0]}
    else:
        try:
            emp = frappe.get_doc({
                'doctype': 'Employee',
                'employee_name': 'Nada Ramy',
                'user_id': 'nada.ramy@its-operations.com',
                'company': 'BetaEdge (Demo)',
                'department': 'Operations',
                'designation': 'Engineer',
                'status': 'Active',
                'date_of_joining': '2024-01-01',
                'employment_type': 'Full-time',
                'gender': 'Female',
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
            results['nada_employee'] = {'status': 'error', 'error': str(e)}

    # =========================================================
    # PHASE 2: ADD MISSING ROLES TO NADA USER
    # =========================================================

    required_roles = [
        'System Manager', 'Projects Manager', 'Projects User',
        'Accounts Manager', 'Accounts User', 'Purchase Manager', 'Purchase User',
        'Stock Manager', 'Stock User', 'HR Manager', 'HR User',
        'Quality Manager', 'Manufacturing Manager', 'Manufacturing User',
        'Portal Administrator', 'Project Manager', 'Procurement Manager',
        'Finance Manager', 'Sales Manager', 'Item Manager',
        'Sales Master Manager', 'Equipment Manager', 'Fabrication Manager'
    ]

    try:
        user = frappe.get_doc('User', 'nada.ramy@its-operations.com')
        current_roles = [r.role for r in user.roles]
        added_roles = []

        for role in required_roles:
            if role not in current_roles:
                # Check role exists
                if frappe.db.exists('Role', role):
                    user.append('roles', {'role': role})
                    added_roles.append(role)

        user.save(ignore_permissions=True)
        frappe.db.commit()

        results['nada_roles'] = {
            'status': 'updated',
            'roles_added': added_roles,
            'total_roles': [r.role for r in user.roles]
        }
    except Exception as e:
        results['nada_roles'] = {'status': 'error', 'error': str(e)}

    print(json.dumps(results, indent=2, default=str))
