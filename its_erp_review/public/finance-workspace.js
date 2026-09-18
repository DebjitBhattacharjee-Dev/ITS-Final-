/* Clear finance navigation. Keep historical balance entries distinct from invoices. */
(()=>{
 SCHEMAS.invoice.label='Tax invoice';
 SCHEMAS.accountInvoice.label='Legacy invoice balance entry';
 FINANCE_TYPES.accountInvoice[0]='Legacy invoice balance entry';
 schema('proforma',8,'Proforma invoice (PI)','PI',[F('customer','Customer'),F('clientPO','Customer PO / reference','text',false),F('issueDate','Issue date','date'),F('validUntil','Valid until','date'),F('paymentTerms','Payment terms','textarea'),F('deliveryTerms','Delivery terms','textarea',false)],['Quotation / order reference'],'invoice',true);
 const sections=[
  ['Customer billing',[['invoice','Tax Invoices','Issue invoices with the approved A4 template.'],['proforma','Proforma Invoices (PI)','Prepare a payment request before the tax invoice.'],['creditNote','Credit Notes','Record customer or supplier credits.'],['debitNote','Debit Notes','Record adjustments and debit references.']]],
  ['Payments & collections',[['receiptVoucher','Receipts','Record money received.'],['paymentVoucher','Payments','Record money paid.'],['payment','Collection Follow-up','Track due dates and collection actions.'],['retention','Retention & Releases','Track retention and financial closure.']]],
  ['Supplier accounting & controls',[['supplierInvoice','Supplier Invoices','Review purchase order and receipt matching.'],['expense','Expenses & Reconciliation','Record expenses and reconciliation details.'],['payroll','Payroll Review','Review payroll evidence.'],['vatReview','VAT Review','Review tax-period schedules.'],['taxRegistration','Tax Registrations','Maintain registration references.'],['openingBalance','Opening Balances','Record account opening balances.']]]
 ];
 const oldList=listPage;listPage=function(){oldList();if(route!=='module/8')return;
  const chips=$('view').querySelector('.chips');
  if(chips)chips.innerHTML=`<button class="chip ${filter.type==='all'?'active':''}" data-action="filter-type" data-type="all">All records</button><a class="chip" href="#statements">Statements of Account (SOA)</a><a class="chip" href="#finance-reports">Financial Reports</a>${filter.type!=='all'?`<span class="chip active">${esc(SCHEMAS[filter.type]?.label||filter.type)}</span>`:''}`;
  const newButton=$('view').querySelector('[data-action="new"]');
  if(newButton&&filter.type!=='all'&&filter.type!=='accountInvoice'){newButton.dataset.type=filter.type;newButton.textContent='+ Create '+SCHEMAS[filter.type].label;}
  if(newButton&&filter.type==='accountInvoice')newButton.remove();
  chips?.insertAdjacentHTML('afterend',`<section class="panel pad" style="margin:18px 0"><h2>Billing &amp; Finance workspace</h2><p>Choose the document or task you need. All sections support your company’s projects.</p>${sections.map(([heading,entries])=>`<h3>${heading}</h3><div class="quick-grid">${entries.map(([type,label,description])=>`<button class="quick" data-action="filter-type" data-type="${type}" ${filter.type===type?'style="border-color:#F18716"':''}><strong>${label}</strong><small>${description}</small><small>${records.filter(r=>r.type===type).length} records · Open →</small></button>`).join('')}</div>`).join('')}<details style="margin-top:20px"><summary>Historical statement entries</summary><p>Earlier invoice balance entries are retained for statement history. Create new billing documents under Tax Invoices or Proforma Invoices.</p><button class="button" data-action="filter-type" data-type="accountInvoice">View legacy invoice balance entries</button></details></section>`);
 };
 const oldNew=newDialog;newDialog=function(el){oldNew(el);$('new-type-choice')?.querySelector('option[value="accountInvoice"]')?.remove();};
 const oldTable=table;table=function(rows){return oldTable(rows.map(r=>r.type==='accountInvoice'?{...r,title:'Legacy invoice balance entry · '+(r.fields.party||r.id)}:r));};
 const oldPage=recordPage;recordPage=function(id){oldPage(id);const r=recordBy(id);if(r?.type==='accountInvoice')$('view').querySelector('.page-heading')?.insertAdjacentHTML('afterend','<div class="notice">This is a historical statement balance entry, not a printable tax invoice. Use Billing &amp; Finance → Tax Invoices to create a billing document.</div>');if(r?.type==='proforma')$('view').querySelector('.page-heading')?.insertAdjacentHTML('afterend','<div class="notice">Proforma invoice — not a tax invoice. The approved PI print layout is awaiting your template.</div>');};
})();
