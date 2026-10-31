#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
typedef uint64_t u64;typedef uint32_t u32;
typedef struct {unsigned char *data;uint64_t size;} wasm_rt_shared_memory_t;
typedef struct {wasm_rt_shared_memory_t *w2c_env_memory;} w2c_game;
#define PG_CAMERA_FRAME_TEST 1
#define PG_FN_FIRST_PERSON_VEHICLE test_first_person_vehicle
static uint64_t vehicleCamera;static float extra=15;
static float pg_first_person_extra(void){return extra;}
static u64 test_first_person_vehicle(w2c_game *i){(void)i;return vehicleCamera;}
#include "../Source/NativeCameraFrame.c"
static unsigned char bytes[2048];
static void setf(unsigned at,float f){memcpy(bytes+at,&f,4);}
static float getf(unsigned at){float f;memcpy(&f,bytes+at,4);return f;}
int main(void){
 wasm_rt_shared_memory_t memory={bytes,sizeof bytes};w2c_game game={&memory};
 setf(256+160,60);setf(1024+108,123);setf(1024+116,456);
 for(unsigned n=0;n<10000;n++){
  setf(1024+112,getf(256+160));u64 old=pg_camera_frame_begin();pg_camera_mark_shooter(256);pg_camera_frame_end(&game,256,1024,old,1);
  assert(getf(1024+112)==75&&getf(256+160)==60); // source camera never feeds widened FOV back
 }
 assert(getf(1024+108)==123&&getf(1024+116)==456);
 setf(1024+112,60);u64 old=pg_camera_frame_begin();pg_camera_frame_end(&game,256,1024,old,1);assert(getf(1024+112)==60); // third person/cutscene
 vehicleCamera=512;old=pg_camera_frame_begin();pg_camera_mark_vehicle(&game,512);setf(1024+112,45);pg_camera_frame_end(&game,512,1024,old,1);assert(getf(1024+112)==60); // bike/car base45 supported
 old=pg_camera_frame_begin();pg_camera_mark_vehicle(&game,768);setf(1024+112,45);pg_camera_frame_end(&game,768,1024,old,1);assert(getf(1024+112)==45);
 old=pg_camera_frame_begin();pg_camera_mark_shooter(256);u64 nested=pg_camera_frame_begin();pg_camera_mark_vehicle(&game,512);setf(1280+112,45);pg_camera_frame_end(&game,512,1280,nested,1);setf(1024+112,60);pg_camera_frame_end(&game,256,1024,old,1);assert(getf(1280+112)==60&&getf(1024+112)==75);
 old=pg_camera_frame_begin();pg_camera_mark_shooter(256);setf(1024+112,60);pg_camera_frame_end(&game,256,1024,old,0);assert(getf(1024+112)==60);
 extra=0;old=pg_camera_frame_begin();pg_camera_mark_shooter(256);pg_camera_frame_end(&game,256,1024,old,1);assert(getf(1024+112)==60);
 assert(!pg_camera_frame_apply(bytes,sizeof bytes,UINT64_MAX,15,false));assert(!pg_camera_frame_apply(bytes,1100,1024,15,false));
 puts("PASS 10000 stable frames, untouched camera state, bike/car, nested camera, cutscene/failed/0-FOV/bounds");
}
