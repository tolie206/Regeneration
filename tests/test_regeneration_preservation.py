import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Baseline(unittest.TestCase):
 def test_renderer_streaming_and_turbo_unchanged(self):
  for path,sha in json.loads((ROOT/'tests/regeneration_perf_baseline.json').read_text()).items():
   self.assertEqual(hashlib.sha256((ROOT/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),sha,path)
