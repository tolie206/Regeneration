// MuZom V001. All natives execute only on the existing main-script tick.
#include "MuZomNatives.h"
#include "MuZomMapData.h"
static _Atomic bool mzEnabled;
void PGSetZombieMode(bool enabled){if(!atomic_load(&started))atomic_store(&mzEnabled,enabled);}
typedef struct {u32 entity,model;unsigned kind;int placement;double deadAt,nextTask;} MZLive;
typedef struct {bool active;u32 model;unsigned kind;int placement;float p[3],heading;double began;u64 owner;} MZPending;
static MZLive mzLive[64];static MZPending mzPending;
static u32 mzBad[64];static unsigned mzBadCount,mzRandom=0x4d755a6f,mzKills,mzVerified;
static u64 mzScratch;static double mzNext,mzLogAt;static bool mzChecked,mzFailed,mzPoliceSet;static u32 mzLastPlayer;
#define MZCALL(name,...) pg_test_call(instance,MZ_##name,(int)(sizeof((u64[]){__VA_ARGS__})/sizeof(u64)),(u64[]){__VA_ARGS__})
static u32 mz_hash(const char *s){u32 h=0;for(;*s;s++){h+=(unsigned char)*s;h+=h<<10;h^=h>>6;}h+=h<<3;h^=h>>11;h+=h<<15;return h;}
static unsigned mz_rand(void){mzRandom^=mzRandom<<13;mzRandom^=mzRandom>>17;mzRandom^=mzRandom<<5;return mzRandom;}
static bool mz_bad(u32 model){for(unsigned i=0;i<mzBadCount;i++)if(mzBad[i]==model)return true;return false;}
static void mz_ban(u32 model){if(!mz_bad(model)&&mzBadCount<64){mzBad[mzBadCount++]=model;char line[112];snprintf(line,sizeof line,"MuZom: model 0x%08x unavailable/failed; skipped safely.",model);pg_log(line);}}
static bool mz_owned(w2c_game *instance,MZLive *e){return e->entity&&PG_FN_ENTITY_EXISTS(instance,e->entity)&&PG_FN_GET_ENTITY_MODEL(instance,e->entity)==e->model&&PG_FN_ENTITY_OWNED(instance,e->entity,0);}
static bool mz_delete(w2c_game *instance,MZLive *e){
 if(!mz_owned(instance,e)){memset(e,0,sizeof *e);return true;}
 if(e->kind==2)for(int seat=-1;seat<15;seat++)if(PG_FN_VEHICLE_OCCUPANT(instance,e->entity,(u32)seat,1))return false;
 *(u32*)pg_pointer(&env,mzScratch+128,8)=e->entity;
 MZCALL(DELETE_ENTITY,mzScratch+128);
 if(PG_FN_ENTITY_EXISTS(instance,e->entity))return false;
 memset(e,0,sizeof *e);return true;
}
static bool mz_used(int placement){for(unsigned i=0;i<64;i++)if(mzLive[i].entity&&mzLive[i].placement==placement)return true;return false;}
static bool mz_request(w2c_game *instance,u32 model,unsigned kind,int placement,const float *p,float heading,double now){
 if(mz_bad(model))return false;
 if(MZCALL(IS_MODEL_IN_CDIMAGE,model)!=1||(kind==1&&MZCALL(IS_MODEL_A_PED,model)!=1)||(kind==2&&!PG_FN_IS_VEHICLE_MODEL(instance,model))||(kind==3&&(MZCALL(IS_MODEL_A_PED,model)==1||PG_FN_IS_VEHICLE_MODEL(instance,model)))){mz_ban(model);return false;}
 if(kind==2){u32 category=PG_FN_VEHICLE_CLASS(instance,model);if(category==14||category==15||category==16||category==21){mz_ban(model);return false;}}
 mzPending=(MZPending){.active=true,.model=model,.kind=kind,.placement=placement,.heading=heading,.began=now,.owner=PG_FN_CURRENT_SCRIPT_HANDLER(instance)};
 memcpy(mzPending.p,p,12);PG_FN_REQUEST_MODEL(instance,model);return true;
}
static void mz_finish_request(w2c_game *instance){
 if(mzPending.active&&mzPending.owner==PG_FN_CURRENT_SCRIPT_HANDLER(instance))PG_FN_RELEASE_MODEL(instance,mzPending.model);
 mzPending.active=false;
}
static bool mz_create(w2c_game *instance,double now,u32 player){
 MZPending *q=&mzPending;u32 entity=0;
 if(q->kind==1)entity=(u32)MZCALL(CREATE_PED,4,q->model,pg_f32_arg(q->p[0]),pg_f32_arg(q->p[1]),pg_f32_arg(q->p[2]),pg_f32_arg(q->heading),0,1);
 else if(q->kind==2){float *v=pg_pointer(&env,mzScratch,24);memset(v,0,24);v[0]=q->p[0];v[2]=q->p[1];v[4]=q->p[2];entity=PG_FN_CREATE_VEHICLE(instance,q->model,mzScratch,q->heading,0,0,1);}
 else entity=(u32)MZCALL(CREATE_OBJECT_NO_OFFSET,q->model,pg_f32_arg(q->p[0]),pg_f32_arg(q->p[1]),pg_f32_arg(q->p[2]),0,1,0);
 if(!entity||entity==UINT32_MAX||entity==player||!PG_FN_ENTITY_EXISTS(instance,entity)||PG_FN_GET_ENTITY_MODEL(instance,entity)!=q->model||!PG_FN_ENTITY_OWNED(instance,entity,0)){mz_ban(q->model);return false;}
 unsigned slot=0;while(slot<64&&mzLive[slot].entity)slot++;
 if(slot==64)return false;
 mzLive[slot]=(MZLive){.entity=entity,.model=q->model,.kind=q->kind,.placement=q->placement,.nextTask=now+8000};
 MZCALL(SET_ENTITY_LOD_DIST,entity,120);
 if(q->kind==1){
  MZCALL(REMOVE_ALL_PED_WEAPONS,entity,1);MZCALL(SET_PED_AS_ENEMY,entity,1);MZCALL(SET_BLOCKING_OF_NON_TEMPORARY_EVENTS,entity,1);
  MZCALL(SET_ENTITY_HEALTH,entity,160,0);MZCALL(TASK_COMBAT_PED,entity,player,0,16);
  if(MZCALL(HAS_ANIM_SET_LOADED,mzScratch+64)==1)MZCALL(SET_PED_MOVEMENT_CLIPSET,entity,mzScratch+64,pg_f32_arg(0.25f));
 }else if(q->kind==2){PG_FN_GROUND_VEHICLE(instance,entity,5.f);MZCALL(SET_VEHICLE_ENGINE_HEALTH,entity,pg_f32_arg(250.f));MZCALL(SET_VEHICLE_DIRT_LEVEL,entity,pg_f32_arg(15.f));MZCALL(SET_VEHICLE_DOORS_LOCKED,entity,1);MZCALL(SET_VEHICLE_ENGINE_ON,entity,0,1,0);}
 else {if(q->placement>=0){const MZPlacement *p=&mzPlacements[q->placement];MZCALL(SET_ENTITY_ROTATION,entity,pg_f32_arg(p->pitch),pg_f32_arg(p->roll),pg_f32_arg(p->yaw),2,1);}MZCALL(FREEZE_ENTITY_POSITION,entity,1);}
 mzVerified++;
 if(mzVerified<=6){char line[160];snprintf(line,sizeof line,"MuZom verified entity: kind %u, handle %u, model 0x%08x, visible flag %u (engine state, not pixel proof).",q->kind,entity,q->model,PG_FN_SPAWN_ENTITY_VISIBLE(instance,entity));pg_log(line);}
 return true;
}
static void pg_muzom_tick(w2c_game *instance){
 if(!atomic_load(&mzEnabled)||mzFailed||PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneActive())return;
 if(!mzChecked){
  mzChecked=true;for(unsigned i=0;i<sizeof mzRequiredNatives/sizeof *mzRequiredNatives;i++)if(!mz_native_available(mzRequiredNatives[i])){mzFailed=true;pg_log("MuZom disabled safely: required native missing; no partial world changes.");return;}
 }
 u64 previous=pg_asi_enter_script(instance);u32 player=PG_FN_PLAYER_PED_ID(instance);
 if(!player||!PG_FN_CURRENT_SCRIPT_HANDLER(instance)){pg_asi_leave_script(instance,previous);return;}
 if(!mzScratch){mzScratch=pg_asi_alloc(256);if(!mzScratch){mzFailed=true;pg_asi_leave_script(instance,previous);return;}memset(pg_pointer(&env,mzScratch,256),0,256);strcpy(pg_pointer(&env,mzScratch+64,64),"move_m@drunk@verydrunk");MZCALL(REQUEST_ANIM_SET,mzScratch+64);pg_log("MuZom native survival started; scenery/AI are bounded and streamed locally.");}
 // Density controls are per-frame natives; only the heavier work is throttled.
 MZCALL(SET_PED_DENSITY_MULTIPLIER_THIS_FRAME,pg_f32_arg(0));MZCALL(SET_SCENARIO_PED_DENSITY_MULTIPLIER_THIS_FRAME,pg_f32_arg(0),pg_f32_arg(0));
 MZCALL(SET_VEHICLE_DENSITY_MULTIPLIER_THIS_FRAME,pg_f32_arg(0));MZCALL(SET_RANDOM_VEHICLE_DENSITY_MULTIPLIER_THIS_FRAME,pg_f32_arg(0));MZCALL(SET_PARKED_VEHICLE_DENSITY_MULTIPLIER_THIS_FRAME,pg_f32_arg(0));
 double now=timeMS(CLOCK_MONOTONIC);if(now<mzNext){pg_asi_leave_script(instance,previous);return;}mzNext=now+500;
 if(!mzPoliceSet){PG_FN_SET_MAX_WANTED(instance,0);u32 id=PG_FN_PLAYER_ID(instance);MZCALL(SET_POLICE_IGNORE_PLAYER,id,1);MZCALL(SET_PLAYER_WANTED_LEVEL,id,0,0);MZCALL(SET_PLAYER_WANTED_LEVEL_NOW,id,0);mzPoliceSet=true;}
 PG_FN_GET_ENTITY_COORDS(instance,mzScratch,player,1);float *v=pg_pointer(&env,mzScratch,24);float pos[3]={v[0],v[2],v[4]};
 if(!isfinite(pos[0])||!isfinite(pos[1])||!isfinite(pos[2])){pg_asi_leave_script(instance,previous);return;}
 unsigned zombies=0,cars=0,props=0,used=0;
 for(unsigned i=0;i<64;i++){
  MZLive *e=&mzLive[i];if(!e->entity)continue;if(!mz_owned(instance,e)){memset(e,0,sizeof *e);continue;}
  PG_FN_GET_ENTITY_COORDS(instance,mzScratch,e->entity,1);v=pg_pointer(&env,mzScratch,24);float dx=v[0]-pos[0],dy=v[2]-pos[1],dz=v[4]-pos[2];
  if(dx*dx+dy*dy+dz*dz>180.f*180.f){if(mz_delete(instance,e))continue;}
  if(e->kind==1){
   if(MZCALL(IS_PED_DEAD_OR_DYING,e->entity,1)==1){if(!e->deadAt){e->deadAt=now;mzKills++;}if(now-e->deadAt>20000&&mz_delete(instance,e))continue;}
   else if(player!=mzLastPlayer||now>=e->nextTask){MZCALL(TASK_COMBAT_PED,e->entity,player,0,16);e->nextTask=now+8000;}
   zombies++;
  }else if(e->kind==2)cars++;else props++;used++;
 }
 mzLastPlayer=player;
 if(now>=mzLogAt){char line[180];snprintf(line,sizeof line,"MuZom health: %u infected/corpses, %u abandoned cars, %u scenery, %u kills, %u verified creations; fixed capacity 64.",zombies,cars,props,mzKills,mzVerified);pg_log(line);mzLogAt=now+30000;}
 uint64_t room=UINT64_MAX;bool measured=nativeProcessHeadroom(&room);uint64_t reserve=distanceStreaming.reserveBytes;
 if(!measured)room=UINT64_MAX;
 bool memoryOK=room>=reserve+(128ull<<20);
 if(mzPending.active){
  if(mzPending.owner!=PG_FN_CURRENT_SCRIPT_HANDLER(instance)){mzPending.active=false;}
  else if(!memoryOK){mz_finish_request(instance);}
  else if((mzPending.p[0]-pos[0])*(mzPending.p[0]-pos[0])+(mzPending.p[1]-pos[1])*(mzPending.p[1]-pos[1])>140.f*140.f){mz_finish_request(instance);}
  else if(PG_FN_HAS_MODEL_LOADED(instance,mzPending.model)){if(used<64)mz_create(instance,now,player);mz_finish_request(instance);}
  else if(now-mzPending.began>5000){mz_ban(mzPending.model);mz_finish_request(instance);}
  pg_asi_leave_script(instance,previous);return;
 }
 if(!memoryOK||used>=64){pg_asi_leave_script(instance,previous);return;}
 unsigned zCap=processLimitMB<=2560?6:processLimitMB<=5000?10:14;
 unsigned carCap=processLimitMB<=2560?2:processLimitMB<=5000?3:4;
 unsigned propCap=processLimitMB<=2560?16:processLimitMB<=5000?24:32;
 if(zombies<zCap||cars<carCap){
  bool ped=zombies<zCap;
  if(!ped){int best=-1;float near=120.f*120.f;
   for(unsigned i=0;i<MZ_PLACEMENTS_COUNT;i++){const MZPlacement *p=&mzPlacements[i];if(p->kind!=2||mz_bad(p->model)||mz_used((int)i))continue;float dx=p->x-pos[0],dy=p->y-pos[1],dz=p->z-pos[2],d=dx*dx+dy*dy+dz*dz;if(d<near&&d>20.f*20.f){near=d;best=(int)i;}}
   if(best>=0){const MZPlacement *p=&mzPlacements[best];float a[3]={p->x,p->y,p->z};if(mz_request(instance,p->model,2,best,a,p->yaw,now)){pg_asi_leave_script(instance,previous);return;}}
  }
  float angle=(mz_rand()%6283)/1000.f,dist=ped?30.f+(mz_rand()%20):45.f+(mz_rand()%20);
  float x=pos[0]+sinf(angle)*dist,y=pos[1]+cosf(angle)*dist;
  u64 result=ped?MZCALL(GET_SAFE_COORD_FOR_PED,pg_f32_arg(x),pg_f32_arg(y),pg_f32_arg(pos[2]),0,mzScratch,14):MZCALL(GET_CLOSEST_VEHICLE_NODE,pg_f32_arg(x),pg_f32_arg(y),pg_f32_arg(pos[2]),mzScratch,1,pg_f32_arg(3.f),pg_f32_arg(0.f));
  if(result==1){v=pg_pointer(&env,mzScratch,24);float p[3]={v[0],v[2],v[4]};float dx=p[0]-pos[0],dy=p[1]-pos[1],dz=p[2]-pos[2];
   if(isfinite(p[0])&&isfinite(p[1])&&isfinite(p[2])&&dx*dx+dy*dy>=20.f*20.f&&dx*dx+dy*dy<=100.f*100.f&&fabsf(dz)<12.f){
    const char *peds[]={"u_m_y_zombie_01","a_m_m_tramp_01","a_m_m_skidrow_01","a_m_m_hillbilly_01"};const char *vehicles[]={"emperor","ingot","asea"};
    u32 model=mz_hash(ped?peds[mz_rand()%4]:vehicles[mz_rand()%3]);mz_request(instance,model,ped?1:2,-1,p,(float)(mz_rand()%360),now);
   }
  }
 }else if(props<propCap){
  int best=-1;float near=120.f*120.f;
  for(unsigned i=0;i<MZ_PLACEMENTS_COUNT;i++){const MZPlacement *p=&mzPlacements[i];if(p->kind==2&&cars>=carCap)continue;if(mz_bad(p->model)||mz_used((int)i))continue;
   float dx=p->x-pos[0],dy=p->y-pos[1],dz=p->z-pos[2],d=dx*dx+dy*dy+dz*dz;if(d<near&&d>12.f*12.f){near=d;best=(int)i;}}
  if(best>=0){const MZPlacement *p=&mzPlacements[best];float a[3]={p->x,p->y,p->z};mz_request(instance,p->model,p->kind,best,a,p->yaw,now);}
 }
 pg_asi_leave_script(instance,previous);
}
#undef MZCALL
