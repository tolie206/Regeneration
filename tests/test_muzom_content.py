import hashlib,io,json,unittest,wave,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class Content(unittest.TestCase):
 def test_exact_bundled_inputs(self):
  expected=json.loads((R/'muzom-inputs/content-manifest.json').read_text(encoding='utf8'))
  with zipfile.ZipFile(R/'app/Resources/MuZomContent.zip') as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),set(expected))
   for n,h in expected.items(): self.assertEqual(hashlib.sha256(z.read(n)).hexdigest(),h,n)
   for name in ['mz_human','mz_docz']:
    for ext in ['ydd','yft','ymt','ytd']:self.assertTrue(z.read(name+'/'+name+'.'+ext).startswith(b'RSC7'))
   banks=[n for n in z.namelist() if n.endswith('.awc')];self.assertEqual(len(banks),24)
   for n in banks:self.assertTrue(z.read(n).startswith(b'ADAT'));self.assertNotIn('explosion',n)
   for i in range(8):
    with wave.open(io.BytesIO(z.read('groans/groan'+str(i)+'.wav'))) as w:
     self.assertEqual(w.getnchannels(),1);self.assertEqual(w.getsampwidth(),2);self.assertLessEqual(w.getnframes()/w.getframerate(),4)
