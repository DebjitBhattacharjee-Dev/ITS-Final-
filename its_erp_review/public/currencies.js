(()=>{
 for(const s of Object.values(SCHEMAS))if(s.lines||[0,3,8].includes(s.module)){const key=s.key==='invoice'?'invoiceCurrency':'currency';let f=s.fields.find(f=>f.key===key);if(!f){f=F(key,'Currency','select',false,['AED','USD','EUR','GBP']);s.fields.unshift(f);}Object.assign(f,{label:'Currency (EUR = EURO; GBP = STG / Sterling)',type:'select',required:false,options:['AED','USD','EUR','GBP']});for(const f of s.fields)if(['amount','price','rate'].includes(f.key))f.label=f.label.replace(' (AED)','');}
 const previousField=field;field=function(f,value,prefix){if(['invoiceCurrency','currency'].includes(f.key)){value=({EURO:'EUR',STG:'GBP'})[String(value).toUpperCase()]||value||'AED';}return previousField(f,value,prefix);};
 document.addEventListener('change',e=>{if(['f:invoiceCurrency','f:currency'].includes(e.target.name)&&editDraft){collect();recordPage(editDraft.id);}});
})();
