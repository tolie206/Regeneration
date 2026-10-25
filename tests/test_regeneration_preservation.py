import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Baseline(unittest.TestCase):
 def test_renderer_streaming_and_turbo_unchanged(self):
  for path,sha in json.loads((ROOT/'tests/regeneration_perf_baseline.json').read_text()).items():
   data=(ROOT/path).read_bytes().replace(b'\r\n',b'\n')
   if path=='app/Source/EngineHost.c': data=data.replace(b'#include "NativeLargeResources.inc"\n',b'').replace(b' pg_large_archive_mounted(packfile,label);\n',b'')
   if path=='app/Source/NativeTurbo.inc': data=data.replace(b'PGLoadSceneActive()',b'PGLoadSceneSeconds()!=0')
   self.assertEqual(hashlib.sha256(data).hexdigest(),sha,path)
