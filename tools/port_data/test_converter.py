import unittest,sys,tempfile,struct,zlib,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import convert_data as c

def resource(code=b'EDX1',width=4,height=4,depth=1,mips=3):
 raw=bytearray(8192);t=256;raw[512:514]=b'x\0'
 struct.pack_into('<Q',raw,t+0x28,0x50000200)
 block=8 if code in (b'EDX1',b'EAT1') else 16
 struct.pack_into('<HHHH',raw,t+0x50,width,height,depth,max(1,width*block//16));raw[t+0x58:t+0x5c]=code;raw[t+0x5d]=mips
 struct.pack_into('<Q',raw,t+0x70,0x60000000)
 co=zlib.compressobj(6,zlib.DEFLATED,-15)
 return struct.pack('<4sIII',b'RSC7',13,1<<24,(13<<28)|(1<<24))+co.compress(raw)+co.flush()

def archive(path,files):
 names=b'\0';offsets=[]
 for name,data,flags in files:offsets.append(len(names));names+=name.encode()+b'\0'
 n=len(files)+1;table=bytearray(struct.pack('<4I',0x52504637,n,len(names),0x4e45504f)+bytes(n*16)+names)
 struct.pack_into('<4I',table,16,0,0x7fffff00,1,len(files))
 table.extend(bytes((-len(table))%512))
 for i,((name,data,flags),no) in enumerate(zip(files,offsets),1):
  off=len(table)//512;isresource=flags is not None
  v=no|((len(data) if isresource else 0)<<16)|(off<<40)|(isresource<<63)
  struct.pack_into('<QII',table,16+i*16,v,flags[0] if flags else len(data),flags[1] if flags else 0)
  table.extend(data);table.extend(bytes((-len(table))%512))
 path.write_bytes(table)

class Tests(unittest.TestCase):
 def test_real_formats_all_mips_and_resource_roundtrip(self):
  for tag,target in [(b'EDX1',b'DXT1'),(b'EDX3',b'DXT5'),(b'EDX5',b'DXT5'),(b'EAT1',b'ATI1'),(b'EAT2',b'ATI2')]:
   b=c.convert_resource(resource(tag));raw,v,codec,version=c.resource(b)
   self.assertEqual(raw[256+0x58:256+0x5c],target);self.assertEqual((len(raw),v,codec,version),(8192,4096,'deflate',13))
   self.assertEqual(c.convert_resource(b),b)
 def test_unsupported_volume_not_silently_accepted(self):
  with self.assertRaises(ValueError):c.convert_resource(resource(depth=2))
 def test_channel_order_and_eac_components(self):
  bgra=bytes([30,100,200,255]*16)
  for channels,encoder,decoder,expected in [(1,c.enc.compress_blocks_bc4,c.dec.decode_bc4,[0,0,200,255]),(2,c.enc.compress_blocks_bc5,c.dec.decode_bc5,[0,100,200,255])]:
   out=decoder(encoder(c.surface(bgra,4,4,channels)),4,4)
   self.assertEqual(list(out[:4]),expected)
  out=c.dec.decode_bc3(c.enc.compress_blocks_bc3(c.surface(bgra,4,4,4)),4,4)
  self.assertLess(max(abs(a-b) for a,b in zip(out[:4],bgra[:4])),6)
 def test_bad_resource_rejected(self):
  with self.assertRaises(ValueError):c.convert_resource(b'RSC7'+bytes(100))
 def test_nested_archive_rebuilt_without_entry_loss_or_source_write(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);b=resource();flags=struct.unpack_from('<II',b,8)
   archive(p/'child.rpf',[('t.ytd',b,flags),('a.bin',b'unchanged',None)])
   child=bytearray((p/'child.rpf').read_bytes());struct.pack_into('<I',child,12,0);(p/'child.rpf').write_bytes(child)
   archive(p/'input.rpf',[('nested.rpf',(p/'child.rpf').read_bytes(),None)])
   original=bytearray((p/'input.rpf').read_bytes());struct.pack_into('<I',original,12,0);(p/'input.rpf').write_bytes(original)
   before=hashlib.sha256((p/'input.rpf').read_bytes()).hexdigest();r=c.Rpf(p/'input.rpf')
   c.convert_rpf(r,p/'output.rpf');r.close()
   out=c.Rpf(p/'output.rpf');self.assertEqual(struct.unpack_from('<I',out.data,12)[0],0x4e45504f);nested=out.nested(out.entries[0]);self.assertEqual(struct.unpack_from('<I',nested.data,nested.base+12)[0],0x4e45504f);tex=next(x for x in nested.entries if x.path=='t.ytd')
   raw,*_=c.resource(nested.raw(tex),tex.system,tex.graphics)
   self.assertEqual(raw[256+0x58:256+0x5c],b'DXT1')
   self.assertEqual(nested.binary(next(x for x in nested.entries if x.path=='a.bin')),b'unchanged');out.close()
   self.assertEqual(hashlib.sha256((p/'input.rpf').read_bytes()).hexdigest(),before)
if __name__=='__main__':unittest.main()
