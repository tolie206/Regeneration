"""Independent full readback of published candidate manifest and all converted RPF/resources."""
from pathlib import Path
import json,sys,collections,hashlib,struct,time
from resource_codec import resource
from rpf_reader import Rpf

def main():
 data=Path(sys.argv[1]).resolve();report=json.loads((data.parent/(data.name+'-report.json')).read_text());manifest=json.loads((data/'manifest.json').read_text());marker=json.loads((data/'mugoat-port-data.json').read_text())
 if hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest()!=marker['manifestSHA256']:raise ValueError('manifest hash')
 records={x['path']:x for x in report['records']};stats=collections.Counter();start=time.time()
 def check_resource(b,system=None,graphics=None):
  raw,v,codec,version=resource(b,system,graphics)
  if codec!='deflate':raise ValueError('non-deflate candidate resource')
  for code in (b'EDX1',b'EDX3',b'EDX5',b'EAT1',b'EAT2'):
   if code in raw[:v]:raise ValueError('custom format remains')
  stats['resources_readback']+=1
 def walk(r,depth=0):
  if depth>16:raise ValueError('deep archive')
  if struct.unpack_from('<I',r.data,r.base+12)[0]!=0x4e45504f:raise ValueError('engine-incompatible RPF key; expected OPEN')
  for e in r.entries:
   if e.encrypted:raise ValueError('encrypted converted entry')
   if e.resource:check_resource(r.raw(e),e.system,e.graphics)
   elif e.path.endswith('.rpf'):walk(r.nested(e),depth+1)
   elif e.compressed:r.binary(e)
  stats['archives_readback']+=1
 for i,row in enumerate(manifest['files']):
  name,size=row[:2];p=(data/name).resolve()
  if not p.is_relative_to(data) or p.stat().st_size!=size:raise ValueError('path/size '+name)
  h=hashlib.sha256()
  with p.open('rb') as f:
   while b:=f.read(1<<20):h.update(b)
  if h.hexdigest()!=records[name]['sha256']:raise ValueError('file hash '+name)
  if records[name]['source']!='mugoat':
   if p.suffix=='.rpf':
    r=Rpf(p)
    try:walk(r)
    finally:r.close()
   else:
    with p.open('rb') as f:head=f.read(4)
    if head==b'RSC7':check_resource(p.read_bytes())
   stats['port_files_readback']+=1;stats['port_bytes']+=size
  else:stats['mugoat_retained_files']+=1
  if i%500==0:print(json.dumps(dict(done=i+1,total=len(manifest['files']),stats=stats,seconds=round(time.time()-start))),flush=True)
 stats['files_readback']=len(manifest['files']);stats['bytes_readback']=sum(x[1] for x in manifest['files'])
 result=dict(status='OFFLINE_READBACK_PASS_NOT_DEVICE_TESTED',stats=stats,seconds=round(time.time()-start))
 (data.parent/'VERIFICATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
