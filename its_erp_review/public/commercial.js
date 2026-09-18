/* One shared Commercial entry per document type; individual records remain linked. */
(()=>{
 const previousUpdate=updateList;
 updateList=function(){
  previousUpdate();if(route!=='module/0'||filter.type!=='all')return;
  const rows=records.filter(r=>SCHEMAS[r.type]?.module===0&&(filter.project==='all'||r.project===filter.project)&&(filter.status==='all'||r.status===filter.status)&&(!filter.projectType||filter.projectType==='all'||projectOf(r)?.project_type===filter.projectType)&&`${r.id} ${r.title} ${r.owner} ${r.project}`.toLowerCase().includes(filter.query.toLowerCase()));
  $('record-list').innerHTML=`<div class="table-wrap"><table><thead><tr><th>Document type</th><th>Records</th><th>Action</th></tr></thead><tbody>${['rfi','inquiry','quotation','order'].map(type=>`<tr><td><strong>${esc(SCHEMAS[type].label)}</strong></td><td>${rows.filter(r=>r.type===type).length}</td><td><button class="button" data-action="filter-type" data-type="${type}">Open ${esc(SCHEMAS[type].label)}</button></td></tr>`).join('')}</tbody></table></div><p class="count-line">Select a document type to view or create records for any project.</p>`;
 };
})();
