"""Compile the production scene-active predicate with simulated host memory."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
s=(root/'app/Source/NativeCheats.inc').read_text()
a=s.index('bool PGLoadSceneActive(void) {');b=s.index('\n}\n',a)+3
p=Path(sys.argv[1])
p.write_text('#include <assert.h>\n#include <stdint.h>\n#include <stdbool.h>\n#include <stdatomic.h>\n#include <stdlib.h>\nstruct { struct { uint64_t size; void *data; } memory; } env;\nstatic _Atomic double loadSceneSince;\n'+s[a:b]+"""
int main(void){
 assert(!PGLoadSceneActive());
 atomic_store(&loadSceneSince,1);assert(PGLoadSceneActive()); // first millisecond, duration UI still zero
 env.memory.size=23418000;env.memory.data=calloc(1,env.memory.size);assert(env.memory.data);
 atomic_store(&loadSceneSince,0);((uint8_t*)env.memory.data)[23389293]=1;
 assert(PGLoadSceneActive()); // real active state remains even after duration watchdog expiry
 ((uint8_t*)env.memory.data)[23389293]=0;assert(!PGLoadSceneActive());
 free(env.memory.data);return 0;
}
""")
subprocess.run(['clang','-std=c11',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS actual transition predicate: first second, real active flag after duration expiry, release')
