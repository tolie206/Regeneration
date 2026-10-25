import unittest,tempfile,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Resource32(unittest.TestCase):
 def test_actual_pinned_size_read_and_schedule_sites(self):
  with tempfile.TemporaryDirectory() as d:
   app=Path(d);(app/'Scripts').mkdir();(app/'Generated').mkdir()
   for name in ['prepare_large_resources.py','engine_names.py']:shutil.copyfile(ROOT/'app/Scripts'/name,app/'Scripts'/name)
   shutil.copyfile(ROOT/'tests/fixtures/resource32-funcnames.tsv',app/'Generated/funcnames.tsv')
   out=app/'Generated/game_0.c';shutil.copyfile(ROOT/'tests/fixtures/resource32-pinned.c',out)
   subprocess.run([sys.executable,str(app/'Scripts/prepare_large_resources.py')],check=True,capture_output=True)
   text=out.read_text();self.assertEqual(text.count('= pg_large_rpf_size('),14)
   subprocess.run([sys.executable,str(app/'Scripts/prepare_large_resources.py')],check=True,capture_output=True)
   self.assertEqual(text,out.read_text())
   out.write_text((ROOT/'tests/fixtures/resource32-pinned.c').read_text().replace('16777215u;','16777214u;',1))
   self.assertNotEqual(subprocess.run([sys.executable,str(app/'Scripts/prepare_large_resources.py')],capture_output=True).returncode,0)
