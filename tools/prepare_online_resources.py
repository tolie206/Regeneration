from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
folder=root/'app/Resources/TrustedOnlineAssets';folder.mkdir(exist_ok=True,parents=True)
# This translation is shipped in the signed application, not imported from Documents/Mods.
with zipfile.ZipFile(root/'app/Resources/VietnameseAccented.zip') as z:
 for n in z.namelist():
  p=Path(n)
  if p.is_absolute() or '..' in p.parts:raise ValueError(n)
  z.extract(n,folder)
