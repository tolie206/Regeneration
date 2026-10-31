from pathlib import Path
import zipfile,hashlib,unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Optimizer(unittest.TestCase):
 def test_only_two_requested_caps(self):
  path=ROOT/'app/Resources/Mugoat-PortLike-Traffic-v1.oiv'
  self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c')
  with zipfile.ZipFile(path) as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),{'assembly.xml','content/README.txt'})
   root=ET.fromstring(z.read('assembly.xml'));xml=root.find('content/xml');self.assertEqual(xml.attrib['path'],'common/data/gameconfig.xml')
   changes=xml.findall('replace');self.assertEqual(len(changes),2)
   self.assertEqual([(e[0].tag,e[0].attrib['value']) for e in changes],[('VehicleUpperLimit','20'),('VehicleParkedUpperLimit','15')])
   for e in changes:self.assertIn("Item[Platforms='pc']",e.attrib['xpath'])
 def test_home_mods_shortcut_reuses_existing_manager(self):
  home=(ROOT/'app/App/HomeView.swift').read_text(encoding='utf-8');controller=(ROOT/'app/App/NativePortViewController.swift').read_text(encoding='utf-8')
  self.assertIn('playButton, modsButton, preloadLabel',home)
  body=controller.split('private func showMods() {')[1].split('private func showSettings()')[0]
  self.assertIn('let page=ModsViewController()',body);self.assertIn('guard !engineStarted',body)
  self.assertNotIn('PGStartEngine',body)
if __name__=='__main__':unittest.main()
