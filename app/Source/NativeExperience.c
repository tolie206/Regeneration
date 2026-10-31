#include "NativeExperience.h"
#include <stdatomic.h>
static _Atomic float engineGainDB=6, firstPersonExtra=0;
void PGSetVehicleEngineGain(float db){atomic_store(&engineGainDB,isfinite(db)?fminf(fmaxf(db,0),12):0);}
void PGSetFirstPersonWide(float degrees){atomic_store(&firstPersonExtra,isfinite(degrees)?fminf(fmaxf(degrees,0),20):0);}
float pg_vehicle_engine_db(float db){return pg_engine_gain_value(db,atomic_load(&engineGainDB));}
float pg_first_person_fov(float original){return pg_first_person_fov_value(original,atomic_load(&firstPersonExtra));}
