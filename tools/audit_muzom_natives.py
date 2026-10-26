from pathlib import Path
import sys,json,re,hashlib
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'app/Scripts'))
from engine_names import read_names
p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()=='11ca8d2c04c5e843d18ff4aea4899d72c86973c6b031df334e67c446b2ae83e0'
names=read_names(p);manifest=json.loads((r/'muzom-inputs/native-manifest.json').read_text());report={}
for name,h in manifest.items():
 found=[i for i,v in names.items() if 'scrWrapped_'+name+'::Call(rage::scrThread::Info&)' in v]
 if not found:
  camel=''.join(part.capitalize() for part in name.lstrip('_').split('_')).lower()
  found=[i for i,v in names.items() if (v.split('(')[0].split('::')[-1].lower()=='command'+camel) or (v.startswith('rage::scrThread::') and v.split('(')[0].split('::')[-1].lower()==camel)]
 assert len(found)==1,(name,found);assert re.search(r'^'+h+r' .*\b'+name+r'\b',(r/'app/Scripts/asi_native_hashes.txt').read_text(),re.M)
 report[name]=found[0]
print('PASS pinned wasm supports all',len(report),'MuZom natives:',json.dumps(report,sort_keys=True))
