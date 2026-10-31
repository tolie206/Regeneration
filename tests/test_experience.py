import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("experience",ROOT/"app/Scripts/prepare_experience.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class Hooks(unittest.TestCase):
 def fixture(self):
  def volume(n,count):return "\nvoid w2c_game_f%d(w2c_game* instance, u64 var_p0, u64 var_p1) {\n"%n+"  w2c_game_f30(instance, var_j0, var_f1);\n"*count+"}\n"
  store="  f32_store_shared(base, size, memory, (u64)checked_add_u64(var_j0, 160u), var_f1);\n"
  return '#include "game.h"\n'+volume(10,6)+volume(20,4)+"\nvoid w2c_game_f40(w2c_game* instance, u64 var_p0) {\n"+store*3+"}\n"+volume(99,1)
 def test_only_engine_components_and_shooter_fov(self):
  src=self.fixture();out=mod.patch(src,10,20,30,40)
  self.assertEqual(out.count('pg_vehicle_engine_db(var_f1)'),10)
  self.assertEqual(out.count('pg_first_person_fov(var_f1)'),3)
  self.assertEqual(out[out.index('void w2c_game_f99'):],src[src.index('void w2c_game_f99'):])
  self.assertEqual(mod.patch(out,10,20,30,40),out)
 def test_changed_abi_stops_build(self):
  with self.assertRaises(RuntimeError):mod.patch(self.fixture().replace('160u','164u'),10,20,30,40)
  with self.assertRaises(RuntimeError):mod.patch(self.fixture().replace('w2c_game_f30(instance, var_j0, var_f1);','w2c_game_f30(instance, var_j0, var_f2);',1),10,20,30,40)
 def test_new_ui_does_not_duplicate_importer(self):
  home=(ROOT/'app/App/HomeView.swift').read_text(encoding='utf-8')
  self.assertIn('playButton, modsButton, preloadLabel',home)
  controller=(ROOT/'app/App/NativePortViewController.swift').read_text(encoding='utf-8')
  body=controller.split('private func showMods() {')[1].split('private func showSettings()')[0]
  self.assertIn('let page=ModsViewController()',body)
  self.assertNotIn('PGStartEngine',body)
if __name__=='__main__':unittest.main()
