import unittest,tempfile,sys,shlex
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ccache_engine import cache_args
class CacheArgs(unittest.TestCase):
 def test_only_inert_module_flags_removed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'args with space.rsp';items=['-O2','-fmodules','-fbuild-session-file=/tmp/session','-fmodules-cache-path=/tmp/cache','-Iheader folder','-DNAME=a b','-include','NativeRuntime.h']
   p.write_text(shlex.join(items));actual=cache_args(['@'+str(p),'-fno-modules','-c','Generated/game_0.c'])
   self.assertEqual(actual,['-O2','-Iheader folder','-DNAME=a b','-include','NativeRuntime.h','-fno-modules','-c','Generated/game_0.c'])
 def test_real_modules_never_stripped(self):
  self.assertIsNone(cache_args(['-fmodules','-c','Generated/game_0.c']))
  self.assertIsNone(cache_args(['-fno-modules','-fmodules']))
if __name__=='__main__':unittest.main()
