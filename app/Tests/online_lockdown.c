#define PG_ROLEPLAY_CLIENT 1
#define main offline_tests_not_executed
#include "vehicle_spawn.c"
#undef main
int main(void){
 assert(!PGQueueCheat(PGCheatRepairVehicle,0));assert(!PGQueueCheat(PGCheatCameraMode,4));
 assert(!PGSetPersistentCheatEnabled(PGCheatGodMode,true));assert(!PGSetPersistentCheatEnabled(PGCheatNeverWanted,true));
 assert(!PGSpawnVehicle(123,true));return 0;}
