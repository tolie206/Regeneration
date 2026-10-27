from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parents[1]/'app'
sdk=subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-path'],text=True).strip()
files=[str(p) for p in (r/'App').rglob('*.swift')]
args=['xcrun','swiftc','-typecheck','-D','MUGOAT_ONLINE','-target','arm64-apple-ios16.0','-sdk',sdk,'-import-objc-header',str(r/'Source/Native-Bridging-Header.h'),'-I',str(r/'App/GameInstaller'),'-I',str(r/'Vendor/libarchive.xcframework/ios-arm64/Headers')]+files
if '--c-only' not in sys.argv:
    subprocess.run(args,check=True)
    print('PASS all production Swift sources typecheck for iPhoneOS with online-only flag')
if '--swift-only' in sys.argv:
    raise SystemExit(0)

# Compile the generated production bridge against the actual iOS headers, not mock declarations.
subprocess.run(['xcrun','clang','-fsyntax-only','-target','arm64-apple-ios16.0','-isysroot',sdk,'-std=c11','-DPG_ROLEPLAY_CLIENT=1','-DWASM_RT_USE_MMAP=0','-DWASM_RT_MEMCHECK_BOUNDS_CHECK=1','-include',str(r/'Source/NativeRuntime.h'),'-I',str(r/'Source'),'-I',str(r/'Tools/simde'),'-I',str(r/'Generated'),'-I',str(r/'Tools/wabt-1.0.42/include'),'-I',str(r/'Tools/wabt-1.0.42/share/wabt/wasm2c'),str(r/'Generated/MugoatCommands.c')],check=True)
print('PASS generated native C online bridge with original engine headers')
