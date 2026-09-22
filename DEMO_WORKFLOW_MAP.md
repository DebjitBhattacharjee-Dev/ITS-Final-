# ITS ERP Business Workflow & Gate Architecture Map
**BRD v1.2 Compliant | End-to-End Governance Model**

---

## 1. Complete Business Lifecycle Map (G0 to G11)

```text
               +-------------------------------------------------------------+
               | PHASE 1: SELL IT (Commercial Acquisition)                   |
               +-------------------------------------------------------------+
                                              |
                                     [ G0: Enquiry & Opp ]
                                              |
                                    [ G1: Supplier RFQ ]
                                              |
                                 [ G2: Supplier Quotation ]
                                              |
                                 [ G3: Customer Quotation ]
                                              |
               +-------------------------------------------------------------+
               | PHASE 2: COMMIT & CONTRACT (Commercial Governance)          |
               +-------------------------------------------------------------+
                                              |
                                    [ G3.5: Contract EPC ]
                                              |
                                [ G4: Client PO Validation ]  <--- (HARD STOP 1)
                                              |
                                [ G5 / G5.5: Sales Order ]
                                              |
               +-------------------------------------------------------------+
               | PHASE 3: EXECUTION & BUY (Project & Sourcing)               |
               +-------------------------------------------------------------+
                                              |
                                [ G6: Finance Commitment ]    <--- (HARD STOP 2)
                                              |
                                [ G7: Supplier Purchase PO ]
                                              |
                                [ G7.5: Goods Staging / PR ]
                                              |
               +-------------------------------------------------------------+
               | PHASE 4: QUALITY & INSPECTION (Verification)                |
               +-------------------------------------------------------------+
                                              |
                                [ G8: FAT & IFAT Inspection ]
                                              |
                                  [ G8.5: Punch List Gate ]   <--- (HARD STOP 3)
                                              |
               +-------------------------------------------------------------+
               | PHASE 5: DELIVER & COMMISSION (Site Operations)             |
               +-------------------------------------------------------------+
                                              |
                                   [ G9: Delivery Match ]
                                              |
                                   [ G9.5: Delivery Note ]
                                              |
                             [ G9.6: Site Mobilization & SAT ] <--- (COMPLIANCE GATE)
                                              |
                                  [ G9.7: Project Handover ]
                                              |
               +-------------------------------------------------------------+
               | PHASE 6: INVOICE & SETTLEMENT (Financial Realization)       |
               +-------------------------------------------------------------+
                                              |
                                [ G10: Invoice Readiness ]    <--- (HARD STOP 4)
                                              |
                                  [ G10.5: Sales Invoice ]
                                              |
                                 [ Financial Settlement ]
                                              |
               +-------------------------------------------------------------+
               | PHASE 7: AFTER-SALES & MAINTENANCE (Support & Lifecycle)    |
               +-------------------------------------------------------------+
                                              |
                                [ G11: Warranty & Service ]
                                              |
                                    [ Final Closure ]
```

---

## 2. Granular Gate Governance Matrix

| Gate | Stage Name | Source Doc | Target Doc | Dept Owner | Approver Persona | Hard Stop Block Rule | Mandatory Evidence | Next Action |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **G0** | Customer Enquiry | Email / RFP | `Opportunity` | Sales | Sales Lead | Mandatory client reference | Client Specification, Scope BOQ | RFQ Issuance |
| **G1** | Supplier RFQ | `Opportunity` | `Request for Quotation` | Procurement | Procurement Lead | Item specifications required | Principal RFQ Document | Supplier Offer |
| **G2** | Supplier Quote | `Request for Quotation` | `Supplier Quotation` | Procurement | Procurement Manager | Pricing validity date check | Supplier Quotation PDF | Cost Modeling |
| **G3** | Customer Quote | `Opportunity` | `Quotation` | Sales | Management Approver | Margin threshold (<20% blocked) | Commercial Offer, Cost Sheet | Contract Prep |
| **G3.5**| Project Contract| `Quotation` | `Project Contract` | Contracts | Legal / Commercial Head | Mandatory terms & PBG clauses | Signed EPC Agreement | Client PO |
| **G4** | Client PO Val | `Quotation` / `Contract` | `Client PO Validation` | Contracts | Commercial Controller | **HARD STOP 1:** Mismatch in value/scope blocks Sales Order | Signed Customer Purchase Order | Order Entry |
| **G5.5**| Sales Order | `Client PO Validation` | `Sales Order` | Sales / PM | Sales Director | Cannot submit without Matched PO | Validated Client PO Record | Project Setup |
| **G6** | Finance Commit | `Project` / `Sales Order` | `Finance Commitment` | Finance | Finance Controller | **HARD STOP 2:** Unapproved commitment blocks Purchase Order | Cash Flow Impact Assessment | Release PO |
| **G7** | Purchase Order | `Finance Commitment` | `Purchase Order` | Procurement | Procurement Head | Requires budget commitment | Supplier Confirmation | Goods Receipt |
| **G7.5**| Goods Receipt | `Purchase Order` | `Purchase Receipt` | Warehouse | Logistics Supervisor | Packing list & test cert check | MTC, CoC, Commercial Invoice | Document Reg |
| **G8** | FAT / IFAT | `Project` / `Purchase Order` | `Factory Acceptance Test` | QA / QC | Inspection Lead | Any failing test stops delivery | Signed FAT Protocol by Witness | Punch Point |
| **G8.5**| Punch Clearance| `Factory Acceptance Test` | `Snag List` / `Review Punch` | QA / QC | QA Manager | **HARD STOP 3:** Open Category A snags block Delivery Note | Closure Photo & Inspection Sign-Off | Dispatch Release |
| **G9.5**| Delivery Note | `Sales Order` / `Snag List` | `Delivery Note` | Logistics | Warehouse Head | Blocked if critical punch open | Shipping Waybill & POD Receipt | Mobilization |
| **G9.6**| Mobilization | `Personnel Certificate` | `Commissioning Order` | HR / HSE | Operations Manager | **COMPLIANCE GATE:** Expired CICPA/H2S blocks site pass | Valid CICPA Pass & Medical Cert | SAT Execution |
| **G9.7**| Handover | `Commissioning Order` | `Project Handover` | Operations | Operations Director | Incomplete commissioning blocks CEP | Certificate of Performance (CEP) | Invoice Review |
| **G10** | Invoice Readiness| `Delivery Note` / `Handover` | `Invoice Readiness Check`| Finance / Billing | Finance Manager | **HARD STOP 4:** Missing DN or unsubmitted Handover blocks Invoice | Approved Handover & Signed POD | Tax Invoice |
| **G10.5**| Sales Invoice| `Invoice Readiness Check`| `Sales Invoice` | Finance | CFO / Chief Accountant | Blocked if G10 criteria unsatisfied| Official Tax Invoice | Bank Payment |
| **G11** | Warranty Service| `Project Warranty` | `Issue` / `Maintenance Visit` | Field Service | Service Manager | Out-of-warranty requires chargeable quote | Signed Customer Service Work Order | Case Closure |

---

## 3. Departmental Handoff & Segregation of Duties

The ITS operating model guarantees that no individual department can execute a transaction chain in isolation. Progression requires formal cross-functional handoffs:

| From Department | To Department | Handoff Trigger | Controlled Artefact | Compliance Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Sales / Proposals** | **Procurement** | Opportunity Requirement | `Request for Quotation` | Technical specification completeness verified |
| **Procurement** | **Sales / Proposals** | Supplier Commercial Offer | `Supplier Quotation` | Costing baseline and margin lock |
| **Sales / Proposals** | **Management** | Quotation Ready | `Quotation` (Approval Workflow) | Margin >= 30%, commercial conditions review |
| **Contracts** | **Sales / Operations** | Customer PO Received | `Client PO Validation` | Strict 10-point checklist mismatch check (Gate 1) |
| **Project Management**| **Finance** | Project Setup & Cost Plan | `Finance Commitment` | Cash flow alignment & exposure authorization (Gate 2) |
| **Finance** | **Procurement** | Approved Commitment | `Purchase Order` | Procurement release only with approved funds |
| **Procurement** | **QA / Document Control**| Component Assembly Staged| `Factory Acceptance Test` | Testing protocols witnessed by customer |
| **QA / Document Control**| **Warehouse / Logistics** | Punch List Clearance | `Snag List` (Closed) | No open critical defects before dispatch (Gate 3) |
| **Warehouse / Logistics**| **Field Operations** | Site Delivery Completed | `Delivery Note` + POD | Physical asset delivered to Well-X402 site |
| **HR / HSE** | **Field Operations** | Site Mobilization | `Personnel Certificate` | Valid CICPA passes and safety certificates |
| **Field Operations** | **Finance / Billing** | Custody Handover Signed | `Project Handover` + CEP | Customer acceptance certificate received |
| **Finance / Billing** | **Customer Accounts** | Invoicing Prerequisites Met| `Sales Invoice` | Gate 4 verified, tax invoice released |
| **Finance** | **After-Sales Support** | Final Payment Received | `Project Warranty` | 18-month warranty tracking begins |
| **After-Sales Support**| **Client Operations** | Warranty Service Event | `Maintenance Visit` | Resolution of warranty defects without cost |
