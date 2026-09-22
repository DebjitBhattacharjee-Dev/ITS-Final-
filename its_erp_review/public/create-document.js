/* Explicit document choice, project selection, then the editable form. */
(()=>{
 newDialog=function(el){
  const {type,module,project,test,source}=el.dataset;
  if(!type){const options=Object.values(SCHEMAS).filter(s=>s.key!=='accountInvoice'&&(module===undefined||s.module===Number(module))&&(!POWER_ONLY.includes(s.key)||powerCan()));modal(`<h2>What would you like to create?</h2><div class="quick-grid">${options.map(s=>`<button class="quick" data-action="new" data-type="${s.key}" ${project?`data-project="${esc(project)}"`:''} ${source?`data-source="${esc(source)}"`:''}><strong>+ Create ${esc(s.label)}</strong></button>`).join('')}</div>`);return;}
  const schema=SCHEMAS[type];if(!schema||type==='accountInvoice')return;
  const projects=PROJECTS.filter(p=>projectAllows(type,p.id)&&(p.project_type!=='POWERSKID'||powerCan()));
  modal(`<h2>Create ${esc(schema.label)}</h2><p>Select the project, then complete the document details and items.</p><form id="direct-document-form" data-type="${type}" data-test="${esc(test||'')}" data-source="${esc(source||'')}"><label class="field">Project<select name="project" required><option value="">Select a project…</option>${projects.map(p=>`<option value="${esc(p.id)}" ${p.id===project?'selected':''}>${esc(p.id)} · ${esc(p.name)}</option>`).join('')}</select></label><p id="direct-document-error" role="alert"></p><div class="form-actions"><button type="button" class="button" data-action="close">Cancel</button><button class="button primary">Continue to ${esc(schema.label)} details →</button></div></form>`);
 };
 document.addEventListener('submit',e=>{if(e.target.id!=='direct-document-form')return;e.preventDefault();const form=e.target,project=new FormData(form).get('project'),type=form.dataset.type,source=form.dataset.source||null;try{const r=makeRecord(type,project,source);r.title=SCHEMAS[type].label;if(type==='inspection'&&form.dataset.test)r.fields.testType=form.dataset.test;records.push(r);closeModal();route='record/'+r.id;recordTab='details';errors=[];editDraft=structuredClone(r);location.hash=route;render();window.scrollTo(0,0);notify('Complete the form, then Save draft or Save & submit.');}catch(err){$('direct-document-error').textContent=err.message;}});
 const before=listPage;listPage=function(){before();if(!route.startsWith('module/'))return;
  const generic=$('view').querySelector('.page-heading [data-action="new"]');if(generic&&!generic.dataset.type)generic.textContent='+ Create document';
  if(route==='module/8')for(const card of $('view').querySelectorAll('.quick-grid button[data-action="filter-type"]')){const type=card.dataset.type;if(!SCHEMAS[type])continue;const wrapper=document.createElement('div');wrapper.className='workspace-task';card.before(wrapper);wrapper.append(card);wrapper.insertAdjacentHTML('beforeend',`<button class="button primary" data-action="new" data-module="8" data-type="${type}">+ Create ${esc(SCHEMAS[type].label)}</button>`);}
 };
})();
