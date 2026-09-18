/* Explicit project entry points from the PSS landing page. */
(()=>{
 const before=powerDashboard;
 powerDashboard=function(){before();if(!powerCan())return;
  const projects=powerState.projects.filter(p=>p.project_type==='POWERSKID');
  $('view').querySelector('.page-heading')?.insertAdjacentHTML('afterend',`<section class="panel pad" style="margin-bottom:24px"><h2>Project Overview &amp; Skid Details</h2><p>Choose your project below to view its overview or add a skid.</p>${projects.map(p=>`<div class="split" style="padding:14px 0;border-bottom:1px solid var(--line)"><div><strong>${esc(p.id)} · ${esc(p.name)}</strong><p>${powerState.skids.filter(s=>s.projectId===p.id).length} skids registered</p></div><div class="actions"><button class="button" data-pss-overview="${esc(p.id)}">Open Overview</button><button class="button primary" data-pss-add-skid="${esc(p.id)}">+ Add skid / well</button></div></div>`).join('')||'<p>Create a PSS project first using + Create project.</p>'}</section>`);
 };
 document.addEventListener('click',e=>{const target=e.target.closest('[data-pss-overview],[data-pss-add-skid]');if(!target)return;const id=target.dataset.pssOverview||target.dataset.pssAddSkid;if(!powerCan()||!powerState.projects.some(p=>p.id===id&&p.project_type==='POWERSKID'))return;powerProject=id;powerTab='Overview';powerSkid='all';route='project/'+id;location.hash=route;render();if(target.hasAttribute('data-pss-add-skid'))powerEdit('skids');});
})();
