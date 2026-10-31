#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
typedef uint64_t u64;typedef uint32_t u32;typedef struct{int unused;} w2c_game;
static bool gameplay=true,first=true,bike=true,paused,loading;static int status;static float wide=15;
static u32 player=1,vehicle=10;
static float pg_first_person_extra(void){return wide;}
static int PGPauseMenuActive(void){return paused;}
static int PGGameStatus(void){return status;}
static bool PGLoadSceneActive(void){return loading;}
static u64 pg_asi_enter_script(w2c_game *i){(void)i;return 0;}
static void pg_asi_leave_script(w2c_game *i,u64 p){(void)i;(void)p;}
static u32 PG_FN_PLAYER_PED_ID(w2c_game*i){(void)i;return player;}
static u32 PG_FN_PED_VEHICLE(w2c_game*i,u32 p,u32 last){(void)i;(void)p;(void)last;return vehicle;}
static u32 PG_FN_GET_ENTITY_MODEL(w2c_game*i,u32 v){(void)i;return v+100;}
static u64 PG_FN_TURBO_ENTITY_ADDRESS(w2c_game*i,u32 p){(void)i;return p*100;}
static u32 PG_FN_BIKE_MODEL(w2c_game*i,u32 m){(void)i;(void)m;return bike;}
static u32 PG_FN_GAMEPLAY_RENDERING(w2c_game*i){(void)i;return gameplay;}
static u32 PG_FN_RENDERED_FIRST_PERSON(w2c_game*i){(void)i;return first;}
#include "../Source/NativeBikeBody.inc"
int main(void){
 w2c_game game={0};pg_bike_body_tick(&game);assert(pg_hide_bike_body(&game,100));assert(!pg_hide_bike_body(&game,200)); // NPC untouched
 first=false;assert(!pg_hide_bike_body(&game,100));pg_bike_body_tick(&game);assert(!atomic_load(&bikeBodyPed));first=true;
 gameplay=false;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));gameplay=true;
 bike=false;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));bike=true;
 vehicle=0;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));vehicle=10;
 wide=0;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));wide=15;
 paused=true;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));paused=false;
 loading=true;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));loading=false;
 status=1;pg_bike_body_tick(&game);assert(!pg_hide_bike_body(&game,100));status=0;
 pg_bike_body_tick(&game);assert(pg_hide_bike_body(&game,100));PGSetHideBikeBody(0);assert(!pg_hide_bike_body(&game,100));
 PGSetHideBikeBody(1);player=2;pg_bike_body_tick(&game);assert(pg_hide_bike_body(&game,200)&&!pg_hide_bike_body(&game,100));
 puts("PASS only local bike/first-person/wide; restore on foot/car/third-person/pause/load/cutscene/off/respawn; NPC unaffected");
}
