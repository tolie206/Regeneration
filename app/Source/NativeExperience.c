#include "NativeExperience.h"
#include <stdatomic.h>
static _Atomic float engineGainDB=6,engineLinearGain=1.9952623f,firstPersonExtra=0;
static _Atomic uint64_t grainCalls,grainPositive,grainProbes,grainOutput;
void PGSetVehicleEngineGain(float db){db=isfinite(db)?fminf(fmaxf(db,0),12):0;atomic_store(&engineGainDB,db);atomic_store(&engineLinearGain,powf(10,db/20));}
void PGSetFirstPersonWide(float degrees){atomic_store(&firstPersonExtra,isfinite(degrees)?fminf(fmaxf(degrees,0),20):0);}
float pg_first_person_extra(void){return atomic_load(&firstPersonExtra);}
float pg_vehicle_grain_gain(float amplitude){atomic_fetch_add(&grainCalls,1);if(isfinite(amplitude)&&amplitude>0)atomic_fetch_add(&grainPositive,1);return pg_grain_gain_value(amplitude,atomic_load(&engineLinearGain));}
void pg_note_granular_block(bool nonzero){atomic_fetch_add(&grainProbes,1);if(nonzero)atomic_fetch_add(&grainOutput,1);}
float PGVehicleGrainDiagnostics(uint64_t out[4]){out[0]=atomic_load(&grainCalls);out[1]=atomic_load(&grainPositive);out[2]=atomic_load(&grainProbes);out[3]=atomic_load(&grainOutput);return atomic_load(&engineGainDB);}
