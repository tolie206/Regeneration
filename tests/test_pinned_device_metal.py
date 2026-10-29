import unittest,tempfile,json,hashlib,sys,shutil
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app/Scripts'))
import pinned_device_metal as metal
class PinnedDeviceMetal(unittest.TestCase):
 def test_actual_archive_integrity_and_complete_reflection(self):
  import zipfile
  folder=ROOT/'build-tools';meta=json.loads((folder/'r007-device-metal.json').read_text())
  archive=folder/'r007-device-metal.zip'
  self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),metal.PINNED_ARCHIVE_SHA256)
  with zipfile.ZipFile(archive) as z:
   self.assertEqual(set(z.namelist()),set(meta['files']))
   for name,sha in meta['files'].items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),sha)
   self.assertEqual(z.read('shaders-iphoneos.metallib')[:4],b'MTLB')
   refs=[json.loads(line)['h'] for line in z.read('shader-reflection.jsonl').splitlines()]
   self.assertEqual(len(refs),4808);self.assertEqual(len(set(refs)),4808)
  for name,sha in meta['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),sha)
 def test_simulator_is_not_silently_given_device_shaders(self):
  with self.assertRaisesRegex(RuntimeError,'device iOS only'):metal.install('unused',['iphonesimulator'])
 def test_wrong_shader_index_is_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'b/8b0b5899ed/shaders';p.mkdir(parents=True);(p/'index.json').write_text('{}')
   with self.assertRaisesRegex(RuntimeError,'index mismatch'):metal.install(folder,['iphoneos'])
