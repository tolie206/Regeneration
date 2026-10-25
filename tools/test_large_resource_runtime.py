"""Exercise the production registry/walker with an actual VF8-sized entry."""
from pathlib import Path
import sys,subprocess,re,tempfile,shutil
root=Path(__file__).resolve().parents[1];p=Path(sys.argv[1])
s=(root/'app/Source/NativeLargeResources.inc').read_text()
fixture=(root/'tests/fixtures/resource32-pinned.c').read_text()
def body(text,n):
 a=text.index('u32 w2c_game_f'+str(n)+'(') if n==1898 else text.index('u64 w2c_game_f'+str(n)+'(')
 return text[a:text.index('\n}\n',a)+3]
with tempfile.TemporaryDirectory() as d:
 app=Path(d);(app/'Scripts').mkdir();(app/'Generated').mkdir()
 for name in ['engine_names.py','prepare_large_resources.py']:shutil.copyfile(root/'app/Scripts'/name,app/'Scripts'/name)
 shutil.copyfile(root/'tests/fixtures/resource32-funcnames.tsv',app/'Generated/funcnames.tsv')
 generated=app/'Generated/game_0.c';generated.write_text(fixture)
 subprocess.run([sys.executable,str(app/'Scripts/prepare_large_resources.py')],check=True,capture_output=True)
 patched=generated.read_text()
engine_bodies='\n'.join(body(fixture,n).replace('w2c_game_f'+str(n)+'(', 'w2c_game_f'+str(n)+'_old(') for n in [1898,1899])+'\n'+'\n'.join(body(patched,n) for n in [1898,1899])
p.write_text(r"""
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
typedef uint32_t u32;typedef uint64_t u64;typedef int64_t s64;typedef int32_t s32;typedef struct {void *w2c_env_memory;} w2c_game;
static _Alignas(16) unsigned char memory[8192];
#define FUNC_PROLOGUE
#define FUNC_EPILOGUE
static struct {int unused;} env;
static void *pg_pointer(void *e,uint64_t a,size_t n){(void)e;assert(a<=sizeof memory&&n<=sizeof memory-a);return memory+a;}
static const char *pg_string(void *e,uint64_t a){(void)e;assert(a<sizeof memory);return (const char*)memory+a;}
static void pg_log(const char *s){(void)s;}
static u64 checked_add_u64(u64 a,u64 b){return a+b;}
static u64 i64_load_shared(void *a,u64 b,void *c,u64 offset){(void)a;(void)b;(void)c;u64 v;memcpy(&v,pg_pointer(0,offset,8),8);return v;}
static u32 i32_load_shared(void *a,u64 b,void *c,u64 offset){(void)a;(void)b;(void)c;u32 v;memcpy(&v,pg_pointer(0,offset,4),4);return v;}
static u64 i64_load32_u_shared(void *a,u64 b,void *c,u64 offset){return i32_load_shared(a,b,c,offset);}
uint32_t pg_mods_large_resource_size(const char *archive,const char *name,uint32_t system,uint32_t graphics){
 return !strcmp(archive,"dlc_vf8:/vehicles.rpf")&&!strcmp(name,"vf8.yft")&&system==0xa01a1786u&&graphics==0x20000000u?17512137u:0;
}
"""+s+engine_bodies+r"""
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
 w2c_game instance={0};put64(4096+40,entry);
 assert(w2c_game_f1898_old(&instance,0,4096)==0xffffffu);
 assert(w2c_game_f1899_old(&instance,0,4096)==0xffffffu);
 assert(w2c_game_f1898(&instance,0,4096)==17512137u);
 assert(w2c_game_f1899(&instance,0,4096)==17512137u);
 assert(pg_large_rpf_size(0,entry,1234)==1234);
 put64(entry+8,0);assert(pg_large_rpf_size(0,entry,0xffffff)==0xffffff); // reused/mutated entry cannot inherit stale size
 return 0;
}
""")
subprocess.run(['clang','-std=c11','-pthread',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix(''))],check=True)
print('PASS production extended-resource registry: actual pinned Size/Size64 reproduce truncation then return full VF8 length, ordinary entry unchanged, fingerprint rejects stale pointer')
