"""Pinned engine gain and final-output-frame FOV. No writes to camera zoom state."""
from pathlib import Path
import re

def patch(text,granular,channel,frame,shooter,mounted,generate):
 changed=False
 for number in [granular,frame,shooter,mounted,generate]:
  m=re.search(r'\n(?:static )?\w+ w2c_game_f'+str(number)+r'\([^;]+\) \{',text)
  if not m:continue
  a=m.start();b=text.index('\n}\n',a);body=text[a:b]
  if 'pg_vehicle_grain_gain(' in body or 'pg_camera_' in body or 'pg_granular_output_probe(' in body:continue
  if number==granular:
   pattern=rf'(w2c_game_f{channel}\(instance, var_j0, var_i1, )var_f2(, var_f3\);)'
   body,count=re.subn(pattern,r'\1pg_vehicle_grain_gain(var_f2)\2',body)
   if count!=6:raise RuntimeError('Pinned granular channel sites changed: '+str(count))
  elif number==frame:
   if 'var_j2 = 272ull;' not in body or 'var_j1 = 48ull;' not in body:raise RuntimeError('Pinned camera frame layout changed')
   if body.count('FUNC_EPILOGUE;')!=1:raise RuntimeError('Camera return changed')
   body=body.replace('FUNC_PROLOGUE;','FUNC_PROLOGUE;\n  u64 pg_camera_parent = pg_camera_frame_begin();',1)
   body=body.replace('FUNC_EPILOGUE;','pg_camera_frame_end(instance,var_p0,var_p1,pg_camera_parent,var_i0);\n  FUNC_EPILOGUE;')
  elif number in [shooter,mounted]:
   if body.count('FUNC_EPILOGUE;')!=1:raise RuntimeError('First-person camera return changed')
   call='pg_camera_mark_shooter(var_p0);' if number==shooter else 'pg_camera_mark_vehicle(instance,var_p0);'
   body=body.replace('FUNC_EPILOGUE;',call+'\n  FUNC_EPILOGUE;')
  else:
   if body.count('FUNC_EPILOGUE;')!=1:raise RuntimeError('Granular output return changed')
   body=body.replace('FUNC_EPILOGUE;','pg_granular_output_probe(instance,var_p1);\n  FUNC_EPILOGUE;')
  text=text[:a]+body+text[b:];changed=True
 if changed:
  at=text.index('\n',text.index('#include'))+1
  declarations='extern float pg_vehicle_grain_gain(float);\nextern u64 pg_camera_frame_begin(void);\nextern void pg_camera_frame_end(w2c_game*,u64,u64,u64,u32);\nextern void pg_camera_mark_shooter(u64);\nextern void pg_camera_mark_vehicle(w2c_game*,u64);\nextern void pg_granular_output_probe(w2c_game*,u64);\n'
  text=text[:at]+declarations+text[at:]
 return text

def main():
 from engine_names import fn
 ids=[fn(x) for x in ['audGranularEngineComponent::Update(audVehicleVariables*, bool)','rage::audGranularSound::SetChannelVolume(unsigned int, float, float)','camBaseCamera::BaseUpdate(camFrame&)','camFirstPersonShooterCamera::Update()','camCinematicMountedCamera::Update()','rage::audGranularMix::GenerateFrame(float*, unsigned int, float, float)']]
 root=Path(__file__).resolve().parents[1];found=set();expected={ids[i] for i in [0,2,3,4,5]}
 checks={fn('camFrame::CloneFrom(camFrame const&)'):'112u',fn('CViewport::PropagateCameraFrame(camFrame const&)'):'112u'}
 getter=fn('camGameplayDirector::GetFirstPersonVehicleCamera(CEntity const*)')
 for file in sorted((root/'Generated').glob('game_*.c')):
  source=file.read_text()
  for number in list(checks):
   m=re.search(r'\n(?:static )?\w+ w2c_game_f'+str(number)+r'\([^;]+\) \{',source)
   if m:
    body=source[m.start():source.index('\n}\n',m.start())]
    if checks[number] not in body:raise RuntimeError('Camera frame FOV offset changed')
    del checks[number]
  if getter is not None and re.search(r'\n(?:static )?u64 w2c_game_f'+str(getter)+r'\(w2c_game\* instance\) \{',source):getter=None
 if checks or getter is not None:raise RuntimeError('Camera frame/getter ABI not verified')

 for p in sorted((root/'Generated').glob('game_*.c')):
  text=p.read_text();result=patch(text,*ids)
  for n in expected:
   if re.search(r'\n(?:static )?\w+ w2c_game_f'+str(n)+r'\([^;]+\) \{',text):found.add(n)
  if result!=text:p.write_text(result)
 if found!=expected:raise RuntimeError('Missing pinned camera/audio functions: '+str(expected-found))
 print('Granular channel gain and final-output first-person FOV verified')
if __name__=='__main__':main()
