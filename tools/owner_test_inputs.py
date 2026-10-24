"""Package/verify owner-supplied archives for tests in this private repository."""
import argparse, hashlib, json, tempfile, zipfile, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def pack(source, target):
    samples={
        'cars/laferrari.rar':next((source/'mod xe').glob('*.rar')),
        'cars/sh150.zip':next((source/'mod xe').glob('*sh150*')),
        'cars/vision.zip':next((source/'mod xe').glob('*vision*')),
        'sound/engines.zip':next((source/'mod sound').glob('*')),
        'skins/nier.rar':next((source/'mod skin add on').glob('*')),
        'menyoo/menyoo.zip':next((source/'mod menyoo').glob('*')),
    }
    target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryFile(dir=target.parent) as f:
        with zipfile.ZipFile(f,'w',zipfile.ZIP_STORED,allowZip64=True) as z:
            for name,path in samples.items(): z.write(path,name)
        f.seek(0); digest=hashlib.sha256();parts=[];total=0
        while b:=f.read(16*1024*1024):
            name=f'owner-{len(parts):04d}.part';(target/name).write_bytes(b)
            parts.append(name);digest.update(b);total+=len(b)
    meta={'bytes':total,'sha256':digest.hexdigest(),'parts':parts,
          'samples':{n:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in samples.items()}}
    (target/'index.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')
    print('Packaged',len(samples),'original archives;',total,'bytes;',len(parts),'verified parts')

def assemble(source, target):
    meta=json.loads((source/'index.json').read_text(encoding='utf8'))
    assert 0<meta['bytes']<1024**3 and len(meta['parts'])<=64
    target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryFile(dir=target.parent) as f:
        digest=hashlib.sha256();total=0
        for i,name in enumerate(meta['parts']):
            assert name==f'owner-{i:04d}.part'
            b=(source/name).read_bytes();assert len(b)<=16*1024*1024
            f.write(b);digest.update(b);total+=len(b)
        assert total==meta['bytes'] and digest.hexdigest()==meta['sha256']
        f.seek(0)
        with zipfile.ZipFile(f) as z:
            assert set(z.namelist())==set(meta['samples'])
            for name,info in meta['samples'].items():
                assert re.fullmatch(r'(cars|sound|skins|menyoo)/[a-z0-9.]+',name)
                b=z.read(name);assert len(b)==info['bytes'] and hashlib.sha256(b).hexdigest()==info['sha256']
                p=target/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    print('Verified all original owner-supplied archives')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['pack','assemble']);p.add_argument('source',type=Path);p.add_argument('target',type=Path)
    a=p.parse_args();globals()[a.mode](a.source.resolve(),a.target.resolve())
