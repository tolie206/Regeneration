import hashlib,json,sys,zipfile,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'repair-inputs';index=json.loads((root/'index.json').read_text());out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryFile() as f:
 h=hashlib.sha256();size=0
 for p in index['parts']:
  b=(root/p['name']).read_bytes();assert len(b)==p['size'] and hashlib.sha256(b).hexdigest()==p['sha256'];f.write(b);h.update(b);size+=len(b)
 assert size==index['size'] and h.hexdigest()==index['sha256'];f.seek(0)
 with zipfile.ZipFile(f) as z:
  assert set(z.namelist())==set(index['files'])
  for name,sha in index['files'].items():
   b=z.read(name);assert hashlib.sha256(b).hexdigest()==sha;(out/name).write_bytes(b)
print('PASS: supplied repair fixtures verified')
