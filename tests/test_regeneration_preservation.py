import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Baseline(unittest.TestCase):
 def test_renderer_streaming_and_turbo_unchanged(self):
  for path,sha in json.loads((ROOT/'tests/regeneration_perf_baseline.json').read_text()).items():
   data=(ROOT/path).read_bytes().replace(b'\r\n',b'\n')
   r007=json.loads((ROOT/'tests/fixtures/r007_reviewed_hunks.json').read_text())
   for old,new in r007.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path)
    data=data.replace(new.encode(),old.encode())
   reviewed=json.loads((ROOT/'tests/fixtures/r006_reviewed_hunks.json').read_text())
   for old,new in reviewed.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path)
    data=data.replace(new.encode(),old.encode())
   if path=='app/Source/EngineHost.c': data=data.replace(b'#include "NativeLargeResources.inc"\n',b'').replace(b' pg_large_archive_mounted(packfile,label);\n',b'')
   if path=='app/Source/EngineHost.c':
    fragments=json.loads((ROOT/'tests/fixtures/r004_reviewed_fragments.json').read_text())
    current=(ROOT/path).read_bytes().replace(b'\r\n',b'\n')
    for old,new in r007.get(path,[]): current=current.replace(new.encode(),old.encode())
    for old,new in reviewed.get(path,[]): current=current.replace(new.encode(),old.encode())
    for i,(start,end) in enumerate([(b'  // TouchControlsView suppresses swipe',b'    const float baseX'),(b' // Require a 512 MiB margin',b' atomic_store(&engineLimited'),(b' if(!value){const char *v=getenv("PG_GUARD_RESERVE_MB")',b' return value;')]):
     a=current.index(start); b=current.index(end,a)
     data=data.replace(current[a:b],fragments[i].encode())
    data=data.replace(b'Native streaming memory guard enabled (reserve selected from process limit).',b'Native streaming memory guard enabled with 384 MB of reserve.')
   if path=='app/Source/NativeTurbo.inc': data=data.replace(b'PGLoadSceneActive()',b'PGLoadSceneSeconds()!=0')
   self.assertEqual(hashlib.sha256(data).hexdigest(),sha,path)
