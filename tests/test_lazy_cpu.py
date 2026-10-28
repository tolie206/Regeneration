import unittest,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app/Scripts'))
import prepare_lazy_cpu as patch
IDS=dict(zip((*patch.CREATE,*patch.ACCESS),(324,325,326,327,483,515,517,518,519)))
FIX=ROOT/'tests/fixtures/lazy_cpu'
class LazyCPU(unittest.TestCase):
 def test_real_engine_contract_and_idempotence(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'game_0.c'
   s='#include "game-impl.h"\n'+''.join((FIX/f'f{n}.c.txt').read_text() for n in IDS.values())
   p.write_text(s);patch.patch_files(Path(tmp),IDS.__getitem__)
   first=p.read_text();patch.patch_files(Path(tmp),IDS.__getitem__)
   self.assertEqual(first,p.read_text());self.assertEqual(first.count(patch.MARK),9)
   for name,n in IDS.items():
    after=patch.patch_body((FIX/f'f{n}.c.txt').read_text(),name)
    if name in patch.CREATE:
     kind,off,label=patch.CREATE[name]
     self.assertIn(f'var_p0,var_p1,var_p2,{kind}',after)
     self.assertLess(after.index('pg_lazy_cpu_create'),after.index('w2c_game_f91003('))
     self.assertIn(f'goto {label};',after)
    else:
     for arg in patch.ACCESS[name]:self.assertIn(f'pg_lazy_cpu_need(instance,{arg});',after)
 def test_changed_layout_fails_closed_without_writes(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'game_0.c'
   s='#include "game-impl.h"\n'+''.join((FIX/f'f{n}.c.txt').read_text() for n in IDS.values())
   s=s.replace('152u','153u');p.write_text(s)
   with self.assertRaises(RuntimeError):patch.patch_files(Path(tmp),IDS.__getitem__)
   self.assertEqual(p.read_text(),s)
 def test_guest_destructors_only_free_nonnull_cpu_shadows(self):
  for n,off in ((310,144),(367,120),(379,128),(390,136)):
   s=(FIX/f'f{n}.c.txt').read_text();pointer=s.index(f'{off}u)');counter=s.index('8324208ull')
   self.assertLess(pointer,counter);self.assertIn('if (var_i0) {',s[pointer:counter])
 def test_preserve_gpu_and_world(self):
  s=(ROOT/'app/Source/NativeLazyCPU.inc').read_text()
  for call in ('madvise(','mprotect(','DELETE_ENTITY'):self.assertNotIn(call,s)
if __name__=='__main__':unittest.main()
