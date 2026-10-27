from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]/'app'
sdk=subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-path'],text=True).strip()
files=[str(p) for p in (r/'App').rglob('*.swift')]
args=['xcrun','swiftc','-typecheck','-D','MUGOAT_ONLINE','-target','arm64-apple-ios16.0','-sdk',sdk,'-import-objc-header',str(r/'Source/Native-Bridging-Header.h'),'-I',str(r/'App/GameInstaller'),'-I',str(r/'Vendor/libarchive.xcframework/ios-arm64/Headers')]+files
subprocess.run(args,check=True)
print('PASS all production Swift sources typecheck for iPhoneOS with online-only flag')
