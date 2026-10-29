"""Build pinned WABT 1.0.42 for an Intel Mac; generated iOS C stays ARM64-targeted."""
import hashlib,subprocess,tarfile,urllib.request
from pathlib import Path
from safe_extract import extract

def prepare(tools):
 tools=Path(tools);archive=tools/'wabt-host-source.tar.gz'
 archive.write_bytes(urllib.request.urlopen('https://codeload.github.com/WebAssembly/wabt/tar.gz/refs/tags/1.0.42',timeout=120).read())
 if hashlib.sha256(archive.read_bytes()).hexdigest()!='2b2e2ee7c10d7de7cd391fa82f2b1e74f7d5db56ce1bcbcf65ebe1f826d01910':raise RuntimeError('WABT source checksum mismatch')
 sourceRoot=tools/'wabt-host-source';sourceRoot.mkdir(exist_ok=True)
 with tarfile.open(archive) as package:extract(package,sourceRoot)
 source=sourceRoot/'wabt-1.0.42';build=tools/'wabt-host-build';prefix=(tools/'wabt-1.0.42').resolve()
 openssl=subprocess.check_output(['brew','--prefix','openssl@3'],text=True).strip()
 args=['cmake','-S',str(source),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_OSX_ARCHITECTURES=x86_64','-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DBUILD_TESTS=OFF','-DBUILD_TOOLS=OFF','-DBUILD_LIBWASM=OFF','-DUSE_INTERNAL_SHA256=OFF','-DOPENSSL_ROOT_DIR='+openssl]
 subprocess.run(args,check=True)
 # Fail instead of silently switching hash implementations/submodules.
 config=(build/'include/wabt/config.h').read_text()
 if '#define HAVE_OPENSSL_SHA_H 1' not in config:raise RuntimeError('Host WABT must use the available OpenSSL SHA256 interface')
 subprocess.run(['cmake','--build',str(build),'--target','wabt','wasm-rt-impl','--parallel','3'],check=True)
 subprocess.run(['cmake','--install',str(build),'--component','wabt-development'],check=True)
 for rel in ['lib/libwabt.a','include/wabt/config.h','share/wabt/wasm2c/wasm-rt-impl.c']:
  if not (prefix/rel).is_file():raise RuntimeError('Incomplete host WABT install: '+rel)
