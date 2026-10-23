import unittest,zipfile,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Bundled(unittest.TestCase):
 def test_integrity_manifest_matches_actual_translation(self):
  index=json.loads((ROOT/'app/Resources/VietnameseIntegrity.json').read_text())
  for mode,name in [('1','VietnameseAccented'),('2','VietnamesePlain')]:
   with zipfile.ZipFile(ROOT/f'app/Resources/{name}.zip') as z:
    self.assertIsNone(z.testzip());self.assertEqual(index[mode],{n:len(z.read(n)) for n in z.namelist()})
 def test_menyoo_has_translation_matching_keys_and_original_licenses(self):
  with zipfile.ZipFile(ROOT/'app/Resources/BundledMenyoo.zip') as z:
   self.assertIsNone(z.testzip());self.assertEqual(z.read('Menyoo-iOS.asi')[:2],b'MZ')
   for n in ['LICENSE.txt','CREDITS.txt','COPYING.txt']:self.assertGreater(len(z.read(n)),100)
   fr=json.loads(z.read('menyooStuff/Language/French.json').decode('utf-8-sig'))
   vi=json.loads(z.read('menyooStuff/Language/Vietnamese.json'))
   self.assertTrue(set(fr).issubset(vi));self.assertIn(b'language=Vietnamese',z.read('menyooStuff/menyooConfig.ini'))
if __name__=='__main__':unittest.main()
