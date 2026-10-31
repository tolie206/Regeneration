from pathlib import Path
import importlib.util,tempfile,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('repack',ROOT/'tools/lossless_repack_ipa.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Repack(unittest.TestCase):
 def test_application_permissions_signature_and_symlink_bytes_identical(self):
  with tempfile.TemporaryDirectory() as temp:
   source=Path(temp)/'in.ipa';target=Path(temp)/'out.ipa'
   with zipfile.ZipFile(source,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    entry=zipfile.ZipInfo('Payload/Game.app/Game');entry.create_system=3;entry.external_attr=0o100755<<16;entry.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(entry,b'code-and-data'*10000,compresslevel=1)
    entry=zipfile.ZipInfo('Payload/Game.app/link');entry.create_system=3;entry.external_attr=0o120777<<16;z.writestr(entry,b'Game')
    z.writestr('Payload/Game.app/_CodeSignature/CodeResources',b'signature')
   report=mod.repack(source,target);self.assertLessEqual(report['output_bytes'],report['input_bytes']);self.assertFalse(report['runtime_RAM_or_FPS_change'])
   with zipfile.ZipFile(source) as a,zipfile.ZipFile(target) as b:self.assertEqual(mod.manifest(a),mod.manifest(b))
   with self.assertRaises(ValueError):mod.repack(source,source)
 def test_unsafe_or_duplicate_entries_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   source=Path(temp)/'bad.ipa'
   with zipfile.ZipFile(source,'w') as z:z.writestr('../escape',b'bad')
   with self.assertRaises(ValueError):mod.repack(source,Path(temp)/'out.ipa')
if __name__=='__main__':unittest.main()
