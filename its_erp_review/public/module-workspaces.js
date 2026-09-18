/* Consistent department entry points without changing document or project IDs. */
(()=>{
 const groups={
  0:[['Sales workflow',['rfi','inquiry','quotation','order']]],
  1:[['Planning & progress',['plan','task','dpr','projectClosure']],['PSS engineering',['engineering','skidRegister']]],
  2:[['Budgets & cost control',['estimate','variation']]],
  3:[['Purchasing',['material','supplierRFQ','purchase']],['Subcontracting',['subcontract']]],
  4:[['Shipment to delivery',['shipment','stock','delivery']]],
  5:[['Testing & acceptance',['inspection','punch','commission']]],
  6:[['People & time',['employee','timesheet','leave','holiday']],['Site readiness',['access']]],
  7:[['Workshop & equipment',['fabrication','asset']],['Maintenance & support',['maintenance','service']]],
  9:[['Management controls',['exception','generalException','template','approvalRule']]],
  10:[['Agreements & obligations',['contract','lineItemContract','obligation']]]
 };
 const descriptions={inquiry:'Register client requirements and supporting files.',quotation:'Prepare pricing, scope and commercial terms.',order:'Manage accepted orders and delivery commitments.',material:'Request materials for approved work.',supplierRFQ:'Request and compare supplier quotations.',purchase:'Create and follow purchase orders.',subcontract:'Manage subcontract scope and payment terms.',shipment:'Booking, tracking and customs clearance.',stock:'Receipts, movements, locations and condition.',delivery:'Plan transport and record delivery acceptance.',employee:'Create employee and manpower details.',timesheet:'Record time and supervisor review.',leave:'Request and review employee leave.',holiday:'Maintain the company holiday calendar.',access:'Track site passes and permit references.',contract:'Manage signed agreements and amendments.',obligation:'Track guarantees, obligations and expiry dates.'};
 const before=listPage;listPage=function(){before();if(!route.startsWith('module/'))return;const module=Number(route.split('/')[1]);if(module===8||!groups[module])return;
  const types=Object.values(SCHEMAS).filter(s=>s.module===module&&(filter.project==='all'||projectAllows(s.key,filter.project))&&(!POWER_ONLY.includes(s.key)||powerCan()));
  const chips=$('view').querySelector('.chips');if(!chips)return;
  chips.innerHTML=`<button class="chip ${filter.type==='all'?'active':''}" data-action="filter-type" data-type="all">All records</button>${module===10?`<button class="chip ${filter.type==='tender-documents'?'active':''}" data-tender-list>Tender Documents</button>`:''}${filter.type!=='all'&&filter.type!=='tender-documents'?`<span class="chip active">${esc(SCHEMAS[filter.type]?.label||filter.type)}</span>`:''}`;
  // Replace the previous department-specific shortcut panels with this common layout.
  if([4,6].includes(module))for(const h of $('view').querySelectorAll('section.panel h2'))if(['Logistics workflow','Employee / Manpower'].includes(h.textContent))h.closest('section').remove();
  const used=new Set(),sections=groups[module].map(([name,keys])=>[name,keys.map(k=>types.find(s=>s.key===k)).filter(Boolean)]);
  sections.forEach(([,schemas])=>schemas.forEach(s=>used.add(s.key)));const extra=types.filter(s=>!used.has(s.key));if(extra.length)sections.push(['Supporting records',extra]);
  chips.insertAdjacentHTML('afterend',`<section class="panel pad department-workspace" style="margin:18px 0"><h2>${esc(modules[module][0])} workspace</h2><p>Choose a task below to view its records or create a new entry.</p>${module===4?'<p>Shipment → Customs clearance → Receipt &amp; inspection → Site delivery → Signed proof of delivery</p>':''}${sections.filter(([,schemas])=>schemas.length).map(([label,schemas])=>`<h3>${esc(label)}</h3><div class="quick-grid">${schemas.map(s=>`<div class="workspace-task ${filter.type===s.key?'selected':''}"><button class="quick" data-action="filter-type" data-type="${s.key}"><strong>${esc(s.label)}</strong><small>${esc(descriptions[s.key]||'Manage details, documents and approval history.')}</small><small>${records.filter(r=>r.type===s.key&&(filter.project==='all'||r.project===filter.project)).length} records · Open →</small></button><button class="button" ${s.key==='employee'?'data-employee-add':`data-action="new" data-type="${s.key}" data-module="${module}" ${filter.project!=='all'?`data-project="${esc(filter.project)}"`:''}`}>+ ${s.key==='employee'?'Add employee / manpower':'Create '+esc(s.label)}</button></div>`).join('')}</div>`).join('')}</section>`);
  const create=$('view').querySelector('.page-heading [data-action="new"]');if(create&&SCHEMAS[filter.type]?.module===module){create.dataset.type=filter.type;create.textContent='+ Create '+SCHEMAS[filter.type].label;}
 };
})();
