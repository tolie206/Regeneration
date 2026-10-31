import hashlib,json,math,random,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def grade(rgb,p):
 sat,green,contrast,strength=p;r,g,b=rgb
 mask=max(0,min(1,(g-max(r,b)-.015)*5))
 boost=(sat-1)*(1-min(1,max(rgb)-min(rgb)))+(green-1)*mask
 l=sum(x*w for x,w in zip(rgb,[.2126,.7152,.0722]))
 return tuple(max(0,min(1,((l+(c-l)*(1+strength*boost))-.5)*(1+(contrast-1)*strength)+.5)) for c in rgb)
class Filter(unittest.TestCase):
 def test_legacy_shaders_bit_identical(self):
  s=(ROOT/'app/Source/MetalRenderer/MRRenderer.mm').read_text(encoding='utf-8')
  expected=json.loads((ROOT/'tests/fixtures/color_original_shaders.json').read_text())
  for n,h in expected.items():
   a=s.index('fragment float4 '+n+'(');b=s.index('\n',a) if n=='pg_blit' else s.index('\n}',a)+2
   self.assertEqual(hashlib.sha256(s[a:b].encode()).hexdigest(),h,n)
 def test_no_added_present_pass_or_texture_lookup(self):
  s=(ROOT/'app/Source/MetalRenderer/MRRenderer.mm').read_text(encoding='utf-8')
  a=s.index('static void present(');b=s.index('\n}',a);present=s[a:b]
  self.assertEqual(present.count('renderCommandEncoderWithDescriptor:'),1)
  self.assertEqual(present.count('drawPrimitives:'),1)
  self.assertIn('colorActive?colorPipe:basePipe',present)
  self.assertIn('if(colorActive){PGColorParams',present)
  for name,old in [('pg_blit_color','pg_blit'),('pg_blit_scaled_color','pg_blit_scaled'),('pg_blit_fxaa_color','pg_blit_fxaa')]:
   def section(n):
    a=s.index('fragment float4 '+n+'(');b=s.index('\n',a) if n in ['pg_blit','pg_blit_color'] else s.index('\n}',a)+2;return s[a:b]
   self.assertEqual(section(name).count('t.sample('),section(old).count('t.sample('))
   self.assertEqual(section(name).count('t.read('),section(old).count('t.read('))
 def test_green_reference_preserves_skin_neutrals_and_luma(self):
  p=(1,1.24,1,1)
  for c in [(0,0,0),(1,1,1),(.5,.5,.5),(.65,.42,.3),(.15,.2,.6)]:
   for a,b in zip(grade(c,p),c):self.assertAlmostEqual(a,b,places=6)
  c=(.25,.45,.2);out=grade(c,p);self.assertGreater(out[1]-out[0],c[1]-c[0]);self.assertAlmostEqual(sum(x*w for x,w in zip(c,[.2126,.7152,.0722])),sum(x*w for x,w in zip(out,[.2126,.7152,.0722])))
  rng=random.Random(42)
  for _ in range(10000):
   for p in [(1.04,1.12,1.01,1),(1,1.24,1,1),(1.1,1.16,1.025,1)]:
    self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in grade(tuple(rng.random() for i in range(3)),p)))
if __name__=='__main__':unittest.main()
