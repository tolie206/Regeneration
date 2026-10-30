#pragma once
#include <array>
#include <mutex>
#include <cstdint>
struct PGRenderStamp {uint64_t frame=0,serial=0;uint32_t kind=0,phase=0;double cpuMs=0,gpuStartMs=0,gpuEndMs=0;};
class PGRenderTimeline {
 std::array<PGRenderStamp,1024> records{};size_t next=0,count=0;uint64_t overwritten=0;std::mutex lock;
public:
 void add(PGRenderStamp value){std::lock_guard<std::mutex> guard(lock);records[next]=value;next=(next+1)%records.size();if(count<records.size())count++;else overwritten++;}
 size_t drain(std::array<PGRenderStamp,1024>& out,uint64_t& dropped){std::lock_guard<std::mutex> guard(lock);size_t first=(next+records.size()-count)%records.size();for(size_t i=0;i<count;i++)out[i]=records[(first+i)%records.size()];size_t n=count;count=0;dropped=overwritten;overwritten=0;return n;}
};
