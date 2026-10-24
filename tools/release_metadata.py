"""Fail before compilation if XcodeGen would overwrite the intended release version."""
import plistlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate_sources(root=ROOT):
    source = plistlib.loads((root / 'app/App/Info.plist').read_bytes())
    project = (root / 'app/project.yml').read_text(encoding='utf8')
    expected = {}
    for key in ('CFBundleShortVersionString', 'CFBundleVersion'):
        matches = re.findall(r'^\s*' + key + r':\s*"([^"]+)"\s*$', project, re.M)
        if len(matches) != 1:
            raise ValueError(f'Expected one explicit {key} in app/project.yml')
        value = source.get(key)
        if value != matches[0]:
            raise ValueError(f'{key} mismatch: Info.plist={value!r}, project.yml={matches[0]!r}; XcodeGen would overwrite the release metadata')
        expected[key] = value
    return expected

if __name__ == '__main__':
    print('PASS release metadata:', validate_sources())
