"""Independent original/optimized comparison, including exact unchanged mesh/collision/script bytes."""
from pathlib import Path
import struct,json,sys,collections
from resource_codec import resource
from rpf_reader import Rpf
STATS=collections.Counter();BLOCKS={b'DXT1':8,b'DXT3':16,b'DXT5':16,b'ATI1':8,b'ATI2':16}
def u64(b,o):return struct.unpack_from('<Q',b,o)[0]
def ytd(before,after,osys,ogfx,nsys,ngfx):
 a,v,_,ver=resource(before,osys,ogfx);b,nv,_,nver=resource(after,nsys,ngfx)
 assert (v,ver)==(nv,nver) and ver==13 and osys==nsys
 assert struct.unpack_from('<II',after,8)==(nsys,ngfx)
 count=struct.unpack_from('<H',a,0x38)[0];assert struct.unpack_from('<H',b,0x38)[0]==count
 pointer=u64(a,0x30);assert pointer==u64(b,0x30) and pointer>>28==5
 array=pointer&0xfffffff;av=bytearray(a[:v]);bv=bytearray(b[:v]);changed=0
 for i in range(count):
  ptr=u64(a,array+i*8);assert ptr==u64(b,array+i*8) and ptr>>28==5;t=ptr&0xfffffff
  w,h,d,stride=struct.unpack_from('<4H',a,t+0x50);nw,nh,nd,ns=struct.unpack_from('<4H',b,t+0x50)
  fmt=a[t+0x58:t+0x5c];assert fmt==b[t+0x58:t+0x5c] and fmt in BLOCKS and d==nd==1
  m=a[t+0x5d];nm=b[t+0x5d];drop=m-nm;assert 0<=drop<m and nw==max(1,w>>drop) and nh==max(1,h>>drop)
  sizes=[max(1,(max(1,w>>j)+3)//4)*max(1,(max(1,h>>j)+3)//4)*BLOCKS[fmt] for j in range(m)]
  ap=u64(a,t+0x70);bp=u64(b,t+0x70);assert ap>>28==bp>>28==6
  aa=v+(ap&0xfffffff)+sum(sizes[:drop]);bb=v+(bp&0xfffffff);n=sum(sizes[drop:]);assert aa+n<=len(a) and bb+n<=len(b)
  assert a[aa:aa+n]==b[bb:bb+n], 'retained mip content changed'
  changed+=drop>0
  for off,nbytes in [(t+0x50,4),(t+0x56,2),(t+0x5d,1),(t+0x70,8)]:av[off:off+nbytes]=bytes(nbytes);bv[off:off+nbytes]=bytes(nbytes)
 page=u64(a,8);assert page==u64(b,8) and page>>28==5;page&=0xfffffff
 assert b[page+9]==1 and b[page+8]==a[page+8];av[page+9]=bv[page+9]=0
 assert av==bv, 'virtual metadata beyond mip/pointer/page fields changed'
 assert len(b)<len(a)
 STATS['changed_dictionaries']+=1;STATS['reduced_textures']+=changed;STATS['physical_bytes_removed']+=len(a)-len(b)
def compare(a,b):
 assert [(x.path,x.resource) for x in a.entries]==[(x.path,x.resource) for x in b.entries]
 for ea,eb in zip(a.entries,b.entries):
  if not ea.resource and ea.path.endswith('.rpf'):compare(a.nested(ea),b.nested(eb));continue
  before=a.raw(ea);after=b.raw(eb)
  if before==after:
   assert ea.system==eb.system and ea.graphics==eb.graphics
   STATS['unchanged_entries']+=1;continue
  assert ea.resource and ea.path.endswith('.ytd'), 'non-texture payload changed: '+ea.path
  ytd(before,after,ea.system,ea.graphics,eb.system,eb.graphics)
 STATS['archives_compared']+=1

def main():
 old=Path(sys.argv[1]);new=Path(sys.argv[2]);report=json.loads((new.parent/(new.name+'-report.json')).read_text())
 for name in report['changed_files']:
  a=old/name;b=new/name
  if name.endswith('.rpf'):
   ra=Rpf(a);rb=Rpf(b)
   try:compare(ra,rb)
   finally:ra.close();rb.close()
  else:
   assert name.endswith('.ytd');ba=a.read_bytes();bb=b.read_bytes();os,og=struct.unpack_from('<II',ba,8);ns,ng=struct.unpack_from('<II',bb,8);ytd(ba,bb,os,og,ns,ng)
 result=dict(status='PASS_MIP_BYTES_AND_NON_TEXTURE_PAYLOAD_PRESERVED',stats=STATS)
 (new.parent/'CONTENT-COMPARISON.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
