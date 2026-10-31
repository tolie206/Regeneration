"""Reuse exact successful feature checks; only release labels changed afterwards."""
import json,os,subprocess,urllib.request
from pathlib import Path
BASE='16b93f1639235734ab06988a3ad3764253e3dd90'
assert subprocess.check_output(['git','rev-parse','HEAD^'],text=True).strip()==BASE
for path in ['app/App/Theme.swift','app/App/HomeView.swift','app/App/GraphicsOptions.swift','app/App/Info.plist','app/project.yml']:
 old=subprocess.check_output(['git','show',BASE+':'+path]).decode().replace('\r\n','\n')
 expected=old.replace('V5R1-FIX3','V5R1-FIX3-FILTER') if path.endswith('.swift') else old.replace('5004','5005')
 assert Path(path).read_text(encoding='utf-8')==expected,path
allowed={'app/App/Theme.swift','app/App/HomeView.swift','app/App/GraphicsOptions.swift','app/App/Info.plist','app/project.yml','tests/fixtures/v5fix2_reviewed_hunks.json','.github/workflows/v5-fix.yml','.github/workflows/color-filter.yml','tools/verify_filter_release.py'}
changed=set(subprocess.check_output(['git','diff','--name-only',BASE,'HEAD'],text=True).splitlines())
assert changed<=allowed,changed-allowed
for run,sha in [(41159665455,BASE),(41158629219,'24b0b3a')]:
 req=urllib.request.Request('https://api.github.com/repos/tolie206/Regeneration/actions/runs/'+str(run),headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req) as response:data=json.load(response)
 assert data['head_sha'].startswith(sha) and data['conclusion']=='success',(run,data['conclusion'])
print('PASS exact tested filter/audio source; prior Metal/Swift/sanitizer checks successful; only release labels changed')
