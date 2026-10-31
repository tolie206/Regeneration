from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
sdk=subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-path'],text=True).strip()
for name in ['MetalRenderer/MRRenderer.mm','MetalGraphicsHost.mm']:
 subprocess.run(['xcrun','clang++','-fsyntax-only','-std=c++20','-fobjc-arc','-target','arm64-apple-ios16.0','-isysroot',sdk,'-I',str(root/'app/Source'),'-I',str(root/'app/Source/MetalRenderer'),str(root/'app/Source'/name)],check=True)
with tempfile.TemporaryDirectory() as folder:
 s=(root/'app/Source/MetalRenderer/MRRenderer.mm').read_text();a=s.index('R"(');b=s.index(')"',a)
 p=Path(folder)/'helpers.metal';p.write_text(s[a+3:b]);subprocess.run(['xcrun','-sdk','iphoneos','metal','-std=metal3.0','-c',str(p),'-o',folder+'/helpers.air'],check=True)
print('PASS: FIX renderer/bridge device syntax and actual FXAA Metal shader compile')

release=subprocess.check_output(['xcrun','clang++','-E','-P','-DMR_TRACE=0','-std=c++20','-fobjc-arc','-target','arm64-apple-ios16.0','-isysroot',sdk,'-I',str(root/'app/Source'),'-I',str(root/'app/Source/MetalRenderer'),str(root/'app/Source/MetalRenderer/MRRenderer.mm')],text=True)
assert 'R->colorBlitPipe=' in release and 'R->colorScaledPipe=' in release and 'R->colorFXAAPipe=' in release,'Release must create filter pipelines'
assert 'T.alphaPipe =' not in release,'Trace remains disabled in release'
print('PASS actual MR_TRACE=0 Release creates all filter pipelines with trace excluded')
