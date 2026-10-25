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
 return 0;}
""")
subprocess.run(['clang','-std=c11',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS production guard classification: near-equal limits no fast eviction; reserve/growth unchanged')
