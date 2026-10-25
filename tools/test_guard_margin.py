from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parents[1]
s=(r/'app/Source/EngineHost.c').read_text(encoding='utf8')
a=s.index(' static uint64_t spare=UINT64_MAX;');b=s.index(' if(engine<available){',a)
code=s[a:b]
p=Path(sys.argv[1]);p.write_text('#include <stdint.h>\n#include <stdlib.h>\n#include <stdatomic.h>\n#include <assert.h>\n#include "'+str(r/'app/Source/NativeMemoryBudget.h').replace('\\','/')+'"\nstatic _Atomic int engineLimited;\nstatic int classify(uint64_t engine,uint64_t available){\n'+code+'return atomic_load(&engineLimited); }\n'+"""
int main(void){
 uint64_t M=1ull<<20;
 assert(!classify(600*M,601*M));assert(!classify(600*M,700*M));
 assert(!classify(600*M,1112*M));assert(classify(600*M,1113*M));
 assert(!classify(700*M,600*M));
 assert(pg_streaming_resource_budget(1000*M,350*M,384*M,256*M)==-(int64_t)(34*M));
 assert(pg_streaming_resource_budget(1000*M,600*M,384*M,256*M)==0);
 assert(pg_streaming_resource_budget(1000*M,700*M,384*M,256*M)==60*M);
 for(unsigned freeMB=265;freeMB<=297;freeMB++){
  assert(pg_streaming_resource_budget(1000*M,freeMB*M,384*M,64*M)<0);
  assert(pg_streaming_resource_budget(1000*M,freeMB*M,256*M,64*M)==0);
 }
 assert(pg_streaming_resource_budget(1000*M,200*M,256*M,64*M)==-(int64_t)(56*M));
 return 0;}
""")
subprocess.run(['clang','-std=c11',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS production guard classification: near-equal limits no fast eviction; reserve/growth unchanged')

# Compile real reserve selection separately for fresh process limits (static cache is boot-only).
a=(r/'app/Source/EngineHost.c').read_text(encoding='utf8')
i=a.index('static uint64_t guardReserve(void){');j=a.index('static uint64_t guardBand',i)
q=p.with_name('reserve.c')
q.write_text('#include <stdint.h>\n#include <stdlib.h>\n#include <assert.h>\nstatic uint64_t processLimitMB;\n'+a[i:j]+"""
int main(int argc,char **argv){assert(argc==3);processLimitMB=strtoull(argv[1],0,10);assert(guardReserve()==(strtoull(argv[2],0,10)<<20));return 0;}
""")
subprocess.run(['clang','-std=c11',str(q),'-o',str(q.with_suffix(''))],check=True)
for limit,reserve in [(2098,256),(2348,256),(2560,256),(2561,384),(4096,384),(8192,384),(0,384)]:
 subprocess.run([str(q.with_suffix('')),str(limit),str(reserve)],check=True)
# Replay reported sustained headroom: no continuous eviction above the low-limit reserve.
# Both budgets still request eviction below their reserve and never grant growth inside the band.
print('PASS production reserve: 2098/2348 MiB limits retain 256 MiB; other devices unchanged')
