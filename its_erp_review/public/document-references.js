/* Project identity is stored on every record; contract and PO are optional references. */
(()=>{
 const keys={};
 for(const s of Object.values(SCHEMAS)){
  const contract=s.fields.find(f=>['contractNumber','agreementNo','contractNo'].includes(f.key));
  const po=s.fields.find(f=>['clientPO','purchaseOrder','purchaseRef','poNo'].includes(f.key));
  if(contract){contract.label='Contract No. (optional)';contract.required=false;}else s.fields.unshift(F('contractNo','Contract No. (optional)','text',false));
  if(po){po.label=po.key==='purchaseRef'?'PO No. (supplier purchase order)':'PO No.';po.required=false;}else s.fields.unshift(F('poNo','PO No.','text',false));
  keys[s.key]={contract:contract?.key||'contractNo',po:po?.key||'poNo'};
  const ref=keys[s.key];s.fields.sort((a,b)=>([ref.contract,ref.po].includes(a.key)?-1:0)-([ref.contract,ref.po].includes(b.key)?-1:0));
 }
 const priorNew=newDialog;newDialog=function(el){priorNew(el);const form=$('direct-document-form');if(!form)return;form.querySelector('label').insertAdjacentHTML('afterend','<div class="fields"><label class="field">Contract No. (optional)<input name="referenceContract" placeholder="Leave blank if there is no contract"></label><label class="field">PO No. (optional)<input name="referencePO" placeholder="Enter when available"></label></div>');};
 document.addEventListener('submit',e=>{if(e.target.id!=='direct-document-form'||!editDraft)return;const ref=keys[editDraft.type];if(!ref)return;const data=new FormData(e.target);editDraft.fields[ref.contract]=String(data.get('referenceContract')||'').trim();editDraft.fields[ref.po]=String(data.get('referencePO')||'').trim();const saved=records.find(r=>r.id===editDraft.id);if(saved){saved.fields[ref.contract]=editDraft.fields[ref.contract];saved.fields[ref.po]=editDraft.fields[ref.po];}render();});
 const oldDetails=details;details=function(r){return `<section class="notice info"><strong>Project No.: ${esc(r.project)}</strong><p>Contract No. can be left blank for projects without a contract. Enter the PO No. when available.</p></section>`+oldDetails(r);};
 const oldNext=createNext;createNext=function(r){const next=oldNext(r),a=keys[r.type],b=keys[next.type];if(a&&b){if(!next.fields[b.contract])next.fields[b.contract]=r.fields[a.contract]||'';if(!next.fields[b.po])next.fields[b.po]=r.fields[a.po]||'';}return next;};
})();

