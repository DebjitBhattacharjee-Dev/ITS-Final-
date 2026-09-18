/* Show document currency at the first creation step in business departments. */
(()=>{
 const supported=s=>s&&(s.lines||[0,3,8].includes(s.module));
 const options=value=>[['AED','AED — UAE Dirham'],['USD','USD — US Dollar'],['EUR','EUR — Euro'],['GBP','GBP — STG / Sterling']].map(([code,label])=>`<option value="${code}" ${code===value?'selected':''}>${label}</option>`).join('');
 const oldNew=newDialog;newDialog=function(el){oldNew(el);const form=$('direct-document-form');if(!form||!supported(SCHEMAS[form.dataset.type]))return;form.querySelector('.form-actions').insertAdjacentHTML('beforebegin',`<label class="field">Document Currency <span class="required">*</span><select name="creationCurrency" required>${options('AED')}</select></label><p class="muted">Prices and amounts use this currency. Selecting a currency does not convert entered prices.</p>`);};
 let creatingCurrency=null;
 document.addEventListener('submit',e=>{if(e.target.id==='direct-document-form')creatingCurrency=new FormData(e.target).get('creationCurrency');},true);
 const oldMake=makeRecord;makeRecord=function(...args){const r=oldMake(...args);if(creatingCurrency&&supported(SCHEMAS[r.type]))r.fields[r.type==='invoice'?'invoiceCurrency':'currency']=creatingCurrency;return r;};
 document.addEventListener('submit',e=>{if(e.target.id==='direct-document-form')creatingCurrency=null;});
 const oldDetails=details;details=function(r){let html=oldDetails(r);if(!supported(SCHEMAS[r.type]))return html;const active=editDraft?.id===r.id?editDraft:r;return `<section class="notice info"><strong>Document Currency: ${esc(recordCurrency(active))}</strong><p>To change currency, use Edit details and choose Currency. Existing amounts are not converted.</p></section>`+html;};
 const oldList=listPage;listPage=function(){oldList();if(!['module/0','module/3','module/8'].includes(route))return;$('view').querySelector('.page-heading')?.insertAdjacentHTML('afterend','<p class="notice info"><strong>Currency selection:</strong> Click Create on your document, then choose AED, USD, EUR (Euro) or GBP (STG / Sterling). Existing documents: open the record → Edit details → Currency.</p>');};
})();
