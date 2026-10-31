#pragma once
#include <math.h>
// Engine components supply dB, including -100 dB stop/fade sentinels.
static inline float pg_engine_gain_value(float db,float gain){
 if(!isfinite(db)||db<=-96.f||!isfinite(gain)||gain<=0)return db;
 return fminf(db+fminf(gain,12.f),12.f);
}
// Only called from native first-person SHOOTER camera's FOV stores.
// Keep scope/sniper zoom and unusual/scripted values unchanged.
static inline float pg_first_person_fov_value(float original,float extra){
 if(!isfinite(original)||!isfinite(extra)||extra<=0||original<50||original>85)return original;
 return fminf(original+fminf(extra,20),100);
}
