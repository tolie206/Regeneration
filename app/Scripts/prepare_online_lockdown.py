from pathlib import Path
from engine_names import fn
import re
root=Path(__file__).resolve().parents[1]
for name in ['CCheat::DoCheats()','CCheat::HasCheatActivated(unsigned int, unsigned int)','CCheat::HasPcCheatActivated(unsigned int)']:
 index=fn(name);pattern=rf'^(void|u32|u64) w2c_game_f{index}\([^\n]*\) \{{'
 found=[]
 for p in (root/'Generated').glob('game_*.c'):
  s=p.read_text();m=re.search(pattern,s,re.M)
  if not m:continue
  start=m.end();end=s.index('\n}\n',start)
  value='return;' if m.group(1)=='void' else 'return 0;'
  s=s[:start]+'\n  // Online-only: built-in cheat execution is disabled.\n  '+value+'\n'+s[end:];p.write_text(s);found.append(p.name)
 if len(found)!=1:raise RuntimeError(f'{name}: expected one pinned body, found {found}')
 print('Online lockdown',name,index)
