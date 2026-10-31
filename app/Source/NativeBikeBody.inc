// Local draw guard: a remembered/last vehicle is NOT proof of current occupancy.
static _Atomic bool bikeBodyEnabled=true;
static _Atomic uint64_t bikeBodyPed,bikeBodySkips;
static _Atomic unsigned bikeBodyReason;
uint64_t PGHiddenBikeDraws(void){return atomic_load(&bikeBodySkips);}
unsigned PGBikeBodyReason(void){return atomic_load(&bikeBodyReason);}
extern float pg_first_person_extra(void);
u32 PG_FN_BIKE_MODEL(w2c_game*,u32);
u32 PG_FN_GAMEPLAY_RENDERING(w2c_game*);
u32 PG_FN_VEHICLE_VIEW_MODE(w2c_game*);
u32 PG_FN_PED_OCCUPIED(w2c_game*,u32,u32);
void PGSetHideBikeBody(int enabled){atomic_store(&bikeBodyEnabled,enabled!=0);if(!enabled){atomic_store(&bikeBodyPed,0);atomic_store(&bikeBodyReason,0);}}
static void pg_bike_body_tick(w2c_game *instance){
 atomic_store(&bikeBodyPed,0);atomic_store(&bikeBodyReason,0);
 if(!atomic_load(&bikeBodyEnabled)||pg_first_person_extra()<=0||PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneActive())return;
 // Cache identity only. Eligibility must be fresh at draw submission, not cached across dismounts.
 u64 previous=pg_asi_enter_script(instance);u32 ped=PG_FN_PLAYER_PED_ID(instance);
 if(ped)atomic_store(&bikeBodyPed,PG_FN_TURBO_ENTITY_ADDRESS(instance,ped));
 pg_asi_leave_script(instance,previous);
}
bool pg_hide_bike_body(w2c_game *instance,u64 entity){
 if(!entity||entity!=atomic_load(&bikeBodyPed)||!atomic_load(&bikeBodyEnabled)||pg_first_person_extra()<=0)return false;
 if(PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneActive()||!PG_FN_GAMEPLAY_RENDERING(instance)){atomic_store(&bikeBodyReason,6);return false;}
 u32 ped=PG_FN_PLAYER_PED_ID(instance);
 if(!ped||PG_FN_TURBO_ENTITY_ADDRESS(instance,ped)!=entity){atomic_store(&bikeBodyReason,1);return false;}
 // GetVehiclePedIsIn(false) in this pinned engine reads5576 without checking seated bit5291:64.
 // IsPedInAnyVehicle(false) checks that bit, and does NOT count entering/last vehicles.
 if(!PG_FN_PED_OCCUPIED(instance,ped,0)){atomic_store(&bikeBodyReason,2);return false;}
 u32 vehicle=PG_FN_PED_VEHICLE(instance,ped,0);
 if(!vehicle){atomic_store(&bikeBodyReason,3);return false;}
 if(!PG_FN_BIKE_MODEL(instance,PG_FN_GET_ENTITY_MODEL(instance,vehicle))){atomic_store(&bikeBodyReason,4);return false;}
 // The vehicle follow-camera context is distinct from on-foot first-person/aim cameras.
 if(PG_FN_VEHICLE_VIEW_MODE(instance)!=4){atomic_store(&bikeBodyReason,5);return false;}
 atomic_store(&bikeBodyReason,7);atomic_fetch_add(&bikeBodySkips,1);return true;
}
