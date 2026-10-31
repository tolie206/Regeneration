#pragma once
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
// Granular SetChannelVolume takes linear amplitude, not dB.
static inline float pg_grain_gain_value(float amplitude,float factor){
 if(!isfinite(amplitude)||amplitude<=0||!isfinite(factor)||factor<=1)return amplitude;
 float out=amplitude*fminf(factor,3.98107171f);return isfinite(out)?out:amplitude;
}
// This sees native FINAL frame FOV, never the previously widened camera state.
static inline float pg_first_person_fov_value(float original,float extra){
 if(!isfinite(original)||!isfinite(extra)||extra<=0||original<=45||original>=120)return original;
 float t=fminf(fmaxf((original-45)/15,0),1);t=t*t*(3-2*t);
 return fminf(original+fminf(extra,20)*t,110);
}
static inline float pg_first_person_vehicle_fov_value(float original,float extra){
 if(!isfinite(original)||!isfinite(extra)||extra<=0||original<30||original>=120)return original;
 return fminf(original+fminf(extra,20),110);
}
// Tagged camera pointer: engine objects are aligned; low bit identifies vehicle.
typedef struct {uint64_t camera;} PGCameraScope;
static inline uint64_t pg_camera_scope_push(PGCameraScope *s){uint64_t parent=s->camera;s->camera=0;return parent;}
static inline bool pg_camera_scope_pop(PGCameraScope *s,uint64_t camera,uint64_t parent,bool success){bool apply=success&&camera&&(s->camera&~1ull)==camera;s->camera=parent;return apply;}
static inline bool pg_camera_frame_apply(void *base,uint64_t size,uint64_t frame,float extra,bool vehicle){
 if(!base||!frame||frame>size||size-frame<116)return false;
 unsigned char *p=base;float original;memcpy(&original,p+frame+112,4);
 float value=vehicle?pg_first_person_vehicle_fov_value(original,extra):pg_first_person_fov_value(original,extra);if(value==original||!isfinite(value))return false;
 memcpy(p+frame+112,&value,4);return true;
}
