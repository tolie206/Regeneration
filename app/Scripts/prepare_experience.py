"""Pinned, narrow hooks. Never patch global SetVolume or third-person/cutscene cameras."""
from pathlib import Path
import re

def patch(text,engine,granular,volume,zoom):
 changed=False
 for number in [engine,granular,zoom]:
  m=re.search(r'\n(?:static )?\w+ w2c_game_f'+str(number)+r'\([^;]+\) \{',text)
  if not m:continue
  a=m.start();b=text.index('\n}\n',a);body=text[a:b]
  if number==zoom:
   if 'pg_first_person_fov(' in body:continue
   pattern=r'(f32_store(?:_shared|_plain)\([^\n]*checked_add_u64\(var_j0, 160u\), )var_f1(\);)'
   body,count=re.subn(pattern,r'\1pg_first_person_fov(var_f1)\2',body)
   if count!=3:raise RuntimeError('Pinned first-person FOV stores changed: '+str(count))
  else:
   if 'pg_vehicle_engine_db(' in body:continue
   pattern=rf'(w2c_game_f{volume}\(instance, var_j0, )var_f1(\);)'
   body,count=re.subn(pattern,r'\1pg_vehicle_engine_db(var_f1)\2',body)
   expected=6 if number==engine else 4
   if count!=expected:raise RuntimeError('Pinned engine volume sites changed: '+str((number,count)))
  text=text[:a]+body+text[b:];changed=True
 if changed:
  at=text.index('\n',text.index('#include'))+1
  text=text[:at]+'extern float pg_vehicle_engine_db(float);\nextern float pg_first_person_fov(float);\n'+text[at:]
 return text

def main():
 from engine_names import fn
 ids=[fn(x) for x in ['audVehicleEngineComponent::Update(audVehicleVariables*)','audGranularEngineComponent::Update(audVehicleVariables*, bool)','rage::audRequestedSettings::SetVolume(float)','camFirstPersonShooterCamera::UpdateZoom()']]
 root=Path(__file__).resolve().parents[1];found=set()
 for p in sorted((root/'Generated').glob('game_*.c')):
  text=p.read_text();result=patch(text,*ids)
  for n in [ids[0],ids[1],ids[3]]:
   if re.search(r'\n(?:static )?\w+ w2c_game_f'+str(n)+r'\([^;]+\) \{',text):found.add(n)
  if result!=text:p.write_text(result)
 if found!={ids[0],ids[1],ids[3]}:raise RuntimeError('Missing pinned experience functions')
 print('Engine-only gain and native first-person FOV hooks verified')
if __name__=='__main__':main()
