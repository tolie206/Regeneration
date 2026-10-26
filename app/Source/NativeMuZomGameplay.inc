// Fixed-size survival state; no guest allocation or disk access in per-frame UI reads.
#include "MuZomSurvival.h"
#include <pthread.h>
static pthread_mutex_t mzHUDLock=PTHREAD_MUTEX_INITIALIZER;
static PGZombieHUD mzHUD;
static _Atomic int mzAction;
static MZSurvival mzSurvival;
static bool mzSurvivalLoaded;
static double mzSurvivalAt,mzSaveAt,mzWeatherAt,mzGroanAt,mzDamageAt,mzEquipAt;
static int mzWeatherPhase=-1,mzNotice,mzWaypointStage=-1;
static u32 mzEquipped;
typedef struct{bool active;float p[3];unsigned type;double until;} MZLoot;
static MZLoot mzLoot[24];
bool PGZombieRead(PGZombieHUD *out){if(!out)return false;pthread_mutex_lock(&mzHUDLock);*out=mzHUD;pthread_mutex_unlock(&mzHUDLock);return out->ready!=0;}
bool PGZombieAction(int32_t action){if(action<1||action>17||(action>4&&action<10))return false;int expected=0;return atomic_compare_exchange_strong(&mzAction,&expected,action);}
static float mz_dist2(const float *a,const float *b){float x=a[0]-b[0],y=a[1]-b[1],z=a[2]-b[2];return x*x+y*y+z*z;}
static const float mzShelter[3]={-172.f,-880.f,29.f},mzHospital[3]={310.f,-593.f,43.f};
static const float *mz_objective(void){return mzSurvival.stage==1?mzHospital:mzShelter;}
static void mz_marker(w2c_game *instance,const float *p,float size,unsigned red,unsigned green,unsigned blue){
 MZCALL(DRAW_MARKER,1,pg_f32_arg(p[0]),pg_f32_arg(p[1]),pg_f32_arg(p[2]-0.8f),0,0,0,0,0,0,pg_f32_arg(size),pg_f32_arg(size),pg_f32_arg(.5f),red,green,blue,150,0,0,2,0,0,0,0);
}
static void mz_draw_survival(w2c_game *instance,const float *pos){
 if(mz_dist2(pos,mzShelter)<120.f*120.f)mz_marker(instance,mzShelter,3,40,160,220);
 const float *obj=mz_objective();if(mzSurvival.stage<4&&mzSurvival.stage!=2&&obj!=mzShelter&&mz_dist2(pos,obj)<120.f*120.f)mz_marker(instance,obj,3,230,160,40);
 unsigned shown=0;for(unsigned i=0;i<24&&shown<3;i++)if(mzLoot[i].active&&mz_dist2(pos,mzLoot[i].p)<45.f*45.f){mz_marker(instance,mzLoot[i].p,.6f,100,220,90);shown++;}
}
static void mz_drop(w2c_game *instance,u32 entity,u32 player,const float *at,double now){
 u64 source=MZCALL(GET_PED_SOURCE_OF_DEATH,entity);u64 car=MZCALL(GET_VEHICLE_PED_IS_IN,player,0);
 if(source!=player&&(!car||source!=car))return;
 if(mzSurvival.kills<1000000)mzSurvival.kills++;
 for(unsigned i=0;i<24;i++)if(!mzLoot[i].active){mzLoot[i]=(MZLoot){.active=true,.type=mz_rand()%5,.until=now+90000};memcpy(mzLoot[i].p,at,12);break;}
}
static void mz_survival_tick(w2c_game *instance,u32 player,const float *pos,double now){
 if(!mzSurvivalLoaded){mzSurvival=mz_new_survival();MZSurvival saved;if(PGZombieLoad(&saved)&&mz_valid_survival(saved))mzSurvival=saved;mzSurvivalLoaded=true;mzSurvivalAt=now;mzEquipAt=now+4000;}
 float dt=(float)((now-mzSurvivalAt)/1000.);mzSurvivalAt=now;mz_survival_time(&mzSurvival,dt);
 if(mzEquipped!=player&&now>=mzEquipAt){
  // Sandbox equips all weapons during startup; apply survival inventory once after it settles.
  MZCALL(REMOVE_ALL_PED_WEAPONS,player,1);MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_pistol"),mzSurvival.ammo,0,1);MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_crowbar"),1,0,0);
  if(mzSurvival.weapons&1)MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_pumpshotgun"),mzSurvival.shotAmmo,0,0);
  if(mzSurvival.weapons&2)MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_microsmg"),mzSurvival.smgAmmo,0,0);
  mzEquipped=player;
 }
 if(mzWaypointStage!=(int)mzSurvival.stage){const float *destination=mz_objective();if(mzSurvival.stage==2||mzSurvival.stage==4)pg_test_call(instance,MZ_SET_WAYPOINT_OFF,0,NULL);else MZCALL(SET_NEW_WAYPOINT,pg_f32_arg(destination[0]),pg_f32_arg(destination[1]));mzWaypointStage=(int)mzSurvival.stage;}
 bool night=mz_night(mzSurvival);
 if(now>=mzWeatherAt){
  // 15-minute night (18:00-06:00), 5-minute day (06:00-18:00).
  float hours=night?18.f+mzSurvival.cycle*12.f/900.f:6.f+(mzSurvival.cycle-900)*12.f/300.f;unsigned minutes=(unsigned)(hours*60)%1440;
  MZCALL(PAUSE_CLOCK,1);MZCALL(SET_CLOCK_TIME,minutes/60,minutes%60,0);mzWeatherAt=now+5000;
  if(mzWeatherPhase!=(int)night){strcpy(pg_pointer(&env,mzScratch+160,32),night?"FOGGY":"OVERCAST");MZCALL(SET_WEATHER_TYPE_NOW_PERSIST,mzScratch+160);mzWeatherPhase=night;}
 }
 int nearest=-1;float nearestD=5.f*5.f;
 for(unsigned i=0;i<24;i++)if(mzLoot[i].active){float d=mz_dist2(pos,mzLoot[i].p);if(now>=mzLoot[i].until||d>220.f*220.f){mzLoot[i].active=false;continue;}if(d<nearestD){nearestD=d;nearest=(int)i;}}
 bool shop=mz_dist2(pos,mzShelter)<12.f*12.f;
 int action=atomic_exchange(&mzAction,0);bool changed=false;
 if(action){mzNotice=0;
  if(action==1&&mzSurvival.food){mzSurvival.food--;mzSurvival.hunger=fminf(100,mzSurvival.hunger+40);changed=true;}
  else if(action==2&&mzSurvival.water){mzSurvival.water--;mzSurvival.thirst=fminf(100,mzSurvival.thirst+45);changed=true;}
  else if(action==3&&mzSurvival.medkits){u64 health=MZCALL(GET_ENTITY_HEALTH,player);if(health>100&&health<200){mzSurvival.medkits--;MZCALL(SET_ENTITY_HEALTH,player,health+50>200?200:health+50,0);changed=true;}}
  else if(action==4){
   if(nearest>=0){unsigned type=mzLoot[nearest].type;mz_loot_reward(&mzSurvival,type);if(type==2&&mzEquipped==player)MZCALL(ADD_AMMO_TO_PED,player,mz_hash("weapon_pistol"),12);mzLoot[nearest].active=false;changed=true;mzNotice=2;}
   else if(mzSurvival.stage==0&&shop){mzSurvival.stage=1;mzSurvival.cash+=60;changed=true;mzNotice=3;}
   else if(mzSurvival.stage==1&&mz_dist2(pos,mzHospital)<10.f*10.f){mzSurvival.stage=2;mzSurvival.kills=0;mzSurvival.medkits++;changed=true;mzNotice=3;}
   else if(mzSurvival.stage==3&&shop){mzSurvival.stage=4;mzSurvival.cash+=150;changed=true;mzNotice=3;}
  }else if(action>=10&&mz_buy(&mzSurvival,action,shop)){
   if(action==13&&mzEquipped==player)MZCALL(ADD_AMMO_TO_PED,player,mz_hash("weapon_pistol"),24);
   if(action==14)MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_pumpshotgun"),mzSurvival.shotAmmo,0,0);
   if(action==15)MZCALL(GIVE_WEAPON_TO_PED,player,mz_hash("weapon_microsmg"),mzSurvival.smgAmmo,0,0);
   if(action==16)MZCALL(ADD_AMMO_TO_PED,player,mz_hash("weapon_pumpshotgun"),24);if(action==17)MZCALL(ADD_AMMO_TO_PED,player,mz_hash("weapon_microsmg"),60);changed=true;
  }
  if(!changed)mzNotice=1;
 }
 if(mzSurvival.stage==2&&mzSurvival.kills>=5){mzSurvival.stage=3;changed=true;mzNotice=3;}
 if(now>=mzDamageAt){mzDamageAt=now+5000;if(mzSurvival.hunger<=0||mzSurvival.thirst<=0){u64 h=MZCALL(GET_ENTITY_HEALTH,player);if(h>110&&h<10000)MZCALL(SET_ENTITY_HEALTH,player,h-2,0);}}
 if(changed||now>=mzSaveAt){
  if(mzEquipped==player){u64 ammo=MZCALL(GET_AMMO_IN_PED_WEAPON,player,mz_hash("weapon_pistol"));if(ammo<=9999)mzSurvival.ammo=(u32)ammo;ammo=MZCALL(GET_AMMO_IN_PED_WEAPON,player,mz_hash("weapon_pumpshotgun"));if(ammo<=9999)mzSurvival.shotAmmo=(u32)ammo;ammo=MZCALL(GET_AMMO_IN_PED_WEAPON,player,mz_hash("weapon_microsmg"));if(ammo<=9999)mzSurvival.smgAmmo=(u32)ammo;}
  PGZombieSave(mzSurvival);mzSaveAt=now+15000;
 }
 PGZombieHUD hud={.ready=mzEquipped==player,.hunger=(int)mzSurvival.hunger,.thirst=(int)mzSurvival.thirst,.cash=(int)mzSurvival.cash,.food=(int)mzSurvival.food,.water=(int)mzSurvival.water,.medkits=(int)mzSurvival.medkits,.stage=(int)mzSurvival.stage,.kills=(int)mzSurvival.kills,.night=night,.minutes=(int)ceilf((night?900:1200)-mzSurvival.cycle)/60,.shop=shop,.loot=nearest>=0,.notice=mzNotice};
 pthread_mutex_lock(&mzHUDLock);mzHUD=hud;pthread_mutex_unlock(&mzHUDLock);
}
