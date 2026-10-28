// Deferred zero-initialized D3D CPU shadows. Reconstructed from the 1.5.1 call contract.
// Never discard initialized data, GPU memory, streaming assets, or world entities.
// Guest destructors own allocations and counters; unmaterialized shadows remain null.
static pthread_mutex_t pg_lazy_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_once_t pg_lazy_once = PTHREAD_ONCE_INIT;
static int pg_lazy_enabled;
static struct { uint64_t vtable, offset; } pg_lazy_types[4];
static uint64_t pg_lazy_deferred_bytes, pg_lazy_deferred_count, pg_lazy_materialized;
static void pg_lazy_init(void) {
 const char *v=getenv("PG_LAZY_CPU_COPIES");pg_lazy_enabled=!(v&&strcmp(v,"0")==0);
}
static bool pg_lazy_bounds(uint64_t size,uint64_t p,uint64_t n) { return p&&p<=size&&n<=size-p; }
static uint64_t pg_lazy_load(const uint8_t *data,uint64_t p) { uint64_t v;memcpy(&v,data+p,8);return v; }
static void pg_lazy_store(uint8_t *data,uint64_t p,uint64_t v) { memcpy(data+p,&v,8); }
int pg_lazy_cpu_create(w2c_game *instance,uint64_t resource,uint64_t bytes,uint64_t initial,unsigned kind) {
 pthread_once(&pg_lazy_once,pg_lazy_init);
 if(!pg_lazy_enabled||kind<1||kind>4||!bytes||bytes>(1ull<<30))return 0;
 const uint64_t offsets[]={120,128,144,136};uint64_t off=offsets[kind-1];
 uint8_t *data=instance->w2c_env_memory->data;uint64_t size=instance->w2c_env_memory->size;
 if(!pg_lazy_bounds(size,resource,off+16)||size<8324232)return 0;
 // Buffer initial descriptors with a null data pointer also represent zero initialization.
 if(initial&&(kind!=1||!pg_lazy_bounds(size,initial,8)||pg_lazy_load(data,initial)))return 0;
 uint64_t vt=pg_lazy_load(data,resource);
 if(!vt||pg_lazy_load(data,resource+off))return 0;
 pthread_mutex_lock(&pg_lazy_lock);
 // A vtable must always resolve to the same field layout, even after object address reuse.
 for(unsigned i=0;i<4;i++)if(pg_lazy_types[i].vtable==vt&&pg_lazy_types[i].offset!=off){pthread_mutex_unlock(&pg_lazy_lock);return 0;}
 unsigned k=kind-1;
 if(pg_lazy_types[k].vtable&&pg_lazy_types[k].vtable!=vt){pthread_mutex_unlock(&pg_lazy_lock);return 0;}
 pg_lazy_types[k].vtable=vt;pg_lazy_types[k].offset=off;
 pg_lazy_store(data,resource+off+8,bytes);
 pg_lazy_deferred_bytes+=bytes;pg_lazy_deferred_count++;
 pthread_mutex_unlock(&pg_lazy_lock);return 1;
}
void pg_lazy_cpu_need(w2c_game *instance,uint64_t resource) {
 pthread_once(&pg_lazy_once,pg_lazy_init);if(!pg_lazy_enabled)return;
 uint8_t *data=instance->w2c_env_memory->data;uint64_t size=instance->w2c_env_memory->size;
 if(!pg_lazy_bounds(size,resource,8))return;
 uint64_t vt=pg_lazy_load(data,resource),off=0;
 pthread_mutex_lock(&pg_lazy_lock);
 for(unsigned i=0;i<4;i++)if(pg_lazy_types[i].vtable==vt){off=pg_lazy_types[i].offset;break;}
 if(!off||!pg_lazy_bounds(size,resource,off+16)||size<8324232||pg_lazy_load(data,resource+off)){pthread_mutex_unlock(&pg_lazy_lock);return;}
 uint64_t bytes=pg_lazy_load(data,resource+off+8);
 if(!bytes||bytes>(1ull<<30)){pthread_mutex_unlock(&pg_lazy_lock);return;}
 uint64_t ptr=PG_FN_LAZY_CPU_CALLOC(instance,1,bytes);
 // calloc can grow linear memory; refresh both values before publishing its result.
 data=instance->w2c_env_memory->data;size=instance->w2c_env_memory->size;
 if(!pg_lazy_bounds(size,ptr,bytes)){
  pthread_mutex_unlock(&pg_lazy_lock);pg_log("Lazy D3D CPU allocation failed; stopping instead of using a null shadow");wasm_rt_trap(WASM_RT_TRAP_UNREACHABLE);return;
 }
 pg_lazy_store(data,resource+off,ptr);
 uint64_t held=pg_lazy_load(data,8324208)+bytes;
 pg_lazy_store(data,8324208,held);pg_lazy_store(data,8324216,pg_lazy_load(data,8324216)+1);
 if(held>pg_lazy_load(data,8324224))pg_lazy_store(data,8324224,held);
 pg_lazy_materialized++;pthread_mutex_unlock(&pg_lazy_lock);
}
static void pg_lazy_cpu_report(void) {
 pthread_once(&pg_lazy_once,pg_lazy_init);
 char line[220];pthread_mutex_lock(&pg_lazy_lock);
 snprintf(line,sizeof line,"Lazy D3D CPU copies: %s, deferred total %llu MiB in %llu resources, materialized %llu (totals, not current RAM saved)",pg_lazy_enabled?"on":"off",(unsigned long long)(pg_lazy_deferred_bytes>>20),(unsigned long long)pg_lazy_deferred_count,(unsigned long long)pg_lazy_materialized);
 pthread_mutex_unlock(&pg_lazy_lock);pg_log(line);
}
