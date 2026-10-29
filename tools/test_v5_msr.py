"""Compile and execute the actual scale math and C configuration; compile Metal/iOS code on CI."""
from pathlib import Path
import subprocess,sys,tempfile,re
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as folder:
 tmp=Path(folder)
 swift=(root/'app/App/MSRSettings.swift').read_text().split('extension GameSettings')[0]
 swift+='\nfor mode in MSRMode.allCases {\n for (w,h) in [(1920,1080),(1600,900),(960,540),(640,360),(2868,1320)] {\n  let (rw,rh)=mode.renderSize(outputWidth:w,outputHeight:h)\n  assert(rw%2==0 && rh%2==0 && rw>=320 && rh>=180)\n  assert(rw<=w && rh<=h)\n  if mode == .off {assert(rw==w && rh==h)}\n  else {assert(Double(rw*rh)<Double(w*h));assert(abs(Double(rw)/Double(rh)-Double(w)/Double(h))<0.02)}\n }\n}\nprint("PASS: real MSR scale math, alignment, aspect and Off")\n'
 src=tmp/'main.swift';src.write_text(swift)
 subprocess.run(['swiftc',str(src),'-o',str(tmp/'scale')],check=True);subprocess.run([str(tmp/'scale')],check=True)
 c=tmp/'config.c';c.write_text('#include "NativeMSR.h"\n#include <assert.h>\nint main(){for(int m=1;m<=3;m++){uint64_t c=pg_msr_configuration(m,1920,1080);assert(pg_msr_mode(c)==(unsigned)m&&pg_msr_width(c)==1920&&pg_msr_height(c)==1080);}assert(!pg_msr_configuration(0,1920,1080));assert(!pg_msr_configuration(4,1920,1080));assert(!pg_msr_configuration(1,1919,1080));assert(!pg_msr_configuration(1,1920,179));assert(!pg_msr_configuration(1,8194,1080));return 0;}')
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-I',str(root/'app/Source'),str(c),'-o',str(tmp/'config')],check=True);subprocess.run([str(tmp/'config')],check=True)
 # Native renderer checked against the real device SDK before the expensive engine build.
 sdk=subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-path'],text=True).strip()
 subprocess.run(['xcrun','clang++','-fsyntax-only','-std=c++17','-fobjc-arc','-target','arm64-apple-ios16.0','-isysroot',sdk,'-I',str(root/'app/Source'),'-I',str(root/'app/Source/MetalRenderer'),str(root/'app/Source/MetalRenderer/MRRenderer.mm')],check=True)
 subprocess.run(['xcrun','clang++','-fsyntax-only','-std=c++17','-fobjc-arc','-target','arm64-apple-ios16.0','-isysroot',sdk,'-I',str(root/'app/Source'),'-I',str(root/'app/Source/MetalRenderer'),str(root/'app/Source/MetalRenderer/MRFrameReports.mm')],check=True)
 renderer=(root/'app/Source/MetalRenderer/MRRenderer.mm').read_text()
 start=renderer.index('R"(');end=renderer.index(')"',start)
 metal=tmp/'helpers.metal';metal.write_text(renderer[start+3:end])
 subprocess.run(['xcrun','-sdk','iphoneos','metal','-c',str(metal),'-o',str(tmp/'helpers.air')],check=True)
print('PASS: MSR C/Swift execution and iOS renderer/helper Metal compilation')
