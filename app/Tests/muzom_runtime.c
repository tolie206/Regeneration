#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <time.h>
#include "../Source/NativeDistanceStreaming.h"

// Hash declarations are included again by the production include, so remove its unguarded array here.

typedef uint32_t u32;typedef uint64_t u64;typedef struct{int unused;}w2c_game;
static _Atomic bool started;static uint64_t processLimitMB=2348,room=1024ull<<20;
static PGDistanceStreaming distanceStreaming={.reserveBytes=128ull<<20};
static struct{int unused;}env;static unsigned char memory[4096];
static bool paused,scene,allSupported=true,navOK=true,modelsLoaded=true,validModel=true,failCreate,wrongModel,allocationOK=true;
static u32 gameStatus,owner=42,player=1;static double clockMS=1000;static unsigned nextEntity=2,nativeCalls,requests,releases,attacks,deletions;
typedef struct{bool exists,owned,dead,occupied,unarmed,frozen;u32 model;unsigned kind;float p[3];}Entity;
static Entity entities[4096];
static bool PGPauseMenuActive(void){return paused;}static u32 PGGameStatus(void){return gameStatus;}static bool PGLoadSceneActive(void){return scene;}
static double timeMS(clockid_t clock){(void)clock;return clockMS;}
static bool mz_native_available(uint64_t h){(void)h;return allSupported;}
static u64 pg_asi_enter_script(w2c_game *p){(void)p;return 0;}static void pg_asi_leave_script(w2c_game*p,u64 n){(void)p;(void)n;}
static u64 pg_asi_alloc(u64 n){(void)n;return allocationOK?256:0;}
static void *pg_pointer(void*p,u64 at,u64 n){(void)p;assert(at+n<=sizeof memory);return memory+at;}
static void pg_log(const char*s){(void)s;}
static u32 PG_FN_PLAYER_PED_ID(w2c_game*p){(void)p;return player;}static u32 PG_FN_PLAYER_ID(w2c_game*p){(void)p;return 0;}
static void PG_FN_SET_MAX_WANTED(w2c_game*p,u32 v){(void)p;assert(v==0);}
static u64 PG_FN_CURRENT_SCRIPT_HANDLER(w2c_game*p){(void)p;return owner;}
static bool nativeProcessHeadroom(uint64_t*out){*out=room;return true;}
static u32 PG_FN_ENTITY_EXISTS(w2c_game*p,u32 e){(void)p;return e<4096&&entities[e].exists;}
static u32 PG_FN_GET_ENTITY_MODEL(w2c_game*p,u32 e){(void)p;return e<4096?entities[e].model:0;}
static u32 PG_FN_ENTITY_OWNED(w2c_game*p,u32 e,u32 b){(void)p;(void)b;return e<4096&&entities[e].owned;}
static u32 PG_FN_VEHICLE_OCCUPANT(w2c_game*p,u32 e,u32 seat,u32 b){(void)p;(void)seat;(void)b;return entities[e].occupied?player:0;}
static u32 PG_FN_SPAWN_ENTITY_VISIBLE(w2c_game*p,u32 e){(void)p;return entities[e].exists;}
static void PG_FN_GET_ENTITY_COORDS(w2c_game*p,u64 at,u32 e,u32 b){(void)p;(void)b;assert(e<4096);float*v=pg_pointer(&env,at,24);memset(v,0,24);v[0]=entities[e].p[0];v[2]=entities[e].p[1];v[4]=entities[e].p[2];}
static unsigned model_kind(u32 model);
static u32 PG_FN_IS_VEHICLE_MODEL(w2c_game*p,u32 m){(void)p;return model_kind(m)==2;}
static u32 PG_FN_VEHICLE_CLASS(w2c_game*p,u32 m){(void)p;(void)m;return 0;}
static void PG_FN_REQUEST_MODEL(w2c_game*p,u32 m){(void)p;(void)m;requests++;}
static void PG_FN_RELEASE_MODEL(w2c_game*p,u32 m){(void)p;(void)m;assert(owner==42);releases++;}
static u32 PG_FN_HAS_MODEL_LOADED(w2c_game*p,u32 m){(void)p;(void)m;return modelsLoaded;}
static u32 make(u32 model,unsigned kind,float x,float y,float z){if(failCreate)return 0;assert(nextEntity<4096);u32 e=nextEntity++;entities[e]=(Entity){.exists=true,.owned=true,.model=wrongModel?model^1:model,.kind=kind,.p={x,y,z}};return e;}
static u32 PG_FN_CREATE_VEHICLE(w2c_game*p,u32 m,u64 at,float h,u32 a,u32 b,u32 c){(void)p;(void)h;assert(a==0&&b==0&&c==1);float*v=pg_pointer(&env,at,24);return make(m,2,v[0],v[2],v[4]);}
static void PG_FN_GROUND_VEHICLE(w2c_game*p,u32 e,float z){(void)p;(void)e;(void)z;}
static u64 pg_f32_arg(float x){u32 n;memcpy(&n,&x,4);return n;}static float fl(u64 x){u32 n=(u32)x;float v;memcpy(&v,&n,4);return v;}
static u64 pg_test_call(w2c_game*,u64,int,const u64*);
#include "../Source/NativeMuZom.inc"
static unsigned model_kind(u32 model){
 for(unsigned i=0;i<MZ_PLACEMENTS_COUNT;i++)if(mzPlacements[i].model==model)return mzPlacements[i].kind;
 if(model==mz_hash("emperor")||model==mz_hash("ingot")||model==mz_hash("asea"))return 2;
 return 1;
}
static u64 pg_test_call(w2c_game*instance,u64 hash,int n,const u64*a){
 (void)instance;nativeCalls++;
 if(hash==MZ_IS_MODEL_IN_CDIMAGE)return validModel;
 if(hash==MZ_IS_MODEL_A_PED)return model_kind((u32)a[0])==1;
 if(hash==MZ_HAS_ANIM_SET_LOADED)return 1;
 if(hash==MZ_GET_SAFE_COORD_FOR_PED||hash==MZ_GET_CLOSEST_VEHICLE_NODE){assert(n==(hash==MZ_GET_SAFE_COORD_FOR_PED?6:7));if(!navOK)return 0;u64 at=a[hash==MZ_GET_SAFE_COORD_FOR_PED?4:3];float*v=pg_pointer(&env,at,24);memset(v,0,24);v[0]=fl(a[0]);v[2]=fl(a[1]);v[4]=fl(a[2]);return 1;}
 if(hash==MZ_CREATE_PED){assert(n==8&&a[6]==0&&a[7]==1);return make((u32)a[1],1,fl(a[2]),fl(a[3]),fl(a[4]));}
 if(hash==MZ_CREATE_OBJECT_NO_OFFSET){assert(n==7&&a[4]==0);return make((u32)a[0],3,fl(a[1]),fl(a[2]),fl(a[3]));}
 if(hash==MZ_TASK_COMBAT_PED){assert(n==4&&a[0]!=player&&a[1]==player&&a[2]==0&&a[3]==16);attacks++;return 0;}
 if(hash==MZ_REMOVE_ALL_PED_WEAPONS){entities[a[0]].unarmed=true;return 0;}
 if(hash==MZ_FREEZE_ENTITY_POSITION){entities[a[0]].frozen=true;return 0;}
 if(hash==MZ_IS_PED_DEAD_OR_DYING)return entities[a[0]].dead;
 if(hash==MZ_DELETE_ENTITY){u32*e=pg_pointer(&env,a[0],8);assert(*e!=player&&entities[*e].owned);entities[*e].exists=false;*e=0;deletions++;return 0;}
 return 0;
}
static unsigned live(unsigned kind){unsigned n=0;for(unsigned i=0;i<64;i++)if(mzLive[i].entity&&mzLive[i].kind==kind)n++;return n;}
static void tick(w2c_game*p){clockMS+=500;pg_muzom_tick(p);}
int main(void){
 w2c_game g={0};entities[1]=(Entity){.exists=true,.model=123,.p={-170,-880,29}};
 unsigned before=nativeCalls;pg_muzom_tick(&g);assert(nativeCalls==before); // Story/free mode untouched.
 PGSetZombieMode(true);atomic_store(&started,true);PGSetZombieMode(false);assert(atomic_load(&mzEnabled));
 paused=true;pg_muzom_tick(&g);assert(nativeCalls==before);paused=false;
 scene=true;pg_muzom_tick(&g);assert(nativeCalls==before);scene=false;
 allSupported=false;pg_muzom_tick(&g);assert(mzFailed&&nativeCalls==before);mzFailed=false;mzChecked=false;allSupported=true;
 for(unsigned i=0;i<160;i++)tick(&g);
 assert(mzVerified>=8&&live(1)==6&&live(2)==2&&live(3)>0&&live(3)<=16&&attacks>=6);
 for(unsigned i=0;i<64;i++)if(mzLive[i].kind==1&&mzLive[i].entity)assert(entities[mzLive[i].entity].unarmed);
 assert(requests==releases+(mzPending.active?1:0));
 unsigned killed=0;for(unsigned i=0;i<64;i++)if(mzLive[i].kind==1&&mzLive[i].entity){entities[mzLive[i].entity].dead=true;killed=mzLive[i].entity;break;}
 tick(&g);assert(mzKills==1);for(unsigned i=0;i<45;i++)tick(&g);assert(!entities[killed].exists);
 room=10ull<<20;unsigned created=mzVerified;for(unsigned i=0;i<20;i++)tick(&g);assert(mzVerified==created&&!mzPending.active);room=1024ull<<20;
 // Occupied abandoned cars and foreign/reused handles must never be deleted.
 u32 protected=0;for(unsigned i=0;i<64;i++)if(mzLive[i].kind==2&&mzLive[i].entity){protected=mzLive[i].entity;entities[protected].occupied=true;break;}assert(protected);
 entities[1].p[0]+=5000;unsigned del=deletions;tick(&g);assert(deletions>del&&entities[protected].exists);
 for(unsigned i=0;i<64;i++)if(mzLive[i].entity&&mzLive[i].entity!=protected){entities[mzLive[i].entity].owned=false;}
 tick(&g);assert(entities[protected].exists);
 // Model load timeouts are bounded and release the outstanding request.
 memset(mzLive,0,sizeof mzLive);mzPending.active=false;modelsLoaded=false;mzBadCount=0;
 float p[3]={entities[1].p[0]+30,entities[1].p[1],29};assert(mz_request(&g,0x123456,1,-1,p,0,clockMS));
 clockMS+=6000;tick(&g);assert(!mzPending.active&&mz_bad(0x123456));
 // Resuming after pause must accept an already-loaded model, not ban it on elapsed wall time.
 modelsLoaded=true;assert(mz_request(&g,0x123457,1,-1,p,0,clockMS));clockMS+=6000;tick(&g);assert(!mz_bad(0x123457)&&live(1)==1);
 // Fast travel invalidates pending old-area coordinates without creating in that area.
 assert(mz_request(&g,0x123458,1,-1,p,0,clockMS));entities[1].p[0]+=1000;created=mzVerified;tick(&g);assert(!mzPending.active&&mzVerified==created);
 // A handler change must not release through the wrong script owner.
 assert(mz_request(&g,0x123460,1,-1,p,0,clockMS));owner=99;before=releases;tick(&g);assert(!mzPending.active&&releases==before);owner=42;
 // Missing/invalid models are refused before REQUEST_MODEL.
 validModel=false;before=requests;assert(!mz_request(&g,0x123459,1,-1,p,0,clockMS));assert(requests==before);validModel=true;
 mzPending.active=false;unsigned active=live(1);for(unsigned i=0;i<300;i++){tick(&g);assert(live(1)<=6&&live(2)<=2&&live(3)<=16);}
 // The same fixed-storage runtime scales up only within each quota's caps.
 entities[1].p[0]=414;entities[1].p[1]=-1225;entities[1].p[2]=39;
 processLimitMB=4096;for(unsigned i=0;i<200;i++){tick(&g);assert(live(1)<=10&&live(2)<=3&&live(3)<=24);}
 assert(live(1)==10);
 processLimitMB=7096;for(unsigned i=0;i<200;i++){tick(&g);assert(live(1)<=14&&live(2)<=4&&live(3)<=32);}
 assert(live(1)==14);
 (void)active;
 printf("PASS production MuZom runtime: %u verified entities, %u safe deletes; caps/AI/ownership/memory/scene/timeout/respawn coordinates\n",mzVerified,deletions);
 return 0;
}
