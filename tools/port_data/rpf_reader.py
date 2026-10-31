"""Read-only OPEN/plain RPF7; local SoundArchive.swift entry layout."""
from pathlib import Path
from dataclasses import dataclass
import mmap,struct,zlib
@dataclass
class Entry:
 index:int;path:str;offset:int;size:int;unpacked:int;encrypted:bool;compressed:bool;resource:bool;system:int;graphics:int
class Rpf:
 def __init__(self,path,data=None,base=0,size=None,owner=None):
  self.path=str(path);self.base=base;self.file=None;self.owner=owner
  if data is None:self.file=open(path,'rb');self.data=mmap.mmap(self.file.fileno(),0,access=mmap.ACCESS_READ)
  else:self.data=data
  self.size=len(self.data)-base if size is None else size
  if self.size<16:raise ValueError('short RPF')
  magic,count,names,enc=struct.unpack_from('<4I',self.data,base)
  if magic!=0x52504637 or enc not in (0,0x4e45504f):raise ValueError('not OPEN/plain RPF7')
  start=16+count*16
  if not(0<count<2000000 and 0<names<=32*1024*1024 and start+names<=self.size):raise ValueError('invalid table')
  table=self.data[base+16:base+start];strings=self.data[base+start:base+start+names];visited=set();out=[]
  def walk(i,parent,depth):
   if depth>=32 or i in visited or not 0<=i<count:raise ValueError('invalid directory graph')
   visited.add(i);first,second,a,b=struct.unpack_from('<4I',table,i*16);directory=second==0x7fffff00;at=first if directory else first&65535
   if at>=len(strings):raise ValueError('invalid name')
   end=strings.find(b'\0',at)
   if end<0:raise ValueError('unterminated name')
   name=strings[at:end].decode('utf8').lower()
   if '/' in name or '\\' in name or name in ('.','..'):raise ValueError('unsafe name')
   path='/'.join(x for x in (parent,name) if x)
   if directory:
    if a>count or b>count-a:raise ValueError('directory bounds')
    for j in range(a,a+b):walk(j,path,depth+1)
   else:
    resource=bool(second&0x80000000);packed=first|(second<<32);length=(packed>>16)&0xffffff;compressed=length!=0;offset=((packed>>40)&(0x7fffff if resource else 0xffffff))*512
    if resource and length==0xffffff:
     h=self.data[base+offset:base+offset+16];length=h[7]|h[14]<<8|h[5]<<16|h[2]<<24
    if not resource and length==0:length=a
    if offset<start+names or offset>self.size or length>self.size-offset:raise ValueError('entry bounds')
    out.append(Entry(i,path,offset,length,a,not resource and b!=0,compressed,resource,a,b))
  walk(0,'',0)
  if len(visited)!=count or len({e.path for e in out})!=len(out):raise ValueError('orphan or duplicate')
  self.entries=out
 def raw(self,e):return self.data[self.base+e.offset:self.base+e.offset+e.size]
 def binary(self,e):
  if e.resource or e.encrypted or e.unpacked>64*1024*1024:raise ValueError('unsupported binary')
  b=self.raw(e)
  if e.compressed:
   d=zlib.decompressobj(-15);r=d.decompress(b,e.unpacked+1)
   if len(r)!=e.unpacked or not d.eof or d.unconsumed_tail:raise ValueError('inflate mismatch')
   return r
  return b
 def nested(self,e):
  if e.resource or e.encrypted or e.compressed:raise ValueError('nested RPF encrypted/compressed')
  return Rpf(self.path+'!'+e.path,self.data,self.base+e.offset,e.size,self)
 def close(self):
  if self.file:self.data.close();self.file.close()
