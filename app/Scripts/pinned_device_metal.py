"""Reuse the byte-identical device metallib from verified R007 build 1016.
Same engine/shader index, shader translator, binding ABI and Xcode 26.2 (17C52).
This replaces only an ARM-hosted build tool, not any renderer code or iOS CPU code.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PINNED_ARCHIVE_SHA256='d9b8c9fc1ce511728e842e6e38544d38daf6e03dfb8f9738a28ebf85d11ea92e'

def install(mirror,sdks):
 if sdks!=['iphoneos']:raise RuntimeError('Pinned resources cover device iOS only; simulator requires native shader translator')
 folder=ROOT.parent/'build-tools';archive=folder/'r007-device-metal.zip';meta=json.loads((folder/'r007-device-metal.json').read_text())
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=PINNED_ARCHIVE_SHA256:raise RuntimeError('Pinned shader archive mismatch')
 indexPath=Path(mirror)/'b/8b0b5899ed/shaders/index.json'
 if hashlib.sha256(indexPath.read_bytes()).hexdigest()!=meta['shader_index_sha256']:raise RuntimeError('Pinned shader index mismatch')
 version=subprocess.check_output(['xcodebuild','-version'],text=True)
 if 'Xcode 26.2\n' not in version or 'Build version 17C52' not in version:raise RuntimeError('Pinned Metal resources require the exact original Xcode build')
 # Refuse reuse if translator or binding/reflection loader changed since R007.
 for name,sha in meta['source_sha256'].items():
  if hashlib.sha256((ROOT.parent/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=sha:raise RuntimeError('Shader source/ABI changed: '+name)
 with zipfile.ZipFile(archive) as z:
  expected={'shaders-iphoneos.metallib','shader-reflection.jsonl'}
  if set(z.namelist())!=expected:raise RuntimeError('Unexpected pinned shader archive entries')
  files={n:z.read(n) for n in expected}
 for name,data in files.items():
  if hashlib.sha256(data).hexdigest()!=meta['files'][name]:raise RuntimeError('Pinned shader checksum mismatch: '+name)
 index=json.loads(indexPath.read_bytes());wanted={h for h,r in index.items() if not h.startswith('_') and r.get('ok') and r['stage'] in ('vs','ps','cs')}
 actual={json.loads(line)['h'] for line in files['shader-reflection.jsonl'].splitlines()}
 if wanted!=actual:raise RuntimeError('Shader coverage mismatch')
 out=ROOT/'GeneratedResources';out.mkdir(exist_ok=True)
 for name,data in files.items():(out/name).write_bytes(data)
 print('Pinned device Metal: exact R007 binaries, '+str(len(actual))+' shaders verified; V5 helper shader remains source-compiled.')
