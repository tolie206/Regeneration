"""Strictly convert provided Menyoo scenery; never execute XML scripts/clear-world commands."""
from pathlib import Path
import xml.etree.ElementTree as ET,math,json,hashlib,sys
R=Path(__file__).resolve().parents[1]
def convert():
 rows=[];counts={};hashes={}
 for p in sorted((R/'muzom-inputs/dead-among-us').glob('*.xml')):
  b=p.read_bytes()
  if b'<!DOCTYPE' in b.upper() or b'<!ENTITY' in b.upper():raise ValueError('XML entities forbidden')
  root=ET.fromstring(b);assert root.tag=='SpoonerPlacements'
  counts[p.name]={str(i):0 for i in (1,2,3)};hashes[p.name]=hashlib.sha256(b).hexdigest()
  for v in root.findall('Placement'):
   kind=int(v.findtext('Type'));counts[p.name][str(kind)]+=1
   model=int(v.findtext('ModelHash'),0);assert 0<model<=0xffffffff
   coords=[float(v.findtext('PositionRotation/'+k)) for k in ['X','Y','Z','Pitch','Roll','Yaw']]
   assert all(math.isfinite(x) for x in coords) and all(abs(x)<15000 for x in coords[:3])
   name=v.findtext('HashName','').lower();attachment=v.find('Attachment')
   if v.findtext('IsVisible','true').lower()!='true' or (attachment is not None and attachment.get('isAttached')=='true'):continue
   if kind==3 and not name.startswith(('prop_rub_','prop_barrier_','prop_dumpster_','prop_bin_','prop_crate_','prop_skip_')):continue
   if kind not in (2,3):continue
   if v.findtext('IsOnFire','false').lower()=='true':continue
   rows.append((model,kind,*coords))
 out=['// Derived from The Dead Among Us, denedwin; see MuZomCredits.txt.','typedef struct {uint32_t model;uint8_t kind;float x,y,z,pitch,roll,yaw;} MZPlacement;','static const MZPlacement mzPlacements[]={']
 for row in rows:
  floats=','.join(format(x,'.8g')+('f' if '.' in format(x,'.8g') or 'e' in format(x,'.8g') else '.0f') for x in row[2:])
  out.append('{0x%08xu,%d,%s},'%(row[0],row[1],floats))
 out+=['};','#define MZ_PLACEMENTS_COUNT (sizeof mzPlacements/sizeof mzPlacements[0])']
 return '\n'.join(out)+'\n',{'source_counts':counts,'raw_placements':sum(sum(v.values()) for v in counts.values()),'selected':len(rows),'sha256':hashes}
if __name__=='__main__':
 text,report=convert();path=R/'app/Source/MuZomMapData.h'
 if '--check' in sys.argv:assert path.read_text()==text
 else:path.write_text(text);(R/'muzom-inputs/map-audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
