import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("experience",ROOT/"app/Scripts/prepare_experience.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Hooks(unittest.TestCase):
 def fixture(self):
  def func(n,body):return "\nvoid w2c_game_f%d(w2c_game* instance, u64 var_p0, u64 var_p1) {\nFUNC_PROLOGUE;\n"%n+body+"\nFUNC_EPILOGUE;\n}\n"
  return '#include "game.h"\n'+func(10," w2c_game_f20(instance, var_j0, var_i1, var_f2, var_f3);\n"*6)+func(30,"var_j1 = 48ull;\nvar_j2 = 272ull;")+func(40,'nativeUpdate();')+func(50,'nativeUpdate();')+func(60,'generate();')+func(99,'setNpcVolume();')
 def test_only_final_frame_and_linear_granular_channel(self):
  src=self.fixture();out=mod.patch(src,10,20,30,40,50,60)
  self.assertEqual(out.count('pg_vehicle_grain_gain(var_f2)'),6)
  self.assertNotIn('pg_first_person_fov(var_f1)',out)
  self.assertEqual(out.count('pg_camera_frame_end(instance,'),1)
  self.assertEqual(out[out.index('void w2c_game_f99'):],src[src.index('void w2c_game_f99'):])
  self.assertEqual(mod.patch(out,10,20,30,40,50,60),out)
 def test_changed_abi_stops_build(self):
  with self.assertRaises(RuntimeError):mod.patch(self.fixture().replace('272ull','280ull'),10,20,30,40,50,60)
  with self.assertRaises(RuntimeError):mod.patch(self.fixture().replace('var_f2, var_f3);','var_f4, var_f3);',1),10,20,30,40,50,60)
if __name__=='__main__':unittest.main()
