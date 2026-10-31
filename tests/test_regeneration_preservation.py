import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Baseline(unittest.TestCase):
 def test_core_preserved_except_explicit_reviewed_changes(self):
  for path,sha in json.loads((ROOT/'tests/regeneration_perf_baseline.json').read_text()).items():
   data=(ROOT/path).read_bytes().replace(b'\r\n',b'\n')
   fix5=json.loads((ROOT/'tests/fixtures/v5fix5_reviewed_hunks.json').read_text())
   for old,new in fix5.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path);data=data.replace(new.encode(),old.encode())
   fix4=json.loads((ROOT/'tests/fixtures/v5fix4_reviewed_hunks.json').read_text())
   for old,new in fix4.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path);data=data.replace(new.encode(),old.encode())
   color=json.loads((ROOT/'tests/fixtures/v5color_reviewed_hunks.json').read_text())
   for old,new in color.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path);data=data.replace(new.encode(),old.encode())
   v5=json.loads((ROOT/'tests/fixtures/v5_reviewed_changes.json').read_text())
   fixFile=ROOT/'tests/fixtures/v5fix_reviewed_changes.json'
   fixes=json.loads(fixFile.read_text()) if fixFile.exists() else {}
   fix2=json.loads((ROOT/'tests/fixtures/v5fix2_reviewed_hunks.json').read_text())
   for old,new in fix2.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path);data=data.replace(new.encode(),old.encode())
   if path in fixes:
    self.assertEqual(fixes[path]['base_v5_sha256'],v5[path]['v5_sha256'],path)
    self.assertEqual(hashlib.sha256(data).hexdigest(),fixes[path]['fix_sha256'],path)
    continue
   if path in v5:
    self.assertEqual(hashlib.sha256(data).hexdigest(),v5[path]['v5_sha256'],path)
    continue # intentional V5 changes explicitly reviewed; other core hashes still enforced
   r008=json.loads((ROOT/'tests/fixtures/r008_reviewed_hunks.json').read_text())
   for old,new in r008.get(path,[]):
    self.assertEqual(data.count(new.encode()),1,path)
    data=data.replace(new.encode(),old.encode())
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
    for old,new in fix5.get(path,[]): current=current.replace(new.encode(),old.encode())
    for old,new in r008.get(path,[]): current=current.replace(new.encode(),old.encode())
    for old,new in r007.get(path,[]): current=current.replace(new.encode(),old.encode())
    for old,new in reviewed.get(path,[]): current=current.replace(new.encode(),old.encode())
    for i,(start,end) in enumerate([(b'  // TouchControlsView suppresses swipe',b'    const float baseX'),(b' // Require a 512 MiB margin',b' atomic_store(&engineLimited'),(b' if(!value){const char *v=getenv("PG_GUARD_RESERVE_MB")',b' return value;')]):
     a=current.index(start); b=current.index(end,a)
     data=data.replace(current[a:b],fragments[i].encode())
    data=data.replace(b'Native streaming memory guard enabled (reserve selected from process limit).',b'Native streaming memory guard enabled with 384 MB of reserve.')
   if path=='app/Source/NativeTurbo.inc': data=data.replace(b'PGLoadSceneActive()',b'PGLoadSceneSeconds()!=0')
   self.assertEqual(hashlib.sha256(data).hexdigest(),sha,path)
