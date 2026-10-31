// Local render suppression only. No entity visibility/alpha, model, texture or network writes.
static _Atomic bool bikeBodyEnabled=true;
static _Atomic uint64_t bikeBodyPed,bikeBodySkips;
uint64_t PGHiddenBikeDraws(void){return atomic_load(&bikeBodySkips);}
extern float pg_first_person_extra(void);
u32 PG_FN_BIKE_MODEL(w2c_game*,u32);
u32 PG_FN_GAMEPLAY_RENDERING(w2c_game*);
u32 PG_FN_RENDERED_FIRST_PERSON(w2c_game*);
void PGSetHideBikeBody(int enabled){atomic_store(&bikeBodyEnabled,enabled!=0);if(!enabled)atomic_store(&bikeBodyPed,0);}
static void pg_bike_body_tick(w2c_game *instance){
 atomic_store(&bikeBodyPed,0);
 if(!atomic_load(&bikeBodyEnabled)||pg_first_person_extra()<=0||PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneActive())return;
 if(!PG_FN_GAMEPLAY_RENDERING(instance)||!PG_FN_RENDERED_FIRST_PERSON(instance))return;
 u64 previous=pg_asi_enter_script(instance);
 u32 ped=PG_FN_PLAYER_PED_ID(instance),vehicle=ped?PG_FN_PED_VEHICLE(instance,ped,0):0;
 if(vehicle&&PG_FN_BIKE_MODEL(instance,PG_FN_GET_ENTITY_MODEL(instance,vehicle)))
  atomic_store(&bikeBodyPed,PG_FN_TURBO_ENTITY_ADDRESS(instance,ped));
 pg_asi_leave_script(instance,previous);
}
bool pg_hide_bike_body(w2c_game *instance,u64 entity){
 if(!entity||entity!=atomic_load(&bikeBodyPed)||!atomic_load(&bikeBodyEnabled)||pg_first_person_extra()<=0)return false;
 if(PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneActive())return false;
 if(!PG_FN_GAMEPLAY_RENDERING(instance)||!PG_FN_RENDERED_FIRST_PERSON(instance))return false;
 atomic_fetch_add(&bikeBodySkips,1);return true;
}
