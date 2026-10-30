"""Aggregate local tester logs only; never copies raw logs or assets into repository."""
from pathlib import Path
import argparse,csv,json,re,collections
p=argparse.ArgumentParser();p.add_argument('logs',type=Path);p.add_argument('--index',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('docs/performance'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
index=json.loads(a.index.read_text(encoding='utf8'));sets={};counts={};rows=[];summary=[]
pattern=re.compile(r'fps: ([\d.]+) \((\d+) frames, (\d+) draws/frame, ([\d.]+) command buffers/frame\).*renderer busy ([\d.]+) ms/frame')
for path in sorted(a.logs.glob('*.log')):
 lines=path.read_text(encoding='utf8',errors='replace').splitlines();device=next((s for s in lines if s.startswith('Device:')),'unknown');counts[path.name]=collections.Counter()
 for n,s in enumerate(lines,1):
  m=re.search(r'no precompiled shader ([0-9a-f]+) \(stage (\d+)\)',s)
  if m:counts[path.name][m.groups()]+=1
  m=pattern.search(s)
  if m:
   following=lines[n] if n<len(lines) else ''
   cb=re.search(r'present ([\d.]+), readback ([\d.]+), idle queries ([\d.]+)',following)
   rows.append([path.name,n,*m.groups(),*(cb.groups() if cb else ('','','')),'UNCLASSIFIED: may include loading/menu/pause; not a gameplay benchmark'])
 sets[path.name]=set(counts[path.name]);summary.append({'file':path.name,'lines':len(lines),'device':device,'missing_unique':len(sets[path.name]),'missing_occurrences':sum(counts[path.name].values()),'renderer_windows':sum(r[0]==path.name for r in rows),'gpu_buffer_warnings':sum('GPU version of buffer not updated!' in s for s in lines)})
with (a.out/'renderer_windows.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['file','line','fps','frames','draws_per_frame','cb_per_frame','cpu_renderer_busy_ms','present_cb','readback_cb','idle_cb','context']);w.writerows(rows)
with (a.out/'missing_shaders.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['hash','stage',*sets.keys(),'in_available_index','pass_mapping'])
 for key in sorted(set().union(*sets.values())):w.writerow([*key,*[counts[k][key] for k in sets],key[0] in index,index.get(key[0],{}).get('effect','UNKNOWN: original shader absent')])
(a.out/'log_summary.json').write_text(json.dumps({'logs':summary,'identical_missing_sets':all(v==next(iter(sets.values())) for v in sets.values()),'index_entries':len(index),'notice':'Aggregated observations, not matched device benchmark; no raw logs included.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False));print('Missing tuples identical:',all(v==next(iter(sets.values())) for v in sets.values()))
