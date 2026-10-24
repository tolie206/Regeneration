import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app/Scripts'))
spec=importlib.util.spec_from_file_location('prepare_turbo',ROOT/'app/Scripts/prepare_turbo.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Turbo(unittest.TestCase):
    def test_hook_fails_closed_and_is_idempotent(self):
        anchor='  var_B124:;\n  f32_store_shared(wasm_rt_local_memory_base, wasm_rt_local_memory_size, instance->w2c_env_memory, (u64)checked_add_u64(var_j0, 100u), var_f1);'
        result=module.patch_body(anchor)
        self.assertIn('pg_native_turbo_boost(var_p1, var_p6,',result)
        self.assertEqual(module.patch_body(result),result)
        with self.assertRaises(RuntimeError):module.patch_body(anchor.replace('100u','104u'))
        with self.assertRaises(RuntimeError):module.patch_body(anchor+anchor)

    def test_every_audio_sample_is_pcm_and_matches_manifest(self):
        root=ROOT/'app/TurboSounds'
        manifest=json.loads((root/'manifest.json').read_text())
        actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*.wav')}
        self.assertEqual(actual,manifest['sha256']);self.assertEqual(len(actual),46)
        for path in actual:
            with wave.open(str(root/path)) as sample:
                self.assertEqual(sample.getcomptype(),'NONE');self.assertGreater(sample.getnframes(),0)
                self.assertIn(sample.getnchannels(),[1,2]);self.assertLess(sample.getnframes()/sample.getframerate(),4)
        self.assertNotIn('Default/EX_POP_34.wav',actual)

if __name__=='__main__':unittest.main()
