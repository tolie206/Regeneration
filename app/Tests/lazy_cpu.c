#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <assert.h>
#include <setjmp.h>
typedef struct { uint8_t *data;uint64_t size; } Memory;
typedef struct { Memory *w2c_env_memory; } w2c_game;
static uint64_t next_address=10000000,allocations;
static int fail_alloc;static jmp_buf trapped;
static uint64_t fake_calloc(w2c_game *g,uint64_t n,uint64_t bytes){
 assert(n==1);allocations++;if(fail_alloc)return 0;
 uint64_t p=next_address;next_address+=bytes;assert(next_address<=g->w2c_env_memory->size);memset(g->w2c_env_memory->data+p,0,(size_t)bytes);return p;
}
#define PG_FN_LAZY_CPU_CALLOC fake_calloc
#define WASM_RT_TRAP_UNREACHABLE 1
static void wasm_rt_trap(int n){assert(n==1);longjmp(trapped,1);}
static void pg_log(const char *s){(void)s;}
#include "../Source/NativeLazyCPU.inc"
static w2c_game game;
static void *need_thread(void *p){pg_lazy_cpu_need(&game,(uint64_t)(uintptr_t)p);return NULL;}
int main(int argc,char **argv){
 (void)argv;Memory memory={calloc(1,32<<20),32<<20};assert(memory.data);game.w2c_env_memory=&memory;
 uint8_t *data=memory.data;
 if(argc>1){setenv("PG_LAZY_CPU_COPIES","0",1);pg_lazy_store(data,1024,500);assert(!pg_lazy_cpu_create(&game,1024,4096,0,1));pg_lazy_cpu_need(&game,1024);assert(!allocations);pg_lazy_cpu_report();free(data);return 0;}
 const uint64_t offsets[]={120,128,144,136};
 for(unsigned k=1;k<=4;k++){
  uint64_t r=k*1024,off=offsets[k-1];pg_lazy_store(data,r,500+k);
  assert(pg_lazy_cpu_create(&game,r,4096*k,0,k));assert(!allocations);assert(!pg_lazy_load(data,r+off));assert(pg_lazy_load(data,r+off+8)==4096*k);
 }
 assert(!pg_lazy_load(data,8324208));
 assert(!pg_lazy_cpu_create(&game,0,4096,0,1));assert(!pg_lazy_cpu_create(&game,1024,0,0,1));
 assert(!pg_lazy_cpu_create(&game,1024,1ull<<32,0,1));assert(!pg_lazy_cpu_create(&game,1024,4096,0,5));
 assert(!pg_lazy_cpu_create(&game,memory.size-2,4096,0,1));
 // Preserve all initialized texture payloads, even descriptors whose first pointer is null.
 for(unsigned k=2;k<=4;k++)assert(!pg_lazy_cpu_create(&game,k*1024,1000,16000,k));
 pg_lazy_store(data,16000,18000);assert(!pg_lazy_cpu_create(&game,1024,1000,16000,1));
 pg_lazy_store(data,16000,0);assert(pg_lazy_cpu_create(&game,1024,4096,16000,1));
 // Unknown resource interfaces, invalid ranges and reused addresses cannot allocate wrong layouts.
 pg_lazy_store(data,20000,900);pg_lazy_cpu_need(&game,20000);pg_lazy_cpu_need(&game,0);pg_lazy_cpu_need(&game,UINT64_MAX);assert(!allocations);
 pg_lazy_store(data,21000,503);assert(!pg_lazy_cpu_create(&game,21000,4096,0,1));
 // Concurrent access must materialize a deferred buffer exactly once.
 pthread_t threads[8];for(unsigned i=0;i<8;i++)assert(!pthread_create(threads+i,NULL,need_thread,(void*)(uintptr_t)1024));
 for(unsigned i=0;i<8;i++)pthread_join(threads[i],NULL);
 assert(allocations==1);assert(pg_lazy_load(data,8324208)==4096);assert(pg_lazy_load(data,8324216)==1);
 uint64_t ptr=pg_lazy_load(data,1144);assert(ptr);for(unsigned i=0;i<4096;i++)assert(!data[ptr+i]);
 data[ptr]=123;pg_lazy_cpu_need(&game,1024);assert(data[ptr]==123&&allocations==1);
 for(unsigned k=2;k<=4;k++)pg_lazy_cpu_need(&game,k*1024);
 assert(allocations==4);assert(pg_lazy_load(data,8324208)==40960);assert(pg_lazy_load(data,8324216)==4);assert(pg_lazy_load(data,8324224)==40960);
 // Repeated maps/copies do not allocate again or change data/counters.
 for(unsigned i=0;i<100000;i++)pg_lazy_cpu_need(&game,3072);
 assert(allocations==4);
 // Destructor-equivalent ownership: unmaterialized objects own no CPU allocation or counter.
 pg_lazy_store(data,25000,501);assert(pg_lazy_cpu_create(&game,25000,4096,0,1));assert(!pg_lazy_load(data,25120));assert(pg_lazy_load(data,8324216)==4);
 // Allocation failure must trap, never publish a null pointer or inflate counters.
 fail_alloc=1;if(!setjmp(trapped)){pg_lazy_cpu_need(&game,25000);assert(0);}
 assert(!pg_lazy_load(data,25120));assert(pg_lazy_load(data,8324216)==4);
 fail_alloc=0;pg_lazy_cpu_need(&game,25000);assert(pg_lazy_load(data,25120));
 pg_lazy_cpu_report();free(data);puts("PASS lazy CPU shadows: initialization, four layouts, reuse, concurrency, counters, OOM");return 0;
}
