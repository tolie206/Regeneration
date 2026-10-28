"""Link the real iOS Rust library with the production library-search configuration before compiling the engine."""
from pathlib import Path
import subprocess,shutil,re,json
root=Path(__file__).resolve().parents[1];app=root/'app';out=app/'Build/OnlineLinkCheck';out.mkdir(parents=True,exist_ok=True)
archive=app/'Build/Online/libmugoat_online.a'
if not archive.is_file():raise SystemExit('Missing actual iOS Rust archive before link preflight')
lib=out/'Build/Online/libmugoat_online.a';lib.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(archive,lib)
project=(app/'project.yml').read_text(encoding='utf-8')
m=re.search(r'^    LIBRARY_SEARCH_PATHS:\n((?:      -[^\n]*\n)+)',project,re.M)
if not m:raise SystemExit('Cannot extract production library-search paths')
(out/'host.c').write_text('''#include "MugoatOnline.h"
int mugoat_command_info(const char*n,uint32_t*p,uint32_t c,uint32_t*r){return -1;}
bool mugoat_command_call(void*i,const char*n,const MugoatValue*a,uint32_t c,MugoatValue*r){return false;}
uint8_t*mugoat_memory_data(void*i,uint64_t*s){*s=0;return NULL;}
int main(void){char status[512];MugoatOnlineConfigure("127.0.0.1:47520","Audit","roleplay",2);mugoat_script_tick(NULL,0,0);mugoat_explosion(0);mugoat_time_warp(0);MugoatOnlineStatus(status,512);return MugoatOnlineConnected()?0:1;}
''')
spec='''name: OnlineLinkCheck
options:
  deploymentTarget:
    iOS: "16.0"
settings:
  base:
    HEADER_SEARCH_PATHS: __HEADER__
    GENERATE_INFOPLIST_FILE: YES
    LIBRARY_SEARCH_PATHS:
__LIBRARY_PATHS__targets:
  OnlineLinkCheck:
    type: application
    platform: iOS
    sources: [host.c]
    dependencies:
      - framework: Build/Online/libmugoat_online.a
        embed: false
      - sdk: UIKit.framework
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: vn.gta.online.link.audit
'''.replace('__HEADER__',json.dumps(str(app/'Source'))).replace('__LIBRARY_PATHS__',m.group(1))
(out/'project.yml').write_text(spec)
subprocess.run(['xcodegen','generate','--spec','project.yml'],cwd=out,check=True)
p=subprocess.run(['xcodebuild','-project','OnlineLinkCheck.xcodeproj','-scheme','OnlineLinkCheck','-configuration','Release','-sdk','iphoneos','-destination','generic/platform=iOS','-derivedDataPath',str(out/'Derived'),'CODE_SIGNING_ALLOWED=NO','build'],cwd=out,text=True,capture_output=True)
log=p.stdout+p.stderr;(out/'link.log').write_text(log)
if p.returncode:
 print('\n'.join(log.splitlines()[-140:]));raise SystemExit('Online iOS link preflight failed before expensive engine compilation')
print('PASS real iOS Rust archive links using production project library search paths (compile/link test, not device execution)')
