"""Build a separate performance dataset. Originals are read-only; unchanged files may be hardlinked."""
from pathlib import Path
import sys,json,struct,hashlib,os,shutil,collections,time
from rpf_reader import Rpf
from convert_data import align,sha
from optimize_ytd import optimize
STATS=collections.Counter();CAP=256

def allowed(name):
 if name.lower().startswith('x64/textures/') and not name.lower().startswith('x64/textures/plantsmgr'):return False
 return not any(x in name.lower() for x in ('font','radar','minimap','hud','frontend','scaleform','script','hacking','minigame','reticle'))

def rebuild(r,target,prefix):
 n,names=struct.unpack_from('<II',r.data,r.base+4);end=16+n*16+names;table=bytearray(r.data[r.base:r.base+end]);struct.pack_into('<I',table,12,0x4e45504f)
 changes=0
 with target.open('wb') as f:
  f.write(table);align(f)
  for e in r.entries:
   align(f);offset=f.tell();child=None;system=e.system;graphics=e.graphics
   try:
    b=r.raw(e)
    if e.resource and e.path.endswith('.ytd') and allowed(prefix+'/'+e.path):
     optimized,info=optimize(b,e.system,e.graphics,CAP)
     if 'changed' in info:
      b=optimized;system,graphics=struct.unpack_from('<II',b,8);changes+=1
      STATS['dictionaries']+=1;STATS['textures_reduced']+=info['changed'];STATS['physical_before']+=info['physical_before'];STATS['physical_after']+=info['physical_after'];STATS['pixel_before']+=info['pixel_before'];STATS['pixel_after']+=info['pixel_after']
     else:STATS[info['reason']]+=1
    elif not e.resource and e.path.endswith('.rpf'):
     child=target.with_name(target.name+'.child');changes+=rebuild(r.nested(e),child,prefix+'/'+e.path);b=None
    size=child.stat().st_size if child else len(b)
    if e.resource and size>=0xffffff:raise ValueError('large resource preserved at dataset level')
    stored=size if e.resource or e.compressed else 0
    value=(struct.unpack_from('<I',table,16+e.index*16)[0]&65535)|(stored<<16)|((offset//512)<<40)|(int(e.resource)<<63)
    struct.pack_into('<Q',table,16+e.index*16,value)
    if e.resource:struct.pack_into('<II',table,16+e.index*16+8,system,graphics)
    elif child:struct.pack_into('<I',table,16+e.index*16+8,size)
    if child:
     with child.open('rb') as inp:shutil.copyfileobj(inp,f,1<<20)
    else:f.write(b)
   finally:
    if child:child.unlink(missing_ok=True)
  align(f);f.seek(0);f.write(table)
 check=Rpf(target);assert len(check.entries)==len(r.entries);check.close()
 return changes

def main():
 source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
 if out==source or source in out.parents or out in source.parents:raise ValueError('source/output overlap')
 if out.exists() and any(out.iterdir()):raise ValueError('output must be empty')
 manifest=json.loads((source/'manifest.json').read_text());oldreport=json.loads((source.parent/(source.name+'-report.json')).read_text());records={x['path']:x for x in oldreport['records']};newrecords=[];rows=[];changed_files=[];out.mkdir(parents=True,exist_ok=True);start=time.time()
 for i,row in enumerate(manifest['files']):
  name=row[0];p=source/name;dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.optimizing');changed=0;reason=''
  if name.lower().endswith('.rpf') and allowed(name) and name.startswith(('x64/levels/','x64/models/')):
   with p.open('rb') as f:h=f.read(16)
   if len(h)==16 and struct.unpack_from('<I',h,12)[0]==0x4e45504f:
    before=STATS.copy()
    try:
     r=Rpf(p)
     try:changed=rebuild(r,tmp,name)
     finally:r.close()
    except Exception as ex:
     STATS.clear();STATS.update(before);reason='kept original: '+str(ex);tmp.unlink(missing_ok=True);changed=0
  elif name.endswith('.ytd') and allowed(name):
   try:
    b,info=optimize(p.read_bytes(),cap=CAP)
    if 'changed' in info:
     tmp.write_bytes(b);changed=1;STATS['dictionaries']+=1;STATS['textures_reduced']+=info['changed']
     for key in ('physical_before','physical_after','pixel_before','pixel_after'):STATS[key]+=info[key]
   except Exception as ex:reason='kept original: '+str(ex)
  record=dict(records[name]);record['optimization']=reason or ('mip cap '+str(CAP) if changed else 'unchanged')
  if changed:
   os.replace(tmp,dest);record['size']=dest.stat().st_size;record['sha256']=sha(dest);changed_files.append(name)
  else:
   tmp.unlink(missing_ok=True)
   try:os.link(p,dest)
   except OSError:shutil.copyfile(p,dest)
  newrecords.append(record);rows.append([name,dest.stat().st_size,int(dest.stat().st_mtime)])
  if changed or i%500==0:print(json.dumps(dict(done=i+1,total=len(manifest['files']),path=name,changed=changed,reason=reason,seconds=round(time.time()-start),stats=STATS)),flush=True)
 manifest['files']=rows;manifest['version']='port-performance-v2';raw=json.dumps(manifest,separators=(',',':')).encode();(out/'manifest.json').write_bytes(raw)
 marker=json.loads((source/'mugoat-port-data.json').read_text());marker['manifestSHA256']=hashlib.sha256(raw).hexdigest();marker['optimization']='YTD existing mip cap256, compact physical pages';(out/'mugoat-port-data.json').write_text(json.dumps(marker,indent=2))
 report=dict(status='OPTIMIZED_CANDIDATE_NEEDS_READBACK',hybrid=True,complete=True,records=newrecords,stats=STATS,changed_files=changed_files,installed_payload_bytes=sum(x[1] for x in rows))
 (out.parent/(out.name+'-report.json')).write_text(json.dumps(report,indent=2),encoding='utf8');(out.parent/'OPTIMIZATION.json').write_text(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2),encoding='utf8');print(json.dumps(dict(done=True,bytes=report['installed_payload_bytes'],stats=STATS)),flush=True)
if __name__=='__main__':main()
