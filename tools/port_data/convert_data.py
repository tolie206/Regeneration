"""Offline port -> existing Mugoat formats; original data is always read-only.
This is a HYBRID dataset: retains Mugoat engine scripts/control metadata and
falls back to current files on unsupported input. Every fallback is recorded.
"""
from pathlib import Path
import sys,struct,zlib,json,os,hashlib,time,collections,argparse,shutil
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'deps'),str(ROOT)]
import texture2ddecoder as dec,ispc_texcomp as enc
from rpf_reader import Rpf
from resource_codec import resource
MAPPINGS={b'EDX1':(b'DXT1',8,dec.decode_etc2,enc.compress_blocks_bc1,4),b'EDX3':(b'DXT5',16,dec.decode_etc2a8,enc.compress_blocks_bc3,4),b'EDX5':(b'DXT5',16,dec.decode_etc2a8,enc.compress_blocks_bc3,4),b'EAT1':(b'ATI1',8,dec.decode_eacr,enc.compress_blocks_bc4,1),b'EAT2':(b'ATI2',16,dec.decode_eacrg,enc.compress_blocks_bc5,2)}
STATS=collections.Counter()
def pointer(raw,p,v,n):
 region=p>>28;offset=p&0xfffffff
 if region==5:at=offset;end=v
 elif region==6:at=v+offset;end=len(raw)
 else:raise ValueError('invalid texture pointer')
 if at>end or n>end-at:raise ValueError('texture out of bounds')
 return at

def surface(bgra,w,h,channels):
 from PIL import Image
 pw=max(4,(w+3)&~3);ph=max(4,(h+3)&~3)
 img=Image.frombytes('RGBA',(w,h),bgra,'raw','BGRA')
 if (pw,ph)!=(w,h):
  pad=Image.new('RGBA',(pw,ph));pad.paste(img,(0,0))
  if pw>w:pad.paste(img.crop((w-1,0,w,h)).resize((pw-w,h)),(w,0))
  if ph>h:pad.paste(pad.crop((0,h-1,pw,h)).resize((pw,ph-h)),(0,h))
  img=pad
 if channels==4:data=img.tobytes()
 elif channels==1:data=img.getchannel('R').tobytes()
 else:data=Image.merge('LA',(img.getchannel('R'),img.getchannel('G'))).tobytes()
 return enc.RGBASurface(data,pw,ph,pw*channels)

def convert_resource(data,system=None,graphics=None):
 raw,v,codec,ver=resource(data,system,graphics);out=bytearray(raw);converted=0;used=set()
 for code,(target,block,decode,encode,channels) in MAPPINGS.items():
  start=0
  while True:
   a=raw.find(code,start)
   if a<0:break
   start=a+4;t=a-0x58
   if t<0 or t+0x90>v:continue
   try:
    w,h,d,stride,fmt=struct.unpack_from('<HHHHI',raw,t+0x50);mips=raw[t+0x5d]
    if not(0<w<=16384 and 0<h<=16384 and d==1 and 0<mips<=16):continue
    # Validate both name and pixel pointers before accepting a FourCC match.
    name=pointer(raw,struct.unpack_from('<Q',raw,t+0x28)[0],v,1)
    if raw.find(b'\0',name,min(name+256,v))<0:continue
    sizes=[max(1,(max(1,w>>i)+3)//4)*max(1,(max(1,h>>i)+3)//4)*block for i in range(mips)]
    pix=pointer(raw,struct.unpack_from('<Q',raw,t+0x70)[0],v,sum(sizes))
    if pix<v:raise ValueError('texture not in physical segment')
    if stride not in {max(1,w*block//16),max(1,(w+3)//4)*block}:raise ValueError('nonstandard texture stride')
   except (ValueError,struct.error):continue
   key=(pix,tuple(sizes),code)
   if key not in used:
    at=pix
    for i,n in enumerate(sizes):
     mw=max(1,w>>i);mh=max(1,h>>i);bgra=decode(raw[at:at+n],mw,mh)
     if len(bgra)!=mw*mh*4:raise ValueError('decoder byte count')
     blocks=encode(surface(bgra,mw,mh,channels))
     if len(blocks)<n:raise ValueError('encoder byte count')
     out[at:at+n]=blocks[:n];at+=n
    used.add(key)
   out[a:a+4]=target;converted+=1;STATS[code.decode()]+=1
 # Fail closed on a valid texture descriptor that wasn't converted (e.g. volume/cubemap).
 # Any custom tag in the virtual segment is refused rather than knowingly shipped unsupported.
 for code in MAPPINGS:
  if code in out[:v]:raise ValueError('unconverted custom texture tag '+code.decode())
 if codec!='zstd' and not converted:return data
 co=zlib.compressobj(6,zlib.DEFLATED,-15);packed=co.compress(out)+co.flush()
 header=bytearray(data[:16])
 if system is not None:struct.pack_into('<II',header,8,system,graphics)
 result=bytes(header)+packed
 check,cv,cc,cver=resource(result,system,graphics)
 if check!=out or cv!=v or cver!=ver or cc!='deflate':raise ValueError('resource roundtrip')
 STATS['resources']+=1;STATS['textures']+=converted
 return result

def align(f):
 n=(-f.tell())%512
 if n:f.write(b'\0'*n)

def convert_rpf(r,target):
 # Preserve original table hierarchy and names. Only payload positions/sizes change.
 n,names=struct.unpack_from('<II',r.data,r.base+4);end=16+n*16+names
 table=bytearray(r.data[r.base:r.base+end])
 struct.pack_into('<I',table,12,0x4e45504f) # Engine rejects key 0; existing OpenIV path accepts OPEN.
 with open(target,'wb') as f:
  f.write(table);align(f)
  for e in r.entries:
   align(f);offset=f.tell();child=None
   try:
    if e.encrypted:raise ValueError('encrypted entry '+e.path)
    if e.resource:
     b=convert_resource(r.raw(e),e.system,e.graphics)
    elif e.path.endswith('.rpf'):
     child=target.with_name(target.name+'.child')
     convert_rpf(r.nested(e),child);b=None
    else:b=r.raw(e)
    size=child.stat().st_size if child else len(b)
    if e.resource and size>=0xffffff:raise ValueError('large resource needs extended size index')
    if not e.resource and e.compressed and child:raise ValueError('compressed nested archive')
    stored=size if e.resource or e.compressed else 0
    if stored>=0xffffff or offset//512>=(0x800000 if e.resource else 0x1000000):raise ValueError('RPF size exceeds table')
    original=struct.unpack_from('<4I',table,16+e.index*16)
    value=(original[0]&65535)|(stored<<16)|((offset//512)<<40)|(int(e.resource)<<63)
    struct.pack_into('<Q',table,16+e.index*16,value)
    if child:struct.pack_into('<I',table,16+e.index*16+8,size)
    if child:
     with child.open('rb') as inp:shutil.copyfileobj(inp,f,1024*1024)
    else:f.write(b)
   finally:
    if child:child.unlink(missing_ok=True)
  align(f);f.seek(0);f.write(table)
 # Parse output and check directory/payload extents again.
 check=Rpf(target)
 if len(check.entries)!=len(r.entries):raise ValueError('RPF entry loss')
 check.close();STATS['archives']+=1

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--source',required=True);ap.add_argument('--fallback',required=True);args=ap.parse_args()
 port=Path(args.source).resolve();old=Path(args.fallback).resolve();dest=Path(args.output).resolve()
 if dest==old or old in dest.parents or dest==port or port in dest.parents:raise ValueError('output overlaps source')
 if dest.exists() and any(dest.iterdir()):raise ValueError('output must be empty')
 dest.mkdir(parents=True,exist_ok=True);manifest=json.loads((old/'manifest.json').read_text());index=collections.defaultdict(list);opened=[]
 for p in [port/'common.rpf',*sorted(port.glob('x64?.rpf'))]:
  r=Rpf(p);opened.append(r)
  for e in r.entries:index[('common/' if p.name=='common.rpf' else 'x64/')+e.path].append((r,e))
 loose={p.relative_to(port).as_posix().lower():p for d in ('common','x64') for p in (port/d).rglob('*') if p.is_file()}
 records=[];files=[];start=time.time()
 try:
  for i,row in enumerate(manifest['files']):
   if args.limit and i>=args.limit:break
   name=row[0];key=name.lower();out=dest/name;out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.name+'.converting');entry=None
   source='mugoat';reason='no equivalent base asset; retain engine-compatible file'
   # Retain engine-specific control, mount, scripts, fonts and boot data.
   eligible=key.startswith('x64/') and '/script/' not in key and not key.startswith('x64/data/')
   try:
    if eligible and key in loose:
     p=loose[key];source='port-loose';reason=''
     if p.suffix.lower()=='.rpf':
      r=Rpf(p)
      try:convert_rpf(r,tmp)
      finally:r.close()
     elif p.read_bytes()[:4]==b'RSC7':tmp.write_bytes(convert_resource(p.read_bytes()))
     else:shutil.copyfile(p,tmp)
    elif eligible and len(index.get(key,[]))==1:
     r,e=index[key][0];source=r.path+'!'+e.path;reason=''
     if e.resource:tmp.write_bytes(convert_resource(r.raw(e),e.system,e.graphics))
     elif key.endswith('.rpf'):convert_rpf(r.nested(e),tmp)
     else:tmp.write_bytes(r.binary(e))
    else:shutil.copyfile(old/name,tmp)
   except Exception as ex:
    source='mugoat';reason='conversion refused: '+str(ex);tmp.unlink(missing_ok=True);shutil.copyfile(old/name,tmp)
   os.replace(tmp,out);size=out.stat().st_size;files.append([name,size,int(out.stat().st_mtime)])
   records.append(dict(path=name,source=source,reason=reason,size=size,sha256=sha(out)))
   if i%100==0 or not reason:print(json.dumps(dict(done=i+1,total=len(manifest['files']),path=name,source=source,reason=reason,seconds=round(time.time()-start),stats=STATS)),flush=True)
  report=dict(status='OFFLINE_CANDIDATE_NOT_DEVICE_TESTED',hybrid=True,stats=STATS,records=records,complete=len(files)==len(manifest['files']))
  (dest.parent/(dest.name+'-report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
  manifest['files']=files;manifest['version']='port-converted-v1';(dest/'manifest.json').write_text(json.dumps(manifest,separators=(',',':')),encoding='utf8')
  print(json.dumps(dict(complete=report['complete'],stats=STATS,port_files=sum(x['source']!='mugoat' for x in records),files=len(files)),ensure_ascii=False),flush=True)
 finally:
  for r in opened:r.close()
if __name__=='__main__':main()
