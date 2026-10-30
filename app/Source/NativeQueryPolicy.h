#pragma once
#include <stdint.h>
#include <cmath>
static inline bool pg_completed_event_fast(uint32_t type,bool hasCommands,bool hasCallbacks,bool hasQueries,uint64_t completed,uint64_t submitted){
 return type==0&&!hasCommands&&!hasCallbacks&&!hasQueries&&completed>=submitted;
}
static inline double pg_query_batch_ms(double requested){return requested>=0&&requested<=1?requested:0;}
static inline int64_t pg_query_wait_ns(bool waiting,double batchMs,double elapsedMs){
 if(!waiting)return 100000000;
 if(!std::isfinite(elapsedMs))return 1000;
 double remaining=(pg_query_batch_ms(batchMs)-elapsedMs)*1000000;
 if(remaining>1000000)remaining=1000000;
 return (int64_t)(remaining>1000?std::ceil(remaining):1000);
}
