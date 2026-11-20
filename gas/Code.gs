const FOLDER='1F78miQNTDb43_YJKfGlgcRiyHXN1JMcG', KEY='改成你的密碼', NAME='fan-ledger-backup.json';
function o_(x){return ContentService.createTextOutput(JSON.stringify(x)).setMimeType(ContentService.MimeType.JSON)}
function pf_(n){const it=DriveApp.getFolderById(FOLDER).getFilesByName(n);return it.hasNext()?it.next():null}
function save_(n,j){const f=pf_(n);f?f.setContent(j):DriveApp.getFolderById(FOLDER).createFile(n,j)}
const DRE=/^\d{4}-\d\d-\d\d$/, IRE=/^o\d+_\d+$/;
function doPost(e){const d=JSON.parse(e.postData.contents);if(d.key!==KEY)return o_({err:'key'});
  if(d.orig){if(!IRE.test(d.orig))return o_({err:'id'});const m=String(d.data).match(/^data:(.+?);base64,(.*)$/);if(!m)return o_({err:'data'});const n='orig-'+d.orig,old=pf_(n);if(old)old.setTrashed(true);DriveApp.getFolderById(FOLDER).createFile(Utilities.newBlob(Utilities.base64Decode(m[2]),m[1],n));return o_({ok:1})}
  if(d.del){if(IRE.test(d.del)){const f=pf_('orig-'+d.del);if(f)f.setTrashed(true)}return o_({ok:1})}
  if(d.date){if(!DRE.test(d.date))return o_({err:'date'});save_('photo-'+d.date+'.json',JSON.stringify(d.photos||[]));return o_({ok:1})}
  delete d.key;save_(NAME,JSON.stringify(d));return o_({ok:1})}
function doGet(e){const p=e.parameter;if(p.key!==KEY)return o_({err:'key'});
  if(p.orig){if(!IRE.test(p.orig))return o_({err:'id'});const f=pf_('orig-'+p.orig);if(!f)return o_({});const b=f.getBlob();return o_({data:'data:'+b.getContentType()+';base64,'+Utilities.base64Encode(b.getBytes())})}
  if(p.list){const out=[],it=DriveApp.getFolderById(FOLDER).getFiles();while(it.hasNext()){const m=it.next().getName().match(/^photo-(\d{4}-\d\d-\d\d)\.json$/);if(m)out.push(m[1])}return o_({dates:out})}
  if(p.date){if(!DRE.test(p.date))return o_({err:'date'});const f=pf_('photo-'+p.date+'.json');return o_({photos:f?JSON.parse(f.getBlob().getDataAsString()):[]})}
  const f=pf_(NAME);return ContentService.createTextOutput(f?f.getBlob().getDataAsString():'{}').setMimeType(ContentService.MimeType.JSON)}
