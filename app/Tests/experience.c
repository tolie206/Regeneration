#include "../Source/NativeExperience.h"
#include "../Source/NativeExperience.c"
#include <assert.h>
#include <stdio.h>
int main(void){
 assert(pg_engine_gain_value(-20,6)==-14);
 assert(pg_engine_gain_value(-100,12)==-100);
 assert(pg_engine_gain_value(-96,12)==-96);
 assert(pg_engine_gain_value(-20,0)==-20);
 assert(pg_engine_gain_value(10,12)==12);
 assert(isnan(pg_engine_gain_value(NAN,6)));
 assert(pg_first_person_fov_value(60,15)==75);
 assert(pg_first_person_fov_value(85,20)==100);
 assert(pg_first_person_fov_value(30,20)==30); // sniper zoom retained
 assert(pg_first_person_fov_value(60,0)==60);
 assert(isnan(pg_first_person_fov_value(NAN,10)));
 PGSetVehicleEngineGain(6);assert(pg_vehicle_engine_db(-20)==-14);
 PGSetVehicleEngineGain(0);assert(pg_vehicle_engine_db(-20)==-20);
 PGSetVehicleEngineGain(100);assert(pg_vehicle_engine_db(-20)==-8);
 PGSetVehicleEngineGain(NAN);assert(pg_vehicle_engine_db(-20)==-20);
 PGSetFirstPersonWide(15);assert(pg_first_person_fov(60)==75);
 PGSetFirstPersonWide(0);assert(pg_first_person_fov(60)==60);
 puts("PASS engine dB gain, silent stop sentinel, scope zoom and bounds");
}
