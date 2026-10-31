"""Repair V1 NONE headers to supported OPEN. Payload/size/manifest remain unchanged."""
from pathlib import Path
import json,struct,sys
from rpf_reader import Rpf
from convert_data import sha

def main():
 data=Path(sys.argv[1]).resolve();marker=json.loads((data/'mugoat-port-data.json').read_text())
 if marker.get('profile')!='mugoat-port-converted-v1':raise ValueError('not a converted dataset')
 journal_path=data.parent/'RPF-FIX1-JOURNAL.json'
 if journal_path.exists():raise ValueError('repair journal exists; do not overwrite rollback record')
 report_path=data.parent/(data.name+'-report.json');report=json.loads(report_path.read_text());records={x['path']:x for x in report['records']}
 manifest=json.loads((data/'manifest.json').read_text());plans=[]
 def walk(r):
  offsets=[]
  if struct.unpack_from('<I',r.data,r.base+12)[0]==0:offsets.append(r.base+12)
  for e in r.entries:
   if e.path.endswith('.rpf') and not e.resource:
    if e.encrypted or e.compressed:raise ValueError('unsupported nested archive')
    child_key=struct.unpack_from('<I',r.data,r.base+e.offset+12)[0]
    if child_key in (0,0x4e45504f):offsets.extend(walk(r.nested(e)))
  return offsets
 for name,size,*_ in manifest['files']:
  if not name.lower().endswith('.rpf'):continue
  p=(data/name).resolve()
  if not p.is_relative_to(data) or p.stat().st_size!=size:raise ValueError('path/size mismatch')
  with p.open('rb') as f:h=f.read(16)
  if len(h)!=16 or struct.unpack_from('<I',h)[0]!=0x52504637:raise ValueError('not RPF7')
  if struct.unpack_from('<I',h,12)[0] not in (0,0x4e45504f):continue
  r=Rpf(p)
  try:offsets=walk(r)
  finally:r.close()
  if offsets:
   before=sha(p)
   if before!=records[name]['sha256']:raise ValueError('pre-repair checksum differs '+name)
   plans.append(dict(path=name,offsets=offsets,beforeSHA256=before))
 journal_path.write_text(json.dumps(dict(profile='rpf-open-repair-v1',original=0,replacement=0x4e45504f,changes=plans),indent=2),encoding='utf8')
 count=0
 for item in plans:
  p=data/item['path']
  with p.open('r+b') as f:
   for offset in item['offsets']:
    f.seek(offset)
    if f.read(4)!=bytes(4):raise ValueError('header changed during repair')
    f.seek(offset);f.write(b'OPEN');count+=1
  records[item['path']]['sha256']=sha(p)
 report['rpf_open_fix']=dict(archives=count,files=len(plans));report['status']='RPF_OPEN_FIXED_NEEDS_READBACK'
 report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 verification=data.parent/'VERIFICATION.json'
 if verification.exists():verification.rename(data.parent/'VERIFICATION_V1_BEFORE_FIX1.json')
 summary=data.parent/'SUMMARY.json';s=json.loads(summary.read_text());s['rpf_open_fix']=report['rpf_open_fix'];s['status']=report['status'];summary.write_text(json.dumps(s,indent=2),encoding='utf8')
 print(json.dumps(report['rpf_open_fix']),flush=True)
if __name__=='__main__':main()
