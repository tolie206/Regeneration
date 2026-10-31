import unittest,struct,zlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from optimize_ytd import optimize
from resource_codec import resource,segment

def fixture(extra=False):
 v=4096;physical=1048576;raw=bytearray(v+physical);struct.pack_into('<Q',raw,8,0x50000080);raw[0x88]=1;raw[0x89]=1
 struct.pack_into('<Q',raw,0x30,0x50000060);struct.pack_into('<H',raw,0x38,1);struct.pack_into('<Q',raw,0x60,0x50000100)
 struct.pack_into('<Q',raw,0x128,0x50000280);raw[0x280:0x282]=b'x\0'
 struct.pack_into('<4H',raw,0x150,1024,1024,1,512);raw[0x158:0x15c]=b'DXT1';raw[0x15d]=11;struct.pack_into('<Q',raw,0x170,0x60000000)
 at=v
 for i in range(11):
  n=max(1,(max(1,1024>>i)+3)//4)**2*8;raw[at:at+n]=bytes([i])*n;at+=n
 if extra:struct.pack_into('<Q',raw,0x300,0x60000010)
 co=zlib.compressobj(6,zlib.DEFLATED,-15)
 return struct.pack('<4sIII',b'RSC7',13,1<<24,(13<<28)|(1<<17)|7)+co.compress(raw)+co.flush()
class Tests(unittest.TestCase):
 def test_compact_physical_allocation_and_retain_exact_mips(self):
  source=fixture();out,stats=optimize(source,cap=512);self.assertEqual(stats['changed'],1)
  before,v,_,_=resource(source);after,ov,_,_=resource(out)
  self.assertEqual(v,ov);self.assertEqual(len(after)-v,262144);self.assertEqual(stats['physical_before'],1048576)
  self.assertEqual(struct.unpack_from('<HH',after,0x150),(512,512));self.assertEqual(after[0x15d],10);self.assertEqual(after[0x89],1)
  retained=sum(max(1,(max(1,512>>i)+3)//4)**2*8 for i in range(10))
  self.assertEqual(after[v:v+retained],before[v+524288:v+524288+retained])
  again,s=optimize(out,cap=512);self.assertEqual(again,out)
 def test_unknown_physical_reference_preserves_original(self):
  source=fixture(True);out,s=optimize(source,cap=512);self.assertEqual(out,source);self.assertIn('unknown physical',s['reason'])
 def test_no_unnecessary_rewrite(self):
  source=fixture();out,s=optimize(source,cap=1024);self.assertEqual(out,source)
if __name__=='__main__':unittest.main()
