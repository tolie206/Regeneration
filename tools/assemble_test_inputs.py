from pathlib import Path
import sys,hashlib,json,zipfile,tempfile
root=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
meta=json.loads((root/'test-inputs/index.json').read_text())
with tempfile.TemporaryFile() as f:
 h=hashlib.sha256();total=0
 for name in meta['parts']:
  b=(root/'test-inputs'/name).read_bytes();f.write(b);h.update(b);total+=len(b)
 assert h.hexdigest()==meta['sha256'] and total==meta['bytes']
 f.seek(0)
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None
  z.extractall(out)
print('Real mod/save fixtures verified and assembled')
