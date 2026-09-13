import frappe
import json
from frappe import _

def check_admin_permission(permission_type="user"):
    if frappe.session.user == "Guest":
        frappe.response["http_status_code"] = 401
        frappe.throw(_("Unauthenticated"), frappe.AuthenticationError)
    
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" in roles or frappe.session.user == "Administrator":
        return True
    if permission_type == "user" and "User Manager" in roles:
        return True
    if permission_type == "role" and "Role Manager" in roles:
        return True
    
    frappe.response["http_status_code"] = 403
    frappe.throw(_("Permission Denied: System Manager or User Manager role required."), frappe.PermissionError)

def success_response(data, meta=None):
    res = {"success": True, "data": data}
    if meta is not None:
        res["meta"] = meta
    return res

def error_response(code, message, status_code=400):
    if status_code in (401, 403, 404):
        frappe.response["http_status_code"] = status_code
    return {
        "success": False,
        "error": {
            "code": code,
            "message": str(message)
        }
    }

# ==============================================================================
# 1. USER MANAGEMENT APIs
# ==============================================================================

@frappe.whitelist()
def get_users(search=None, role=None, enabled=None, user_type=None, page=1, page_length=20):
    check_admin_permission("user")
    
    filters = {}
    if enabled is not None and str(enabled).strip() != "":
        filters["enabled"] = 1 if str(enabled).lower() in ["1", "true"] else 0

    if user_type and str(user_type).strip() != "":
        filters["user_type"] = str(user_type).strip()

    page = int(page or 1)
    page_length = int(page_length or 20)
    start = (page - 1) * page_length

    if role and role.strip():
        user_roles = frappe.get_all("Has Role", filters={"role": role.strip()}, fields=["parent"])
        role_users = [r["parent"] for r in user_roles if r.get("parent")]
        if not role_users:
            return success_response([], {"total": 0, "page": page, "page_length": page_length})
        filters["name"] = ["in", role_users]

    or_filters = None
    if search and search.strip():
        s = search.strip()
        or_filters = [
            ["User", "email", "like", f"%{s}%"],
            ["User", "first_name", "like", f"%{s}%"],
            ["User", "last_name", "like", f"%{s}%"],
            ["User", "full_name", "like", f"%{s}%"]
        ]

    users = frappe.get_list(
        "User",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "email", "first_name", "last_name", "full_name", "enabled", "user_type", "user_image", "creation", "last_active", "last_login"],
        order_by="creation desc",
        start=start,
        page_length=page_length,
        ignore_permissions=False
    )

    user_names = [u["name"] for u in users]
    role_map = {}
    if user_names:
        roles_list = frappe.get_all(
            "Has Role",
            filters={"parent": ["in", user_names], "parenttype": "User"},
            fields=["parent", "role"]
        )
        for r in roles_list:
            role_map.setdefault(r["parent"], []).append(r["role"])

    for u in users:
        u["roles"] = role_map.get(u["name"], [])
        u["role_count"] = len(u["roles"])

    total_count = len(frappe.get_list("User", filters=filters, or_filters=or_filters, fields=["name"], limit_page_length=0, ignore_permissions=False))

    res = success_response(users, {
        "total": total_count,
        "page": page,
        "page_length": page_length
    })
    res["total_count"] = total_count
    return res

@frappe.whitelist()
def get_user_detail(user_id):
    check_admin_permission("user")
    if not frappe.db.exists("User", user_id):
        return error_response("NOT_FOUND", _("User {0} not found").format(user_id), 404)

    user_doc = frappe.get_doc("User", user_id)
    user_dict = {
        "name": user_doc.name,
        "email": user_doc.email,
        "first_name": user_doc.first_name,
        "middle_name": user_doc.middle_name,
        "last_name": user_doc.last_name,
        "full_name": user_doc.full_name,
        "enabled": user_doc.enabled,
        "user_type": user_doc.user_type,
        "language": user_doc.language,
        "time_zone": user_doc.time_zone,
        "send_welcome_email": user_doc.send_welcome_email,
        "user_image": user_doc.user_image,
        "creation": str(user_doc.creation),
        "last_active": str(user_doc.last_active) if getattr(user_doc, "last_active", None) else None,
        "last_login": str(user_doc.last_login) if getattr(user_doc, "last_login", None) else None,
        "modified": str(user_doc.modified)
    }

    assigned_roles = [r.role for r in user_doc.roles]
    
    # Native User Permissions
    user_perms = frappe.get_list(
        "User Permission",
        filters={"user": user_id},
        fields=["name", "user", "allow", "for_value", "is_default", "apply_to_all_doctypes", "applicable_for", "hide_descendants"],
        limit_page_length=0,
        ignore_permissions=False
    )

    # Dynamic Effective Access Summary
    effective_access = get_effective_user_access(user_id)

    return success_response({
        "user": user_dict,
        "roles": assigned_roles,
        "user_permissions": user_perms,
        "effective_access": effective_access
    })

@frappe.whitelist()
def save_user(user_data, roles=None, is_new=False):
    check_admin_permission("user")
    if isinstance(user_data, str):
        user_data = json.loads(user_data)
    if isinstance(roles, str):
        roles = json.loads(roles)

    email = (user_data.get("email") or user_data.get("name") or "").strip()
    if not email:
        return error_response("VALIDATION_ERROR", _("Email is mandatory for User creation"))

    creating_new = bool(is_new or not frappe.db.exists("User", email))

    if creating_new:
        if frappe.db.exists("User", email):
            return error_response("ALREADY_EXISTS", _("User with email {0} already exists").format(email), 409)

        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": user_data.get("first_name") or email.split("@")[0],
            "middle_name": user_data.get("middle_name") or "",
            "last_name": user_data.get("last_name") or "",
            "enabled": 1 if user_data.get("enabled", 1) else 0,
            "user_type": user_data.get("user_type") or "System User",
            "language": user_data.get("language") or "en",
            "time_zone": user_data.get("time_zone") or "Asia/Dubai",
            "send_welcome_email": 0
        })
        user_doc.insert(ignore_permissions=False)
    else:
        user_doc = frappe.get_doc("User", email)
        for key in ["first_name", "middle_name", "last_name", "enabled", "user_type", "language", "time_zone"]:
            if key in user_data:
                setattr(user_doc, key, user_data[key])

    if roles is not None and isinstance(roles, list):
        user_doc.set("roles", [])
        for r in roles:
            if frappe.db.exists("Role", r):
                user_doc.append("roles", {"role": r})
    
    user_doc.save(ignore_permissions=False)
    frappe.db.commit()

    email_sent = False
    email_error = None
    if creating_new:
        try:
            user_doc.send_welcome_mail_to_user()
            email_sent = True
        except Exception as e:
            email_error = str(e)

    return success_response({
        "name": user_doc.name,
        "email": user_doc.email,
        "full_name": user_doc.full_name,
        "roles": [r.role for r in user_doc.roles],
        "is_new": creating_new,
        "email_sent": email_sent,
        "email_error": email_error
    })

@frappe.whitelist()
def send_password_reset_email(user_id):
    check_admin_permission("user")
    if not frappe.db.exists("User", user_id):
        return error_response("NOT_FOUND", _("User {0} not found").format(user_id), 404)

    user_doc = frappe.get_doc("User", user_id)
    try:
        user_doc.send_welcome_mail_to_user()
        return success_response({"message": _("Password setup email sent to {0}").format(user_doc.email), "email": user_doc.email})
    except Exception as e:
        try:
            from frappe.core.doctype.user.user import reset_password
            reset_password(user_doc.name)
            return success_response({"message": _("Password reset email sent to {0}").format(user_doc.email), "email": user_doc.email})
        except Exception as e2:
            return error_response("EMAIL_ERROR", _("Could not send password setup email: {0}").format(str(e2)), 500)

@frappe.whitelist()
def set_user_password(user_id, new_password):
    check_admin_permission("user")
    if not frappe.db.exists("User", user_id):
        return error_response("NOT_FOUND", _("User {0} not found").format(user_id), 404)
    if not new_password or len(str(new_password).strip()) < 6:
        return error_response("VALIDATION_ERROR", _("Password must be at least 6 characters long"))

    from frappe.utils.password import update_password
    update_password(user_id, str(new_password).strip())
    frappe.db.commit()
    return success_response({"user": user_id, "message": _("Password updated successfully")})

@frappe.whitelist()
def set_user_enabled(user_id, enabled):
    check_admin_permission("user")
    if not frappe.db.exists("User", user_id):
        return error_response("NOT_FOUND", _("User {0} not found").format(user_id), 404)
    
    doc = frappe.get_doc("User", user_id)
    doc.enabled = 1 if str(enabled).lower() in ["1", "true"] else 0
    doc.save(ignore_permissions=False)
    frappe.db.commit()
    return success_response({"user": user_id, "enabled": doc.enabled})


# ==============================================================================
# 2. USER PERMISSIONS APIs
# ==============================================================================

@frappe.whitelist()
def add_user_permission(user_id, allow_doctype, for_value, is_default=0):
    check_admin_permission("user")
    if not frappe.db.exists("User", user_id):
        return error_response("NOT_FOUND", _("User {0} not found").format(user_id), 404)

    if not frappe.db.exists("DocType", allow_doctype):
        return error_response("NOT_FOUND", _("DocType {0} does not exist").format(allow_doctype), 404)

    # Check if permission already exists
    existing = frappe.db.exists("User Permission", {
        "user": user_id,
        "allow": allow_doctype,
        "for_value": for_value
    })
    if existing:
        return error_response("ALREADY_EXISTS", _("User Permission for {0}: {1} already exists").format(allow_doctype, for_value), 409)

    doc = frappe.get_doc({
        "doctype": "User Permission",
        "user": user_id,
        "allow": allow_doctype,
        "for_value": for_value,
        "is_default": 1 if is_default else 0,
        "apply_to_all_doctypes": 1
    })
    doc.insert(ignore_permissions=False)
    frappe.db.commit()

    return success_response({
        "name": doc.name,
        "user": doc.user,
        "allow": doc.allow,
        "for_value": doc.for_value,
        "is_default": doc.is_default
    })

@frappe.whitelist()
def delete_user_permission(perm_name):
    check_admin_permission("user")
    if not frappe.db.exists("User Permission", perm_name):
        return error_response("NOT_FOUND", _("User Permission {0} not found").format(perm_name), 404)

    frappe.delete_doc("User Permission", perm_name, ignore_permissions=False)
    frappe.db.commit()
    return success_response({"deleted": perm_name})

# ==============================================================================
# 3. ROLE MANAGEMENT & ROLE PERMISSION MATRIX APIs
# ==============================================================================

@frappe.whitelist()
def get_roles():
    check_admin_permission("role")
    roles = frappe.get_all(
        "Role",
        fields=["name", "role_name", "desk_access", "disabled"],
        order_by="name asc",
        ignore_permissions=False
    )
    return success_response(roles)

@frappe.whitelist()
def save_role(role_name, desk_access=1, disabled=0):
    check_admin_permission("role")
    if not role_name or not role_name.strip():
        return error_response("VALIDATION_ERROR", _("Role Name is mandatory"))
    
    name = role_name.strip()
    if frappe.db.exists("Role", name):
        doc = frappe.get_doc("Role", name)
        doc.desk_access = 1 if desk_access else 0
        doc.disabled = 1 if disabled else 0
        doc.save(ignore_permissions=False)
    else:
        doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": name,
            "desk_access": 1 if desk_access else 0,
            "disabled": 1 if disabled else 0
        })
        doc.insert(ignore_permissions=False)
    
    frappe.db.commit()
    return success_response({"role_name": doc.role_name, "desk_access": doc.desk_access, "disabled": doc.disabled})

@frappe.whitelist()
def get_role_users(role_name):
    check_admin_permission("role")
    if not role_name:
        return error_response("VALIDATION_ERROR", _("Role Name is required"))
    if not frappe.db.exists("Role", role_name):
        return error_response("NOT_FOUND", _("Role {0} not found").format(role_name), 404)

    # Fetch users who have this role via the Has Role child table
    role_assignments = frappe.get_list(
        "Has Role",
        filters={"role": role_name, "parenttype": "User"},
        fields=["parent"],
        limit_page_length=0,
        ignore_permissions=False
    )
    user_names = [r["parent"] for r in role_assignments if r.get("parent")]

    users = []
    if user_names:
        users = frappe.get_list(
            "User",
            filters={"name": ["in", user_names]},
            fields=["name", "email", "full_name", "enabled"],
            limit_page_length=0,
            ignore_permissions=False
        )

    return success_response(users)

@frappe.whitelist()
def get_role_permission_matrix(doctype=None, role=None):
    check_admin_permission("role")
    from frappe.core.page.permission_manager.permission_manager import get_permissions
    
    if not doctype or not role:
        return success_response([])

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} not found").format(doctype), 404)
    if not frappe.db.exists("Role", role):
        return error_response("NOT_FOUND", _("Role {0} not found").format(role), 404)

    perms = get_permissions(doctype=doctype, role=role)
    rules = [dict(p) for p in perms] if perms else []
    return success_response(rules)

@frappe.whitelist()
def update_role_permission(doctype, role, permlevel=0, ptype="read", value=0, if_owner=0):
    check_admin_permission("role")
    from frappe.core.page.permission_manager.permission_manager import update
    permlevel = int(permlevel or 0)
    if_owner = int(if_owner or 0)
    val = "1" if str(value).lower() in ["1", "true"] else "0"

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} not found").format(doctype), 404)
    if not frappe.db.exists("Role", role):
        return error_response("NOT_FOUND", _("Role {0} not found").format(role), 404)

    update(doctype, role, permlevel, ptype, val, if_owner=if_owner)
    frappe.db.commit()
    return success_response({"doctype": doctype, "role": role, "permlevel": permlevel, "ptype": ptype, "value": val, "if_owner": if_owner})

@frappe.whitelist()
def add_role_permission_rule(doctype, role, permlevel=0):
    check_admin_permission("role")
    from frappe.core.page.permission_manager.permission_manager import add
    permlevel = int(permlevel or 0)

    if not frappe.db.exists("DocType", doctype):
        return error_response("NOT_FOUND", _("DocType {0} not found").format(doctype), 404)
    if not frappe.db.exists("Role", role):
        return error_response("NOT_FOUND", _("Role {0} not found").format(role), 404)

    try:
        add(doctype, role, permlevel)
        frappe.db.commit()
    except Exception as e:
        return error_response("ADD_PERM_ERROR", str(e), 400)

    return success_response({"doctype": doctype, "role": role, "permlevel": permlevel})

@frappe.whitelist()
def delete_role_permission_rule(doctype, role, permlevel=0, if_owner=0):
    check_admin_permission("role")
    from frappe.core.page.permission_manager.permission_manager import remove
    permlevel = int(permlevel or 0)
    if_owner = int(if_owner or 0)

    try:
        remove(doctype, role, permlevel, if_owner=if_owner)
        frappe.db.commit()
    except Exception as e:
        return error_response("DELETE_PERM_ERROR", str(e), 400)

    return success_response({"doctype": doctype, "role": role, "permlevel": permlevel, "if_owner": if_owner})


# ==============================================================================
# 4. DYNAMIC EFFECTIVE ACCESS
# ==============================================================================

def get_effective_user_access(user_id):
    if not frappe.db.exists("User", user_id):
        return {}

    key_doctypes = [
        "Project", "Sales Order", "Purchase Order", "Sales Invoice", "Purchase Invoice",
        "Employee", "Material Request", "Stock Entry", "Delivery Note", "Task", "Timesheet"
    ]

    effective = {}
    for dt in key_doctypes:
        if frappe.db.exists("DocType", dt):
            try:
                meta = frappe.get_meta(dt)
                perms = frappe.permissions.get_role_permissions(meta, user=user_id)
                effective[dt] = {
                    "read": bool(perms.get("read")),
                    "create": bool(perms.get("create")),
                    "write": bool(perms.get("write")),
                    "delete": bool(perms.get("delete")),
                    "submit": bool(perms.get("submit"))
                }
            except Exception:
                effective[dt] = {"read": False, "create": False, "write": False, "delete": False, "submit": False}

    return effective
