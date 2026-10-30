#include "NativeQueryPolicy.h"
#include "NativeRenderTimeline.h"
#include <cassert>
#include <thread>
#include <vector>
#include <memory>
int main(){
 for(unsigned type=0;type<6;type++)for(unsigned bits=0;bits<8;bits++)for(unsigned completed=0;completed<8;completed++){
  bool result=pg_completed_event_fast(type,bits&1,bits&2,bits&4,completed,4);
  assert(result==((type==0||type==2)&&bits==0&&completed>=4));
 }
 assert(pg_query_batch_ms(-1)==0&&pg_query_batch_ms(2)==0&&pg_query_batch_ms(.25)==.25);
 assert(pg_query_wait_ns(false,0,0)==100000000);
 assert(pg_query_wait_ns(true,.25,.1)>=149999&&pg_query_wait_ns(true,.25,.1)<=150001);assert(pg_query_wait_ns(true,.25,.3)==1000);
 // Deterministic reproduction of the old shared-buffer reuse hazard.
 auto old=std::make_shared<std::vector<unsigned long long>>(8,0);(*old)[0]=42;
 auto oldReader=[old](){return (*old)[0];};(*old)[0]=0;assert(oldReader()!=42);
 (*old)[0]=42;auto current=std::make_shared<std::vector<unsigned long long>>(8,0);assert(oldReader()==42&&(*current)[0]==0);
 PGRenderTimeline trace;std::vector<std::thread> workers;
 for(unsigned t=0;t<8;t++)workers.emplace_back([&trace,t](){for(unsigned n=0;n<1000;n++)trace.add({t,n,0,2,(double)n,1,2});});
 for(auto& t:workers)t.join();std::array<PGRenderStamp,1024> out;uint64_t dropped=0;auto count=trace.drain(out,dropped);
 assert(count==1024&&dropped==8000-1024);for(size_t i=0;i<count;i++)assert(out[i].frame<8&&out[i].serial<1000&&out[i].gpuEndMs==2);
 assert(trace.drain(out,dropped)==0&&dropped==0);
}
