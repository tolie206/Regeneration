#include "NativeFrameMetrics.h"
#include <cassert>
int main(){PGFrameMetricsWindow w;PGFrameWork work;
assert(!w.record(0,200,work));assert(!w.record(NAN,200,work));
for(int i=0;i<99;i++)assert(w.record(10,200,work));w.record(100,200,work);
auto s=w.snapshot();assert(s.frames==100&&s.p50Ms==10&&s.p95Ms==10&&s.p99Ms==10&&s.onePercentLow==10&&s.over16==1);
w.reset();assert(w.sampleCount==0&&w.snapshot().frames==0);
for(int i=0;i<9000;i++)w.record(20,200,work);s=w.snapshot();assert(w.sampleCount==8192&&s.frames==9000&&s.onePercentLow==50);}
