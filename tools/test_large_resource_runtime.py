"""Exercise the production registry/walker with an actual VF8-sized entry."""
from pathlib import Path
import sys,subprocess
root=Path(__file__).resolve().parents[1];p=Path(sys.argv[1])
s=(root/'app/Source/NativeLargeResources.inc').read_text()
p.write_text(r"""
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
typedef uint32_t u32;typedef uint64_t u64;typedef struct {int unused;} w2c_game;
static unsigned char memory[8192];
static struct {int unused;} env;
static void *pg_pointer(void *e,uint64_t a,size_t n){(void)e;assert(a<=sizeof memory&&n<=sizeof memory-a);return memory+a;}
static const char *pg_string(void *e,uint64_t a){(void)e;assert(a<sizeof memory);return (const char*)memory+a;}
static void pg_log(const char *s){(void)s;}
uint32_t pg_mods_large_resource_size(const char *archive,const char *name,uint32_t system,uint32_t graphics){
 return !strcmp(archive,"dlc_vf8:/vehicles.rpf")&&!strcmp(name,"vf8.yft")&&system==0xa01a1786u&&graphics==0x20000000u?17512137u:0;
}
"""+s+r"""
static void put64(size_t at,uint64_t value){memcpy(memory+at,&value,8);}
int main(void){
 const uint64_t entry=1024+16,lo=(1ull<<63)|(2ull<<40)|(0xffffffull<<16)|1;
 put64(128+32,1024);put64(128+16,2048);
 put64(1024,0x7fffff00ull<<32);put64(1032,(1ull<<32)|1);
 memory[2048]=0;strcpy((char*)memory+2049,"vf8.yft");
 put64(entry,lo);put64(entry+8,0x20000000a01a1786ull);
 assert(pg_large_rpf_size(0,entry,0xffffff)==0xffffff);
 pg_large_archive_mounted(128,"dlc_vf8:/vehicles.rpf");
 assert(pg_large_rpf_size(0,entry,0xffffff)==17512137u);
 assert(pg_large_rpf_size(0,entry,1234)==1234);
 put64(entry+8,0);assert(pg_large_rpf_size(0,entry,0xffffff)==0xffffff); // reused/mutated entry cannot inherit stale size
 return 0;
}
""")
subprocess.run(['clang','-std=c11','-pthread',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS production extended-resource registry: VF8 length, ordinary entry unchanged, fingerprint rejects stale pointer')
