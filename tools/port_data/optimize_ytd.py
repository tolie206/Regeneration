"""Reduce only verified legacy YTD mip chains and compact their physical segment.
No mesh geometry, names/hashes, scripts or collision are rewritten. Retains existing mip bytes.
Unsupported layouts return original data with a recorded reason, never a speculative rewrite.
"""
import struct,zlib,collections
from resource_codec import resource,segment

BLOCKS={b'DXT1':8,b'DXT3':16,b'DXT5':16,b'ATI1':8,b'ATI2':16}
COUNTERS=collections.Counter()
def u64(b,o):return struct.unpack_from('<Q',b,o)[0]
def pos(p,v,physical,n=1):
 region=p>>28;off=p&0xfffffff
 if region==5:at=off;end=v
 elif region==6:at=v+off;end=v+physical
 else:raise ValueError('pointer region')
 if off<0 or at>end or n>end-at:raise ValueError('pointer bounds')
 return at

def optimize(data,system=None,graphics=None,cap=512):
 raw,v,codec,ver=resource(data,system,graphics)
 if ver!=13:return data,dict(reason='not legacy YTD')
 if graphics is None:system,graphics=struct.unpack_from('<II',data,8)
 physical=len(raw)-v
 if not physical:return data,dict(reason='no physical segment')
 try:
  count=struct.unpack_from('<H',raw,0x38)[0]
  if count==0 or count>8192:raise ValueError('dictionary count')
  array=pos(u64(raw,0x30),v,physical,count*8)
  descriptors=[];known_fields=set();groups={};changed=0;old_pixels=0;new_pixels=0
  for i in range(count):
   t=pos(u64(raw,array+i*8),v,physical,0x90)
   if t>=v:raise ValueError('descriptor outside virtual')
   w,h,d,stride=struct.unpack_from('<4H',raw,t+0x50);fmt=raw[t+0x58:t+0x5c];mips=raw[t+0x5d]
   if fmt not in BLOCKS or d!=1 or not(0<w<=16384 and 0<h<=16384 and 1<=mips<=16):raise ValueError('unsupported texture kind')
   if w&(w-1) or h&(h-1):raise ValueError('non-power-of-two dimensions')
   block=BLOCKS[fmt];sizes=[max(1,(max(1,w>>j)+3)//4)*max(1,(max(1,h>>j)+3)//4)*block for j in range(mips)]
   pointer=u64(raw,t+0x70);p=pos(pointer,v,physical,sum(sizes))
   if p<v:raise ValueError('pixels not physical')
   # Recognize both layout stride conventions, preserve the original one.
   convention=0 if stride==max(1,w*block//16) else 1 if stride==max(1,(w+3)//4)*block else -1
   if convention<0:raise ValueError('unknown stride')
   drop=0
   while max(w>>drop,h>>drop)>cap and drop<mips-1 and min(w>>drop,h>>drop)>=8:drop+=1
   key=(pointer,w,h,mips,fmt)
   if pointer in groups and groups[pointer]['key']!=key:raise ValueError('aliased texture layout differs')
   if pointer not in groups:
    old_pixels+=sum(sizes);retained=raw[p+sum(sizes[:drop]):p+sum(sizes)]
    groups[pointer]=dict(key=key,pixels=retained,old_offset=p-v,old_length=sum(sizes),new_offset=0)
    new_pixels+=len(retained)
   descriptors.append((t,w,h,stride,block,mips,drop,pointer,convention));known_fields.add(t+0x70)
   changed+=drop>0
  if not changed:return data,dict(reason='already within cap')
  # A YTD is accepted only when ALL physical references are known texture data pointers.
  for at in range(0,v-7,8):
   value=u64(raw,at)
   if value>>28==6 and at not in known_fields:raise ValueError('unknown physical reference')
  spans=sorted((x['old_offset'],x['old_offset']+x['old_length']) for x in groups.values())
  if any(a[1]>b[0] for a,b in zip(spans,spans[1:])):raise ValueError('overlapping pixels')
  virtual=bytearray(raw[:v]);packed=bytearray()
  for item in groups.values():
   packed.extend(bytes((-len(packed))%16));item['new_offset']=len(packed);packed.extend(item['pixels'])
  # One ordinary resource page: avoids cross-page allocation/pointer relocation ambiguity.
  shift=0
  while (8192<<shift)<len(packed):shift+=1
  if shift>15:raise ValueError('page too large')
  flags=(graphics&0xf0000000)|(1<<17)|shift;allocated=segment(flags)
  if allocated>=physical:return data,dict(reason='no allocation reduction')
  packed.extend(bytes(allocated-len(packed)))
  for t,w,h,stride,block,mips,drop,pointer,convention in descriptors:
   nw=max(1,w>>drop);nh=max(1,h>>drop);ns=max(1,nw*block//16) if convention==0 else max(1,(nw+3)//4)*block
   struct.pack_into('<HH',virtual,t+0x50,nw,nh);struct.pack_into('<H',virtual,t+0x56,ns);virtual[t+0x5d]=mips-drop
   struct.pack_into('<Q',virtual,t+0x70,0x60000000+groups[pointer]['new_offset'])
  page=pos(u64(raw,8),v,physical,16)
  if page>=v or raw[page+9]==0:raise ValueError('pages info missing')
  virtual[page+9]=1 # graphics page count, system count/storage remains intact
  out=bytes(virtual)+bytes(packed);co=zlib.compressobj(6,zlib.DEFLATED,-15)
  result=struct.pack('<4sIII',b'RSC7',ver,system,flags)+co.compress(out)+co.flush()
  check,cv,cc,cver=resource(result,system,flags)
  if check!=out or cv!=v or cver!=ver:raise ValueError('roundtrip')
  # Independently verify every descriptor points to the exact retained original mip bytes.
  for t,w,h,stride,block,mips,drop,pointer,convention in descriptors:
   at=pos(u64(check,t+0x70),v,allocated,len(groups[pointer]['pixels']))
   if check[at:at+len(groups[pointer]['pixels'])]!=groups[pointer]['pixels']:raise ValueError('mip bytes changed')
  return result,dict(changed=changed,physical_before=physical,physical_after=allocated,pixel_before=old_pixels,pixel_after=new_pixels)
 except (ValueError,struct.error,IndexError) as ex:
  return data,dict(reason='preserved: '+str(ex))
