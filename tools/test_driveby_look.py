"""Execute production swipe code; L1 must not swallow vehicle aim motion."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
s=(root/'app/Source/EngineHost.c').read_text(encoding='utf8')
def section(start,end):
 a=s.index(start);return s[a:s.index(end,a)]
axis=section('static float pg_camera_swipe_axis(', '// Virtual pad:')
pack=section('static uint8_t pg_pad_axis(', 'static uint8_t pg_pad_trigger')
start=s.index('  if (dx != 0 || dy != 0) {',s.index('void pg_virtual_pad_apply'))
block=s[start:s.index('  uint8_t *base =',start)]
p=Path(sys.argv[1]);p.write_text('#include <math.h>\n#include <stdint.h>\n#include <stdbool.h>\n#include <assert.h>\n'+axis+pack+"""
static uint64_t apply(uint64_t packed,float dx,float dy,double elapsed){
"""+block+"""return packed;}
int main(void){
 uint64_t neutral=0x0000808080800000ull;
 for(unsigned bits=0;bits<65536;bits++){
  uint64_t p=neutral|bits,r=apply(p,24,-12,1.0/60);
  assert((r&65535)==bits);assert(((r>>32)&65535)!=((p>>32)&65535));
  assert(apply(p,0,0,1.0/60)==p);
 }
 return 0;
}
""")
subprocess.run(['clang','-std=c11',str(p),'-lm','-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS production swipe: all 65536 button combinations including L1 drive-by; neutral unchanged')

# Compile actual Swift mode-selection and aiming expressions with UI-free mocks.
sw=(root/'app/App/TouchControlsView.swift').read_text(encoding='utf8')
a=sw.index('    private var effectiveCameraMode:');b=sw.index('    /// Only the experimental',a)
mode=sw[a:b].replace('private var','var')
a=sw.index('    var aiming: Bool');b=sw.index('\n',a)
q=p.with_suffix('.swift')
q.write_text("""
import Foundation
final class GameSettings {
 static let shared=GameSettings()
 enum CameraTouchMode {case stick,swipePad,swipeMouse}
 var cameraTouchMode=CameraTouchMode.swipeMouse
 var targetingMode=1
}
final class Button {var pressed=false}
final class Controls {
 var aimActive=false
 let fire=Button(),leftFire=Button(),driveBy=Button(),driveAim=Button()
"""+mode+sw[a:b]+"""
}
let c=Controls()
assert(c.effectiveCameraMode == .swipeMouse)
c.driveAim.pressed=true
assert(c.aiming && c.effectiveCameraMode == .swipePad)
c.driveAim.pressed=false;c.driveBy.pressed=true
assert(c.aiming && c.effectiveCameraMode == .swipePad)
GameSettings.shared.targetingMode=3
assert(c.effectiveCameraMode == .swipeMouse)
print("PASS production Swift: drive aim/fire use controller assist; explicit free aim respected")
""")
subprocess.run(['swift',str(q)],check=True)
assert 'case fire, driveBy, driveAim:' in sw
assert 'guard swipeCameraEnabled, !has(isSelectionWheel)' in sw
