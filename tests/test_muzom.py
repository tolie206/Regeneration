import unittest,sys,json,plistlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from muzom_maps import convert
class MuZom(unittest.TestCase):
 def test_source_maps_strict_and_generated(self):
  text,report=convert();self.assertEqual(report['raw_placements'],5450);self.assertEqual(report['selected'],741);self.assertEqual((R/'app/Source/MuZomMapData.h').read_text(),text)
 def test_isolated_identity_and_mode(self):
  info=plistlib.loads((R/'app/App/Info.plist').read_bytes());self.assertEqual(info['CFBundleDisplayName'],'MuZom')
  project=(R/'app/project.yml').read_text();self.assertIn('PRODUCT_BUNDLE_IDENTIFIER: vn.gta.muzom',project)
  s=(R/'app/App/NativePortViewController.swift').read_text(encoding='utf8');self.assertIn('PGSetZombieMode(mode == .zombie)',s);self.assertIn('testMap ? 3 : mode.engineStartMode',s)
  settings=(R/'app/App/GameSettings.swift').read_text(encoding='utf8');self.assertIn('case zombie = 4',settings);self.assertIn('self == .story ? 1 : 2',settings)
