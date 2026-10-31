from pathlib import Path
import hashlib,zipfile,xml.etree.ElementTree as ET,importlib.util,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bike',ROOT/'app/Scripts/prepare_bike_body.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class BikeOptimizer(unittest.TestCase):
 def test_asset_free_optimizer_only_two_population_caps(self):
  p=ROOT/'app/Resources/Mugoat-PortLike-Traffic-v1.oiv'
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c')
  with zipfile.ZipFile(p) as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),{'assembly.xml','content/README.txt'})
   tree=ET.fromstring(z.read('assembly.xml'));xml=tree.find('content/xml');self.assertEqual(xml.attrib['path'],'common/data/gameconfig.xml')
   replacements=xml.findall('replace');self.assertEqual(len(replacements),2)
   self.assertEqual([(e[0].tag,e[0].attrib['value']) for e in replacements],[('VehicleUpperLimit','20'),('VehicleParkedUpperLimit','15')])
   for e in replacements:self.assertIn("Item[Platforms='pc']",e.attrib['xpath'])
 def test_draw_hook_is_early_and_idempotent(self):
  s='#include "game.h"\nu64 w2c_game_f10(w2c_game* instance, u64 var_p0, u64 var_p1, u64 var_p2) {\nFUNC_PROLOGUE;\nu64 var_j0=0;\nFUNC_EPILOGUE;\nreturn var_j0;\n}\n'
  out=mod.patch(s,10);self.assertEqual(mod.patch(out,10),out)
  self.assertLess(out.index('if(pg_hide_bike_body('),out.index('FUNC_PROLOGUE;'))
  self.assertIn('pg_hide_bike_body(instance,var_p1)',out)
if __name__=='__main__':unittest.main()
