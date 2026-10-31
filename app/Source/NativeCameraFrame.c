#ifndef PG_CAMERA_FRAME_TEST
#include "HostInternal.h"
#include "engine-functions.h"
#endif
#include "NativeExperience.h"
u64 PG_FN_FIRST_PERSON_VEHICLE(w2c_game*);
extern float pg_first_person_extra(void);
static _Thread_local PGCameraScope scope;
u64 pg_camera_frame_begin(void){return pg_camera_scope_push(&scope);}
void pg_camera_mark_shooter(u64 camera){if(!(camera&1))scope.camera=camera;}
void pg_camera_mark_vehicle(w2c_game *instance,u64 camera){if(!(camera&1)&&PG_FN_FIRST_PERSON_VEHICLE(instance)==camera)scope.camera=camera|1;}
void pg_camera_frame_end(w2c_game *instance,u64 camera,u64 frame,u64 parent,u32 success){
 bool vehicle=(scope.camera&1)!=0;
 if(!pg_camera_scope_pop(&scope,camera,parent,success!=0))return;
 wasm_rt_shared_memory_t *m=instance->w2c_env_memory;
 pg_camera_frame_apply((void *)m->data,m->size,frame,pg_first_person_extra(),vehicle);
}
