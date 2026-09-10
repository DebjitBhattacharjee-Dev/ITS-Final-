# ITS Project Operations (`its_ui_redesign`)

Custom Vue 3 Enterprise Portal for Construction and Project Operations built for ERPNext & Frappe Framework.

## Features
- **Custom Authentication**: Dedicated `/portal-access` sign-in page without using default `/login`.
- **Protected Shell**: `/portal` application shell with multi-level server and client security guards.
- **10 Workspaces**: Full coverage for Project Management, Estimation, Planning, Procurement, Inventory, HR, Fabrication, Progress & Billing, Accounting, and Reporting.
- **Warranty Architecture**: Product, Supplier, Subcontractor, Project Workmanship, and Defects Liability management.
- **Enterprise Dark Theme**: High density slate-950 visual theme matching design reference.

## Installation
```bash
bench get-app https://github.com/priyal-betaedge/its-new.git
bench --site <your-site> install-app its_ui_redesign
bench --site <your-site> migrate
```

## Development
```bash
cd apps/its_ui_redesign/portal
npm install
npm run dev
```

## Production Build
```bash
cd apps/its_ui_redesign/portal
npm run build
bench --site <your-site> build --app its_ui_redesign
```
