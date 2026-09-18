/* Shared validation and aggregation: browser and local API use the same rules. */
(function(root){
const TYPES=['TRADING','POWERSKID'];
const TEST_STATUS=['Not Planned','Planned','Ready','In Progress','Completed with Punch','Completed','Rejected / Retest Required'];
const COMMISSION_STATUS=['Site Not Ready','Site Ready','FSE Mobilization Planned','FSE Mobilized','Pre-Commissioning','SAT','Commissioning In Progress','Punch Pending','Commissioned','Handover Pending','Handed Over'];
const DOC_CATEGORIES=['Personnel Documents','Vehicle Documents','Drawings','Datasheets','Control Narrative','Cause & Effect','PLC Documents','VFD Documents','Transformer Documents','Switchgear Documents','UPS Documents','F&G Documents','HVAC Documents','FAT Documents','IFAT Documents','SAT Documents','Commissioning Documents','Punch Closure Documents','As-Built Documents','Handover Documents','RCA / Technical Reports'];
const fields={
 skids:{number:'Skid number',well:'Well number',serial:'Serial number',skidType:'Skid type',rating:'Rating',location:'Current location',status:['Not Started','In Progress','Completed']},
 equipment:{name:'Equipment / tag',category:['VFD / VSD','PLC / Control Panel','Transformer','Switchgear','UPS','HVAC','Fire & Gas System','Junction Box','Auxiliary','Skid Structure','Cabling','Other'],supplier:'Supplier reference',serial:'Serial number',status:['Required','Ordered','Received','Installed','Tested']},
 events:{test:['Internal Testing','FAT','IFAT','SAT'],plannedDate:'date',actualDate:'date',location:'Location',witness:'Witness / client',status:TEST_STATUS,result:'Test results',remarks:'Remarks'},
 punches:{source:['FAT','IFAT','SAT','Commissioning','Client Inspection','Other'],category:'Category',description:'Description',responsible:'Responsible party',assigned:'Assigned person',raisedDate:'date',targetDate:'date',priority:['Normal','High','Critical'],status:['Open','In Progress','Pending Client','Ready for Closure','Closed'],closureRemarks:'Closure remarks',evidence:'Closure evidence reference',closedDate:'date'},
 commissioning:{status:COMMISSION_STATUS,plannedDate:'date',commissioningDate:'date',engineer:'Field service engineer',remarks:'Remarks'},
 documents:{driverName:'Driver Name',vehicleName:'Vehicle Name',plateNumber:'Plate Number',supplierName:'Supplier Name (hired vehicle)',holder:'Person name / vehicle registration',role:'Role (FSE / Engineer / Technician / Driver)',documentType:'Document type (CICPA / ADNOC passport / RAG / Other)',expiryDate:'date',documentNumber:'Document number',discipline:'Discipline',transmittal:'Transmittal number',owner:'Document controller / owner',submittedDate:'date',reviewDue:'date',reviewComments:'Review comments',category:DOC_CATEGORIES,title:'Document title',reference:'File / document reference',revision:'Revision',status:['Draft','Submitted','Approved','Returned']},
 activities:{stage:'Workflow stage',title:'Activity title',owner:'Responsible person',plannedDate:'date',actualDate:'date',status:['Not Started','In Progress','Completed','Blocked'],remarks:'Remarks'},
 handovers:{status:['Not Started','Dossier In Progress','Submitted','Accepted'],cep:'CEP / handover reference',date:'date',remarks:'Remarks'}
};
const required={skids:['number','well','status'],equipment:['name','category','status'],events:['test','status'],punches:['source','description','responsible','assigned','raisedDate','targetDate','status'],commissioning:['status'],documents:['title','category','reference','status'],activities:['stage','title','status'],handovers:['status']};
const workflows={TRADING:['Customer Requirement','Quotation','Customer PO / Order','Purchase from Supplier','Material Receipt','Delivery','Sales / Invoice','Project Closure'],POWERSKID:['Project Award','Engineering','Document Submission / Approval','Procurement','Material Receipt','Integration','Internal Testing','FAT Preparation','FAT','FAT Punch Closure','IFAT Preparation','IFAT','IFAT Punch Closure','Delivery','Site Readiness','SAT','Commissioning','Commissioning Punch Closure','Handover / CEP','Project Completion']};
const permissions=['view','create','edit','engineering','fat','ifat','punch','commissioning','handover','admin'].map(x=>'powerskid.'+x);
function blank(projects=[]){return {version:1,projects:projects.map(p=>({...p,project_type:p.project_type||(p.kind==='skid'?'POWERSKID':'TRADING')})),workflows:structuredClone(workflows),...Object.fromEntries(Object.keys(fields).map(k=>[k,[]])),history:[]};}
function check(state){
 const fail=m=>{throw Error(m)},ids=new Set();
 if(!state||!Array.isArray(state.projects))fail('Invalid workspace.');
 const all=state.projects.concat(...Object.keys(fields).map(k=>state[k]||[]));
 for(const r of all){if(!r.id||!/^[A-Za-z0-9_-]+$/.test(r.id)||ids.has(r.id))fail('Unique safe record IDs are required.');ids.add(r.id);}
 for(const p of state.projects){if(!TYPES.includes(p.project_type)||!p.name?.trim()||!p.customer?.trim())fail('Project type, name and customer are required.');}
 for(const type of TYPES){const path=state.workflows?.[type];if(!Array.isArray(path)||!path.length||path.some(x=>typeof x!=='string'||!x.trim())||new Set(path).size!==path.length)fail('Workflow stages must be nonempty and unique.');}
 for(const [kind,defs] of Object.entries(fields)){
  if(!Array.isArray(state[kind]))fail('Missing '+kind+' collection.');
  for(const r of state[kind]){
   const p=state.projects.find(p=>p.id===r.projectId);if(!p)fail('Unknown project.');
   if(p.project_type!=='POWERSKID')fail('PowerSkid records require project_type POWERSKID.');
   if(kind!=='skids'&&(r.skidId||!['documents','activities'].includes(kind))&&!state.skids.some(s=>s.id===r.skidId&&s.projectId===p.id))fail('Select a skid belonging to this project.');
   for(const key of required[kind])if(!String(r[key]??'').trim())fail(key+' is required.');
   for(const [key,def] of Object.entries(defs)){if(Array.isArray(def)&&!def.includes(r[key]))fail('Invalid '+key+'.');if(def==='date'&&r[key]&&(!/^\d{4}-\d{2}-\d{2}$/.test(r[key])||new Date(r[key]+'T00:00:00Z').toISOString().slice(0,10)!==r[key]))fail('Invalid '+key+'.');}
   for(const [key,target] of [['eventId','events'],['equipmentId','equipment'],['punchId','punches'],['commissioningId','commissioning']])if(r[key]){const other=state[target].find(x=>x.id===r[key]);if(!other||other.projectId!==r.projectId||(r.skidId&&other.skidId!==r.skidId))fail('Linked records must belong to the same project and skid.');}
   if(kind==='documents'&&r.previousRevisionId){const prior=state.documents.find(d=>d.id===r.previousRevisionId);if(!prior||prior.projectId!==r.projectId||prior.skidId!==r.skidId||prior.id===r.id)fail('Select a previous revision in the same project and skid.');if(!r.revision||r.revision===prior.revision)fail('Enter a different revision identifier.');if(state.documents.some(d=>d.id!==r.id&&d.previousRevisionId===prior.id))fail('A newer revision already exists. Revise the latest record.');}
   if(kind==='events'&&['Completed','Completed with Punch'].includes(r.status)&&(!r.actualDate||!r.result))fail('Completed tests require actual date and results.');
   if(kind==='events'&&r.status==='Completed'&&state.punches.some(p=>p.eventId===r.id&&p.status!=='Closed'))fail('Close linked punches or use Completed with Punch.');
   if(kind==='punches'&&r.status==='Closed'&&(!r.closedDate||!r.evidence||!r.closureRemarks))fail('Punch closure requires date, remarks and evidence.');
   if(kind==='punches'&&r.closedDate&&r.closedDate<r.raisedDate)fail('Closure cannot precede the raised date.');
   if(kind==='commissioning'&&['Commissioned','Handover Pending','Handed Over'].includes(r.status)&&!r.commissioningDate)fail('Record a separate commissioning date.');
   if(kind==='handovers'&&r.status==='Accepted'&&(!r.cep||!r.date))fail('Accepted handover requires CEP reference and date.');
   if(kind==='handovers'&&r.status==='Accepted'&&(!state.commissioning.some(c=>c.skidId===r.skidId&&['Commissioned','Handover Pending','Handed Over'].includes(c.status))||state.punches.some(p=>p.skidId===r.skidId&&p.status!=='Closed')))fail('Handover requires commissioning and punch closure.');
  }
 }
 for(const s of state.skids)if(state.skids.some(o=>o.id!==s.id&&o.projectId===s.projectId&&o.number===s.number))fail('Skid number already exists in this project.');
 return state;
}
function latest(rows){return rows.at(-1)}
function metrics(state,projectId=null,today=new Date().toISOString().slice(0,10)){
 const projects=state.projects.filter(p=>p.project_type==='POWERSKID'&&(!projectId||p.id===projectId));const pids=new Set(projects.map(p=>p.id));
 const skids=state.skids.filter(s=>pids.has(s.projectId)),punches=state.punches.filter(s=>pids.has(s.projectId));
 const test=(s,t)=>latest(state.events.filter(e=>e.skidId===s.id&&e.test===t))?.status;
 const commission=s=>latest(state.commissioning.filter(e=>e.skidId===s.id))?.status;
 const delivered=s=>state.activities.some(a=>a.skidId===s.id&&a.stage==='Delivery'&&a.status==='Completed');
 return {projects:projects.length,skids:skids.length,wells:new Set(skids.map(s=>s.projectId+':'+s.well)).size,integration:skids.filter(s=>s.status==='In Progress').length,fatPending:skids.filter(s=>test(s,'FAT')!=='Completed').length,fatCompleted:skids.filter(s=>test(s,'FAT')==='Completed').length,ifatPending:skids.filter(s=>test(s,'IFAT')!=='Completed').length,ifatCompleted:skids.filter(s=>test(s,'IFAT')==='Completed').length,delivered:skids.filter(delivered).length,commissionPending:skids.filter(s=>!['Commissioned','Handover Pending','Handed Over','Commissioning In Progress'].includes(commission(s))).length,commissionInProgress:skids.filter(s=>commission(s)==='Commissioning In Progress').length,commissioned:skids.filter(s=>['Commissioned','Handover Pending','Handed Over'].includes(commission(s))).length,punchOpen:punches.filter(p=>p.status!=='Closed').length,punchClosed:punches.filter(p=>p.status==='Closed').length,punchOverdue:punches.filter(p=>p.status!=='Closed'&&p.targetDate<today).length};
}
function checkChanges(before,next){
 check(next);
 for(const kind of ['documents','commissioning','handovers'])for(const r of next[kind]){
  const old=before[kind].find(x=>x.id===r.id);if(JSON.stringify(old)===JSON.stringify(r))continue;
  if(kind==='documents'&&old?.status==='Approved')throw Error('Approved documents are locked. Create a new revision.');
  const same=x=>x.projectId===r.projectId&&x.skidId===r.skidId;
  if(kind==='commissioning'&&['Commissioned','Handover Pending','Handed Over'].includes(r.status)){
   if(latest(next.events.filter(x=>same(x)&&x.test==='SAT'))?.status!=='Completed')throw Error('Complete the latest SAT and close its punches before commissioning.');
   if(latest(next.activities.filter(x=>same(x)&&x.stage==='Site Readiness'))?.status!=='Completed')throw Error('Complete site readiness for this skid before commissioning.');
   if(next.punches.some(x=>same(x)&&x.status!=='Closed'))throw Error('Close skid punches before commissioning.');
   if(!next.documents.some(x=>same(x)&&x.category==='Commissioning Documents'&&x.status==='Approved'&&!next.documents.some(n=>n.previousRevisionId===x.id)))throw Error('Approve the current commissioning document before commissioning completion.');
  }
  if(kind==='handovers'&&r.status==='Accepted'){
   if(!['Commissioned','Handover Pending','Handed Over'].includes(latest(next.commissioning.filter(same))?.status))throw Error('The latest commissioning record must be complete.');
   for(const category of ['As-Built Documents','Handover Documents'])if(!next.documents.some(x=>same(x)&&x.category===category&&x.status==='Approved'&&!next.documents.some(n=>n.previousRevisionId===x.id)))throw Error('Approve the current '+category+' before handover acceptance.');
  }
 }
 return next;
}
for(const definition of Object.values(fields)){definition.contractNo='Contract No. (optional)';definition.poNo='PO No.';}
const api={TYPES,fields,required,workflows,permissions,blank,check,checkChanges,metrics,latest};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.PowerSkid=api;
})(globalThis);

