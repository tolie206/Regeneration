#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <math.h>
// Main-script thread owns the anchor; only the short-lived permit crosses threads.
typedef struct {
 bool anchorValid, wasScene;
 float x,y,z;
 uint64_t nextSceneMS;
 _Atomic uint64_t permitUntilMS;
} PGDistanceStreaming;
static inline void pg_distance_sample(PGDistanceStreaming *s,uint64_t now,bool valid,float x,float y,float z,bool scene){
 if(scene){
  if(!s->wasScene||now>=s->nextSceneMS){atomic_store(&s->permitUntilMS,now+2000);s->nextSceneMS=now+1000;}
  s->anchorValid=false;
 }else if(valid&&isfinite(x)&&isfinite(y)&&isfinite(z)){
  if(s->anchorValid){
   double dx=(double)x-s->x,dy=(double)y-s->y,dz=(double)z-s->z;
   if(dx*dx+dy*dy+dz*dz>=160.0*160.0){
    atomic_store(&s->permitUntilMS,now+2000);s->x=x;s->y=y;s->z=z;
   }
  }else{s->anchorValid=true;s->x=x;s->y=y;s->z=z;}
 }
 s->wasScene=scene;
}
static inline int64_t pg_distance_budget(PGDistanceStreaming *s,uint64_t now,int64_t engine,uint64_t available){
 // Preserve the engine's own signed budget and object-lifetime rules.
 if(engine<0)return engine;
 int64_t result=(uint64_t)engine<available?engine:(available>INT64_MAX?INT64_MAX:(int64_t)available);
 if(available>=(256ull<<20))return result;
 uint64_t until=atomic_load(&s->permitUntilMS);
 if(until&&now<=until&&atomic_compare_exchange_strong(&s->permitUntilMS,&until,0)){
  // One bounded request per permit, not thousands per streaming poll.
  uint64_t deficit=(256ull<<20)-available;
  return -(int64_t)(deficit<(16ull<<20)?deficit:(16ull<<20));
 }
 return result;
}
