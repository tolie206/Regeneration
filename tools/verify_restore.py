"""Restored engine is byte-identical to0383f09; whitelist only optimizer/packaging changes."""
from pathlib import Path
import subprocess,hashlib,zipfile,argparse,json
ROOT=Path(__file__).resolve().parents[1]
BASE='0383f09b08004319c2fd87db96d454eb9696fe45'
SHA='bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c'
def blob(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
def check():
 allowed={'.github/workflows/v5-fix.yml','app/App/BundledOptimizer.swift','app/App/NativePortViewController.swift','app/App/Theme.swift','app/App/HomeView.swift','app/App/Info.plist','app/project.yml','app/Resources/Mugoat-PortLike-Traffic-v1.oiv','app/Tests/BundledOptimizerTests.swift','tools/verify_restore.py','tests/test_restore_optimizer.py','tests/fixtures/restore_ui_hunks.json','docs/performance/RESTORE_0383_OPTIMIZER.md'}
 changed=set(subprocess.check_output(['git','diff','--name-only',BASE,'HEAD'],cwd=ROOT,text=True).splitlines());assert changed<=allowed,changed-allowed
 assert not any(p.startswith(('app/Source/','app/Scripts/')) for p in changed),'Engine/renderer/wasm patchers must exactly match baseline'
 hunks=json.loads(blob('HEAD','tests/fixtures/restore_ui_hunks.json'))
 for name in ['app/App/Theme.swift','app/App/HomeView.swift','app/App/Info.plist','app/project.yml','app/App/NativePortViewController.swift']:
  old=blob(BASE,name).decode().replace('\r\n','\n');new=blob('HEAD',name).decode().replace('\r\n','\n')
  for before,after in hunks.get(name,[]):
   assert new.count(after)==1,(name,after);new=new.replace(after,before)
  if name.endswith(('Theme.swift','HomeView.swift')):expected=old.replace('V5R1-FIX2','V5R1-FIX2-OPTIMIZER')
  elif name.endswith(('Info.plist','project.yml')):expected=old.replace('5003','5009')
  else:expected=old
  assert new==expected,name
 assert hashlib.sha256(blob('HEAD','app/Resources/Mugoat-PortLike-Traffic-v1.oiv')).hexdigest()==SHA
 print('PASS exact0383f09 engine/renderer/scripts/graphics settings; only optimizer startup, reviewed home Mods shortcut and release labels changed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa');a=p.parse_args();check()
 if a.ipa:
  with zipfile.ZipFile(a.ipa) as z:
   files=[n for n in z.namelist() if n.startswith('Payload/') and n.endswith('/Mugoat-PortLike-Traffic-v1.oiv')]
   assert len(files)==1 and hashlib.sha256(z.read(files[0])).hexdigest()==SHA
  print('PASS final IPA embeds exact requested OIV')
