from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','diff','--name-only','099b0da','HEAD','--','app/Source','app/Scripts','inputs'],cwd=root,text=True).splitlines()
assert set(paths)<={'app/Source/MetalGraphicsHost.mm','app/Source/PortDataTextureBudget.h'},paths
original=subprocess.check_output(['git','show','099b0da:app/Source/MetalGraphicsHost.mm'],cwd=root)
current=(root/'app/Source/MetalGraphicsHost.mm').read_bytes().replace(b'\r\n',b'\n')
assert current[current.index(b'void PGNoteTextureRatio'):]==original[original.index(b'void PGNoteTextureRatio'):]
assert current[:current.index(b'// What BC textures')].replace(b'#include "PortDataTextureBudget.h"\n',b'')==original[:original.index(b'// What BC textures')]
print('PASS unchanged engine/renderer/inputs and runtime measurements; boot-only estimate/cache patch isolated')
