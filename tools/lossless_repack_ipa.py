"""Lossless standard ZIP repack: never strip/edit a single application file."""
from pathlib import Path,PurePosixPath
import argparse,copy,hashlib,json,plistlib,shutil,zipfile
OIV_SHA='bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c'
def digest(z,entry):
 h=hashlib.sha256()
 with z.open(entry) as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def manifest(z):
 entries=z.infolist();names=[e.filename for e in entries]
 if len(entries)>20000 or len(set(names))!=len(names) or sum(e.file_size for e in entries)>2*1024**3:raise ValueError('Invalid archive size/duplicates')
 out={}
 for e in entries:
  path=PurePosixPath(e.filename)
  if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='Payload' or e.flag_bits&1:raise ValueError('Unexpected IPA entry')
  if e.compress_type not in [zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED]:raise ValueError('Unsupported IPA compression')
  out[e.filename]=(e.file_size,e.external_attr,e.create_system,digest(z,e))
 return out

def repack(source,target,verify_release=False):
 source=Path(source).resolve();target=Path(target).resolve()
 if source==target or target.exists():raise ValueError('Refusing to overwrite input/existing output')
 with zipfile.ZipFile(source) as original:
  before=manifest(original)
  if verify_release:
   info=[n for n in before if n.endswith('.app/Info.plist')];assert len(info)==1
   metadata=plistlib.loads(original.read(info[0]));assert metadata['CFBundleVersion']=='5009' and metadata['CFBundleIdentifier']=='vn.gta.newgen'
   oiv=[n for n in before if n.endswith('/Mugoat-PortLike-Traffic-v1.oiv')];assert len(oiv)==1 and before[oiv[0]][3]==OIV_SHA
  target.parent.mkdir(parents=True,exist_ok=True)
  try:
   with zipfile.ZipFile(target,'x',allowZip64=True) as output:
    output.comment=original.comment
    for entry in original.infolist():
     new=copy.copy(entry)
     output.writestr(new,original.read(entry),compress_type=entry.compress_type,compresslevel=9)
   with zipfile.ZipFile(target) as result:
    assert manifest(result)==before,'Application bytes/permissions changed'
    assert result.testzip() is None
   if target.stat().st_size>=source.stat().st_size:shutil.copyfile(source,target)
  except Exception:
   target.unlink(missing_ok=True);raise
 installed=sum(v[0] for v in before.values())
 return {'input_bytes':source.stat().st_size,'output_bytes':target.stat().st_size,'saved_bytes':source.stat().st_size-target.stat().st_size,'installed_bytes_before':installed,'installed_bytes_after':installed,'all_application_bytes_and_permissions_identical':True,'runtime_RAM_or_FPS_change':False,'note':'ZIP only. Original executable, shaders, assets, signature and entitlements are unchanged.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('target',type=Path);p.add_argument('--report',type=Path);p.add_argument('--verify-release',action='store_true');a=p.parse_args()
 report=repack(a.source,a.target,a.verify_release)
 if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
