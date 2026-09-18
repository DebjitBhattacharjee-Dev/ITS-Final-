/* Shared record persistence. Never replace a newer database snapshot silently. */
(()=>{
 let ready=false,busy=false,revision=0,token='',saved='',failed=false;
 const status=document.createElement('div');status.className='demo-strip';status.setAttribute('role','status');status.innerHTML='Loading saved business records…';document.querySelector('main').prepend(status);
 const view=document.getElementById('view');view.inert=true;
 const fingerprint=()=>JSON.stringify(records);
 function show(message,error=false){status.replaceChildren(document.createTextNode(message));if(error){const exportButton=document.createElement('button');exportButton.className='button';exportButton.textContent='Export pending records';exportButton.onclick=()=>{const blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),revision,records},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='ITS-pending-records.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};status.append(exportButton);}}
 async function persist(){
  if(!ready||busy||failed||fingerprint()===saved)return;
  busy=true;const snapshot=fingerprint();show('Saving business records…');
  try{const response=await fetch('/api/records',{method:'PUT',headers:{'Content-Type':'application/json','X-ITS-Token':token},body:JSON.stringify({revision,records:JSON.parse(snapshot)})});const body=await response.json();if(!response.ok)throw Error(body.error||'Save failed.');revision=body.revision;saved=snapshot;show('Business records saved in the local database.');}
  catch(e){failed=true;show('Changes are NOT saved: '+e.message,true);}
  finally{busy=false;}
 }
 window.addEventListener('beforeunload',event=>{if(ready&&fingerprint()!==saved){event.preventDefault();event.returnValue='Changes have not been saved.';}});
 async function initialize(){
  try{const response=await fetch('/api/records');if(!response.ok)throw Error('Shared-record service unavailable. Restart the updated local server.');const body=await response.json();
   // The database is authoritative. Never add randomized demo samples on reload.
   saved=JSON.stringify(body.records);records=neutralSharedTitles(body.records);revision=body.revision;token=body.token;ready=true;view.inert=false;render();show('Business records loaded from the local database.');await persist();setInterval(persist,500);
  }catch(e){show(e.message+' Editing is disabled to protect saved records.',true);}
 }
 initialize();
})();

