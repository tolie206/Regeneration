import plistlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from release_metadata import validate_sources

class ReleaseMetadata(unittest.TestCase):
    def test_release_sources_agree_before_xcodegen(self):
        self.assertEqual(validate_sources()['CFBundleVersion'], '1010')

    def test_stale_xcodegen_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'app/App').mkdir(parents=True)
            source = {'CFBundleShortVersionString': '1.4.4', 'CFBundleVersion': '1010'}
            (root / 'app/App/Info.plist').write_bytes(plistlib.dumps(source))
            for stale_key in source:
                project = dict(source)
                project[stale_key] = '1007' if stale_key == 'CFBundleVersion' else '1.4.3'
                (root / 'app/project.yml').write_text('\n'.join(f'{k}: "{v}"' for k, v in project.items()), encoding='utf8')
                with self.subTest(key=stale_key), self.assertRaisesRegex(ValueError, stale_key + ' mismatch'):
                    validate_sources(root)
