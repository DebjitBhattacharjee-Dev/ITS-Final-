# Security & RBAC Governance Contract — `its_ui_redesign`

This document defines the permanent production authorization contract for the `its_ui_redesign` Frappe application and portal.

## 1. Core Authorization Principle
The custom portal is a direct, session-based UI frontend for Frappe/ERPNext. It relies 100% on native Frappe authentication (`frappe.session.user`) and Frappe's permission engine (Roles, DocType Permissions, User Permissions, Document-Level Permissions, and Workflows).

> **Golden Rule:**  
> - If ERPNext Desk denies an action/record, the portal MUST deny it.  
> - If ERPNext Desk permits an action/record, the portal permits it under the exact same session context.  
> - **NEVER solve an access issue by bypassing Frappe permissions (`ignore_permissions=True`).**

---

## 2. Mandatory Developer Guidelines

1. **Identity Source:**
   Always derive the authenticated identity from `frappe.session.user`. Never accept user identities from frontend parameters or impersonate Administrator for user requests.

2. **User-Facing Queries:**
   All user-facing queries must use permission-aware Frappe ORM methods (`frappe.get_list(..., ignore_permissions=False)`). Never use `frappe.get_all()` or raw `frappe.db.sql()` for user-facing data.

3. **Document Operations & CRUD:**
   Document opening (`get_document_detail`), creation (`save_document`), updates, deletions, submissions, cancellations, and PDF rendering must validate `frappe.has_permission(doctype, ptype, doc=name)` server-side.

4. **Dashboard Scoping:**
   Dashboard counts, sums, status distributions, and charts across all 10 workspaces must be computed over `frappe.get_list` to enforce record-level scoping (Company, Project, Warehouse, etc.).

5. **Administrative Endpoint Protection:**
   Whitelisted setup or maintenance endpoints (e.g. schema reloads) must be guarded with explicit role checks (`if "System Manager" not in frappe.get_roles(...)`).

6. **Governance Review:**
   Any new API endpoint or feature added to `its_ui_redesign` must be reviewed against this document to prevent permission drift.
