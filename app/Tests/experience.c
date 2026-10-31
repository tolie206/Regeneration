#include "../Source/NativeExperience.c"
#include <assert.h>
#include <float.h>
#include <stdio.h>
int main(void){
 for(int db=0;db<=12;db+=3){
  PGSetVehicleEngineGain(db);float factor=powf(10,db/20.f);
  assert(fabsf(pg_vehicle_grain_gain(.1f)-.1f*factor)<1e-6);
  assert(pg_vehicle_grain_gain(0)==0);assert(pg_vehicle_grain_gain(-1)==-1);
 }
 assert(isnan(pg_vehicle_grain_gain(NAN)));assert(pg_vehicle_grain_gain(FLT_MAX)==FLT_MAX);
 PGSetVehicleEngineGain(0);assert(pg_vehicle_grain_gain(.25f)==.25f);
 PGSetVehicleEngineGain(NAN);assert(pg_vehicle_grain_gain(.25f)==.25f);
 assert(pg_first_person_fov_value(60,15)==75);assert(pg_first_person_fov_value(85,20)==105);
 assert(pg_first_person_fov_value(30,20)==30);assert(pg_first_person_fov_value(60,0)==60);
 assert(pg_first_person_vehicle_fov_value(45,15)==60);
 float previous=0;for(int i=450;i<=1100;i++){float v=pg_first_person_fov_value(i/10.f,20);assert(v>=previous);previous=v;}
 uint64_t counters[4];PGVehicleGrainDiagnostics(counters);assert(counters[0]>0&&counters[1]>0);
 puts("PASS linear granular gain, no fabricated silence, 0dB rollback, monotonic FOV");
}
