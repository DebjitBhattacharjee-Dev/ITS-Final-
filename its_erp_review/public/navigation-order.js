/* Presentation order only: stable module IDs keep records and links intact. */
(()=>{
 const original=nav;
 nav=function(){
  original();
  const root=$('nav'),first=root.querySelector('a[href^="#module/"]');
  if(!first)return;
  const anchor=document.createElement('span');first.before(anchor);
  for(const id of [10,0,2,1,3,4,5,8,6,7,9]){
   const link=root.querySelector(`a[href="#module/${id}"]`);if(link)anchor.before(link);
  }
  anchor.remove();
 };
})();
