from pathlib import Path
import re

def patch(text,number):
 head=f'u64 w2c_game_f{number}(w2c_game* instance, u64 var_p0, u64 var_p1, u64 var_p2) {{'
 if head not in text:return None
 a=text.index(head);b=text.index('\n}\n',a);body=text[a:b]
 if 'pg_hide_bike_body(' in body:return text
 # Only render submission, no entity simulation/state writes. Native no-draw returns0.
 if 'return var_j0;' not in body:raise RuntimeError('Ped draw return changed')
 text=text[:a]+body.replace(head,head+'\n  if(pg_hide_bike_body(instance,var_p1))return 0;',1)+text[b:]
 at=text.index('\n',text.index('#include'))+1
 return text[:at]+'extern _Bool pg_hide_bike_body(w2c_game*,u64);\n'+text[at:]
def main():
 from engine_names import fn
 number=fn('CPedDrawHandler::AddToDrawList(rage::fwEntity*, rage::fwDrawDataAddParams*)')
 root=Path(__file__).resolve().parents[1]
 for p in sorted((root/'Generated').glob('game_*.c')):
  result=patch(p.read_text(),number)
  if result is not None:p.write_text(result);print('Local bike-body render guard verified');return
 raise RuntimeError('Ped draw handler missing')
if __name__=='__main__':main()
