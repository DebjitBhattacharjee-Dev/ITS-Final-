# ITS ERP Demo Data Register
**Unified Demo Dataset — Dedicated Scenario Context (DEMO-ITS-2026-)**

---

## 1. Master Record Register (All 38 Transaction Steps)

The following register contains all live ERPNext MariaDB documents created for the ITS client demonstration. All records are interconnected in a single commercial and operational chain.

| Step | DocType | Record Name | Business Title / Tag | Status | Docstatus | Owner | Linked Parent | Next Expected Action |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **00** | `Customer` | `Demo Energy Customer` | Demo Energy Operating Co | Active | 0 | Administrator | — | Issue Opportunity |
| **00** | `Supplier` | `Demo Power Equipment Supplier` | Demo Power Principal Equipment | Active | 0 | Administrator | — | Issue Supplier RFQ |
| **00** | `Item` | `DEMO-PSS-SKID-400KVA` | 400 KVA MV Power Skid Unit | Enabled | 0 | Administrator | — | Quote & Procure |
| **01** | `Opportunity` | `CRM-OPP-2026-00016` | DEMO-ITS-2026-OPP-001 | Converted | 0 | `ahmed@betaedgetech.com` | `Demo Energy Customer` | Create Supplier RFQ |
| **03** | `Request for Quotation` | `PUR-RFQ-2026-00012` | DEMO-ITS-2026-RFQ-001 | Submitted | 1 | `ahmed@betaedgetech.com` | `CRM-OPP-2026-00016` | Receive Supplier Quote |
| **04** | `Supplier Quotation` | `PUR-SQTN-2026-00012`| DEMO-ITS-2026-SQTN-001 | Submitted | 1 | `ahmed@betaedgetech.com` | `PUR-RFQ-2026-00012` | Calculate Selling Cost |
| **05** | `Quotation` | `SAL-QTN-2026-00018` | DEMO-ITS-2026-QTN-001 | Approved | 1 | `ahmed@betaedgetech.com` | `CRM-OPP-2026-00016` | Prepare Project Contract |
| **07** | `Project Contract` | `PRJ-CON-2026-00029` | DEMO-ITS-2026-CON-001 | Approved | 0 | Administrator | `SAL-QTN-2026-00018` | Receive Client PO |
| **09** | `Client PO Validation`| `CPO-DE-2026-8801` | Client PO Checklist | Matched | 0 | Administrator | `SAL-QTN-2026-00018` | Authorize Sales Order |
| **11** | `Sales Order` | `SAL-ORD-2026-00026` | DEMO-ITS-2026-SO-001 | Submitted | 1 | `ahmed@betaedgetech.com` | `SAL-QTN-2026-00018` | Initialize Project |
| **12** | `Project` | `PROJ-0016` | DEMO-ITS-2026-PSS-001 | Open | 0 | Administrator | `SAL-ORD-2026-00026` | Create Review Project |
| **13** | `ITS Review Project` | `DEMO-ITS-2026-PSS-001`| 400 KVA Power Skid Well-X402 | Active | 0 | Administrator | `PROJ-0016` | Assign Skid Asset |
| **14** | `ITS Review Skid` | `DEMO-SKID-001` | SKID-400KVA-OIL-01 | Completed | 0 | Administrator | `DEMO-ITS-2026-PSS-001`| Track Sub-Assemblies |
| **15** | `Item (Component)` | `DEMO-VSD-PANEL` | Variable Speed Drive Panel | Enabled | 0 | Administrator | `DEMO-PSS-SKID-400KVA` | Assembly Integration |
| **15** | `Item (Component)` | `DEMO-TRANSFORMER-400KVA`| 400 KVA Step-Up Transformer | Enabled | 0 | Administrator | `DEMO-PSS-SKID-400KVA` | Assembly Integration |
| **15** | `Item (Component)` | `DEMO-PLC-PANEL` | Remote Telemetry & PLC Panel | Enabled | 0 | Administrator | `DEMO-PSS-SKID-400KVA` | Assembly Integration |
| **15** | `Item (Component)` | `DEMO-UPS-SYSTEM` | 24VDC Industrial Battery Cabinet | Enabled | 0 | Administrator | `DEMO-PSS-SKID-400KVA` | Assembly Integration |
| **16** | `Finance Commitment` | `FC-2026-00015` | Project Budget Commitment | Approved | 0 | `mohammed.finance@...` | `PROJ-0016` | Release Supplier PO |
| **17** | `Purchase Order` | `PUR-ORD-2026-00043` | DEMO-ITS-2026-PO-001 | Submitted | 1 | `ahmed@betaedgetech.com` | `PROJ-0016` | Goods Staging & Receipt |
| **19** | `Purchase Receipt` | `MAT-PRE-2026-00008` | DEMO-ITS-2026-PR-001 | Submitted | 1 | Administrator | `PUR-ORD-2026-00043` | Document Register Log |
| **20** | `ITS Review Document`| `DEMO-ITS-2026-DOC-001`| GA Drawing & SLD Rev B | Approved | 0 | Administrator | `DEMO-ITS-2026-PSS-001`| Engineering Query (RFI) |
| **21** | `Request for Info` | `RFI-2026-00030` | DEMO-ITS-2026-RFI-001 | Completed | 0 | Administrator | `PROJ-0016` | Execute Factory Test |
| **22** | `Factory Accept Test`| `FAT-2026-00002` | DEMO-ITS-2026-FAT-001 | Approved | 0 | Administrator | `PROJ-0016` | Integrated Testing |
| **23** | `Integrated FAT` | `IFAT-2026-00002` | DEMO-ITS-2026-IFAT-001 | Approved | 0 | Administrator | `PROJ-0016` | Punch List Inspection |
| **24** | `ITS Review Punch` | `DEMO-ITS-2026-PUNCH-001`| Paint Scratch & Warning Label | Closed | 0 | Administrator | `DEMO-ITS-2026-PSS-001`| Release Quality Block |
| **24** | `Snag List` | `SNAG-2026-00031` | DEMO-ITS-2026-SNAG-001 | Completed | 0 | Administrator | `PROJ-0016` | Prepare Dispatch |
| **26** | `Delivery Note` | `MAT-DN-2026-00006` | DEMO-ITS-2026-DN-001 | Submitted | 1 | Administrator | `SAL-ORD-2026-00026` | Attach POD & Mobilize |
| **29** | `Personnel Cert` | `CERT-2026-00001` | CICPA Pass & H2S Cert | Valid | 0 | `ali.hr@betaedgetech.com`| FSE Rashid Al Nuaimi | Site Gate Access |
| **28** | `ITS Review Comm` | `DEMO-ITS-2026-COMM-001`| On-Site Energization & SAT | Commissioned| 0 | Administrator | `DEMO-ITS-2026-PSS-001`| Client SAT Sign-Off |
| **32** | `Project Handover` | `HND-2026-00032` | DEMO-ITS-2026-HO-001 | Completed | 1 | Administrator | `PROJ-0016` | Final Dossier Sign-Off |
| **32** | `ITS Review Handover`| `DEMO-ITS-2026-HO-001` | Certificate of Performance | Accepted | 0 | Administrator | `DEMO-ITS-2026-PSS-001`| Unlock Invoicing Gate |
| **34** | `Sales Invoice` | `ACC-SINV-2026-00017`| DEMO-ITS-2026-SINV-001 | Submitted | 1 | `mohammed.finance@...` | `MAT-DN-2026-00006` | Customer Payment Entry |
| **35** | `Payment Entry` | `ACC-PAY-2026-00013` | DEMO-ITS-2026-PAY-001 | Submitted | 1 | `mohammed.finance@...` | `ACC-SINV-2026-00017` | Activate Warranty |
| **36** | `Project Warranty` | `PWR-2026-00033` | DEMO-ITS-2026-WAR-001 | Approved | 0 | Administrator | `PROJ-0016` | Service SLA Watch |
| **37** | `Issue` | `ISS-2026-00004` | DEMO-ITS-2026-MAINT-001 | Closed | 0 | Administrator | `Demo Energy Customer` | Assign Technician |
| **38** | `Maintenance Visit` | `MAT-MVS-2026-00001`| Warranty Sensor Calibration | Completed | 1 | Administrator | `Demo Energy Customer` | Service Record Signed |

---

## 2. Component Bill of Materials Breakdown

The main deliverable `DEMO-PSS-SKID-400KVA` incorporates 4 engineered sub-components:

| Component Code | Component Description | Sub-Supplier / Principal | Serial Number | Inspection Protocol |
| :--- | :--- | :--- | :--- | :--- |
| `DEMO-VSD-PANEL` | Variable Speed Drive Inverter (400 KVA MV) | Demo Power Principal | `SN-VSD-2026-402` | Loop & Harmonic Test |
| `DEMO-TRANSFORMER-400KVA` | 11kV/400V Oil-Immersed Step-Up Transformer | Demo Power Principal | `SN-TR-2026-881` | Megger & Oil Dielectric Test |
| `DEMO-PLC-PANEL` | Dual Redundant Remote Telemetry RTU Panel | Industrial Controls FZE | `SN-PLC-2026-104` | Modbus TCP & SCADA Test |
| `DEMO-UPS-SYSTEM` | 24VDC 100AH Industrial Battery Backup Rack | Power Systems LLC | `SN-UPS-2026-309` | 4-Hour Battery Discharge Test |

---

## 3. Financial & Commercial Lifecycle Reconciliation

* **Selling Value (Quotation & Sales Order):** AED 480,000.00
* **Direct Equipment Cost (Supplier PO & Receipt):** AED 320,000.00
* **Gross Commercial Margin:** AED 160,000.00 (**33.33%**)
* **Payment Terms Customer:** 30 Days Net from Commercial Invoice
* **Payment Terms Supplier:** 30 Days Net from Delivery Receipt
* **Invoiced Amount:** AED 480,000.00
* **Settled Amount:** AED 480,000.00 (`ACC-PAY-2026-00013`)
* **Outstanding Receivables Balance:** **AED 0.00**

---

## 4. Compliance & Site Safety Credentials

| Personnel Name | Role / Discipline | Document Type | Certificate Number | Issuing Authority | Expiry Date | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Rashid Al Nuaimi | Lead Commissioning FSE | CICPA Site Access Pass | `DEMO-ITS-2026-CERT-001` | CICPA Security Command | +365 Days | **Valid** |
| Rashid Al Nuaimi | Lead Commissioning FSE | H2S & Breathing Apparatus | `H2S-ADNOC-2026-441` | ADNOC HSE Academy | +365 Days | **Valid** |
| Rashid Al Nuaimi | Lead Commissioning FSE | Permit-to-Work (PTW) Signer| `PTW-LEVEL3-2026-19` | Operating Company HSE | +180 Days | **Valid** |
