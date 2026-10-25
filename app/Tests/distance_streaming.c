#include "../Source/NativeDistanceStreaming.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 const uint64_t M=1ull<<20;PGDistanceStreaming s={0};
 pg_distance_sample(&s,1000,true,0,0,0,false);
 for(unsigned t=1001;t<5000;t++){
  pg_distance_sample(&s,t,true,20,0,0,false);
  assert(pg_distance_budget(&s,t,1024*M,270*M)==270*M);
  assert(pg_distance_budget(&s,t,1024*M,1*M)==1*M);
 }
 pg_distance_sample(&s,5000,true,159,0,0,false);
 assert(pg_distance_budget(&s,5000,1024*M,100*M)==100*M);
 pg_distance_sample(&s,6000,true,160,0,0,false);
 assert(pg_distance_budget(&s,6000,1024*M,100*M)==-(int64_t)(16*M));
 for(unsigned n=0;n<1000000;n++)assert(pg_distance_budget(&s,6001,1024*M,100*M)==100*M);
 // Expired permits cannot trigger late eviction while standing in the new area.
 pg_distance_sample(&s,9000,true,320,0,0,false);
 assert(pg_distance_budget(&s,11001,1024*M,100*M)==100*M);
 // Pause/invalid position/NaN cannot invent a movement permit.
 pg_distance_sample(&s,12000,false,10000,0,0,false);
 pg_distance_sample(&s,13000,true,NAN,0,0,false);
 assert(pg_distance_budget(&s,13000,1024*M,100*M)==100*M);
 // Scene grants at most one slice per second, not per allocation query.
 pg_distance_sample(&s,14000,false,0,0,0,true);
 assert(pg_distance_budget(&s,14000,1024*M,100*M)==-(int64_t)(16*M));
 pg_distance_sample(&s,14250,false,0,0,0,true);
 assert(pg_distance_budget(&s,14250,1024*M,100*M)==100*M);
 pg_distance_sample(&s,15000,false,0,0,0,true);
 assert(pg_distance_budget(&s,15000,1024*M,250*M)==-(int64_t)(6*M));
 // No forged success: preserve native negative budget, low-memory and address-space limits.
 assert(pg_distance_budget(&s,16000,-(int64_t)(20*M),100*M)==-(int64_t)(20*M));
 assert(pg_distance_budget(&s,16000,4*M,100*M)==4*M);
 assert(pg_distance_budget(&s,16000,4*M,0)==0);
 assert(pg_distance_budget(&s,16000,0,100*M)==0);
 puts("PASS distance policy: stationary residency, 160m, bounded cleanup, no poll storm, transitions, invalid coords, native limits");
}
