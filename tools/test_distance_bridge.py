from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parents[1]
s=(r/'app/Source/EngineHost.c').read_text(encoding='utf8')
a=s.index('uint64_t pg_streaming_available_memory(');b=s.index('\n}\n',a)+3
samples=__import__('json').loads((r/'tests/fixtures/r007_headroom_samples.json').read_text())['samples_mib']
p=Path(sys.argv[1]);p.write_text('#include <stdint.h>\n#include <stdbool.h>\n#include <assert.h>\n#include "'+str(r/'app/Source/NativeMemoryBudget.h').replace('\\','/')+'"\n#include "'+str(r/'app/Source/NativeDistanceStreaming.h').replace('\\','/')+'"\n'+"""
static uint64_t available;static bool mode=true;
static const unsigned samples[]={"""+",".join(map(str,samples))+"""};
static PGDistanceStreaming distanceStreaming;
static bool nativeProcessHeadroom(uint64_t *p){*p=available;return true;}
static bool pg_distance_streaming_enabled(void){return mode;}
static uint64_t guardReserve(void){return 256ull<<20;}
static uint64_t guardBand(void){return 256ull<<20;}
static int64_t weaponGrant(int64_t n){return n<(64ll<<20)?(64ll<<20):n;}
"""+s[a:b]+"""
int main(void){uint64_t M=1ull<<20;
 available=M;assert(pg_streaming_available_memory(1024*M)==M);
 available=0;assert(pg_streaming_available_memory(1024*M)==0);
 available=270*M;assert(pg_streaming_available_memory(1024*M)==270*M);
 available=600*M;assert(pg_streaming_available_memory(4*M)==4*M);
 distanceStreaming.reserveBytes=128*M;
 available=270*M;assert(pg_streaming_available_memory(1024*M)==142*M);
 available=12*M;assert(pg_streaming_available_memory(1024*M)==0);
 available=200*M;assert(pg_streaming_available_memory(1024*M)==72*M);
 available=400*M;assert(pg_streaming_available_memory(4*M)==4*M);
 for(unsigned i=0;i<sizeof samples/sizeof samples[0];i++){
  available=(uint64_t)samples[i]*M;
  uint64_t expected=available>128*M?available-128*M:0;
  assert(pg_streaming_available_memory(1024*M)==expected);
 }
 return 0;}
""")
subprocess.run(['clang','-std=c11',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS actual host bridge: R006 opt-out, R007 reserve without legacy band, native ceiling, no weapon grant past OS headroom')
