"""Drop optional test map, finalize engine-bound marker, verify every generated file."""
from pathlib import Path
import argparse,json,hashlib
from convert_data import sha
from resource_codec import resource
from rpf_reader import Rpf

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--base-manifest',required=True);a=ap.parse_args()
 data=Path(a.data).resolve();base=Path(a.base_manifest).resolve();report_path=data.parent/(data.name+'-report.json')
 report=json.loads(report_path.read_text());manifest=json.loads((data/'manifest.json').read_text());original=json.loads(base.read_text())
 if not report.get('complete') or len(manifest['files'])!=len(original['files']):raise ValueError('conversion not complete')
 if [x[0] for x in manifest['files']] != [x[0] for x in original['files']]:raise ValueError('unexpected file list')
 def optional(n):return 'levels/env_test/' in n or n.startswith('common/data/env_test_')
 removed=[];kept=[];lookup={r['path']:r for r in report['records']}
 for row in manifest['files']:
  name,size=row[:2];p=(data/name).resolve()
  if not p.is_relative_to(data):raise ValueError('unsafe generated path')
  if optional(name):
   if p.is_file():p.unlink()
   removed.append(dict(path=name,bytes=size));continue
  if p.stat().st_size!=size or sha(p)!=lookup[name]['sha256']:raise ValueError('candidate checksum mismatch '+name)
  kept.append(row)
 manifest['files']=kept;raw=json.dumps(manifest,separators=(',',':')).encode();(data/'manifest.json').write_bytes(raw)
 marker=dict(profile='mugoat-port-converted-v1',baseManifestSHA256=hashlib.sha256(base.read_bytes()).hexdigest(),manifestSHA256=hashlib.sha256(raw).hexdigest(),hybrid=True,deviceTested=False,optionalTestMapRemoved=True)
 (data/'mugoat-port-data.json').write_text(json.dumps(marker,indent=2),encoding='utf8')
 report['removed_optional_map']=removed;report['installed_payload_bytes']=sum(x[1] for x in kept);report['files_after_optional_removal']=len(kept)
 report['port_payload_bytes']=sum(x[1] for x in kept if lookup[x[0]]['source']!='mugoat');report['fallback_payload_bytes']=sum(x[1] for x in kept if lookup[x[0]]['source']=='mugoat')
 report['status']='HASH_VERIFIED_CANDIDATE_NOT_DEVICE_TESTED'
 report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 summary={k:v for k,v in report.items() if k not in ('records','removed_optional_map')};summary['optional_removed_bytes']=sum(x['bytes'] for x in removed);summary['fallback_reasons']={}
 for x in report['records']:
  if not optional(x['path']) and x['source']=='mugoat':summary['fallback_reasons'][x['reason']]=summary['fallback_reasons'].get(x['reason'],0)+1
 (data.parent/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
