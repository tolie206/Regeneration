"""Read resource/texture metadata only. Does not reinterpret custom EDX pixels as DXT."""
import struct,zlib
try:
 from compression import zstd
except ImportError:
 import zstandard
 class zstd:
  @staticmethod
  def decompress(data):return zstandard.ZstdDecompressor().decompress(data,max_output_size=256*1024*1024)

def segment(flags):
 return sum(((flags>>bit)&mask)*weight for bit,mask,weight in [(27,1,1),(26,1,2),(25,1,4),(24,1,8),(17,127,16),(11,63,32),(7,15,64),(5,3,128),(4,1,256)])*(512<<(flags&15))
def resource(b,system=None,graphics=None):
 if b[:4]!=b'RSC7':raise ValueError('resource header')
 magic,ver,sys,gfx=struct.unpack_from('<4I',b)
 if system is not None:sys,gfx=system,graphics
 expected=segment(sys)+segment(gfx)
 if not 0<expected<=256*1024*1024:raise ValueError('resource size')
 packed=b[16:];codec='zstd' if packed[:4]==b'\x28\xb5\x2f\xfd' else 'deflate'
 if codec=='zstd':raw=zstd.decompress(packed)
 else:
  try:raw=zlib.decompress(packed,-15)
  except zlib.error:raw=zlib.decompress(packed)
 if len(raw)!=expected:raise ValueError('resource size mismatch')
 return raw,segment(sys),codec,ver
