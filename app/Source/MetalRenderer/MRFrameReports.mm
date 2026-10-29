// Optional local-only performance aggregates, once per 15 seconds; off by default.
#include "MRFrameReports.h"
#include "NativeFrameMetrics.h"

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <UIKit/UIKit.h>
#include <TargetConditionals.h>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mach/mach.h>
#include <os/proc.h>

extern "C" void pg_log(const char *);

namespace mr {
static bool enabled;
static PGFrameMetricsWindow window;
static double windowStart;

static std::atomic<bool> inFlight{false}, resetPending{false}, applicationActive{true};


static id<MTLDevice> device;



// Local-only diagnostics. A bounded snapshot is formatted on a utility queue;
// no server request, per-frame allocation or GPU readback is introduced.
static void enqueue(PGFrameMetricsSnapshot stats) {
 bool expected=false;if(!inFlight.compare_exchange_strong(expected,true))return;
 dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY,0),^{@autoreleasepool{
  task_vm_info_data_t memory={};mach_msg_type_number_t count=TASK_VM_INFO_COUNT;
  bool known=task_info(mach_task_self(),TASK_VM_INFO,(task_info_t)&memory,&count)==KERN_SUCCESS;
  char line[1024];double frames=(double)stats.frames;
  snprintf(line,sizeof line,"OfflinePerf frames=%llu fps=%.2f p50CeilMs=%.2f p95CeilMs=%.2f p99CeilMs=%.2f low1Fps=%.2f low1Samples=%llu maxMs=%.2f over16=%llu over33=%llu over50=%llu over100=%llu pipeMs=%.3f uploadMs=%.3f gpuWaitMs=%.3f submitMs=%.3f footprintMB=%.1f metalMB=%.1f thermal=%ld",
   (unsigned long long)stats.frames,stats.fps(),stats.p50Ms,stats.p95Ms,stats.p99Ms,stats.onePercentLow,(unsigned long long)std::min<uint64_t>(stats.frames,8192),stats.maxMs,
   (unsigned long long)stats.over16,(unsigned long long)stats.over33,(unsigned long long)stats.over50,(unsigned long long)stats.over100,
   stats.work.pipeline/frames,stats.work.uploads/frames,stats.work.gpuWait/frames,stats.work.submit/frames,
   known?memory.phys_footprint/1048576.0:-1,device?device.currentAllocatedSize/1048576.0:0,(long)NSProcessInfo.processInfo.thermalState);
  pg_log(line);inFlight.store(false);
 }});
}

void frameReportsInstall(id<MTLDevice> metalDevice) {
	device = metalDevice;
	const char *local=getenv("PG_PERF_LOCAL");
	enabled = (local&&strcmp(local,"1")==0) || [NSProcessInfo.processInfo.arguments containsObject:@"--frame-reports"];
	if (!enabled) { pg_log("Frame reports disabled."); return; }
	dispatch_async(dispatch_get_main_queue(), ^{
		[NSNotificationCenter.defaultCenter addObserverForName:UIApplicationWillResignActiveNotification object:nil queue:nil usingBlock:^(NSNotification *) { applicationActive.store(false); resetPending.store(true); }];
		[NSNotificationCenter.defaultCenter addObserverForName:UIApplicationDidBecomeActiveNotification object:nil queue:nil usingBlock:^(NSNotification *) { resetPending.store(true); applicationActive.store(true); }];
	});
	pg_log("Local frame reports enabled: bounded aggregates every 15 seconds of active world rendering.");
}

void frameReportsRecord(double timeMs, double frameMs, uint64_t draws, bool world, const FrameWork &w) {
	if (!enabled) return;
	if (resetPending.exchange(false)) { window.reset(); windowStart = 0; return; }
	if (!applicationActive.load() || !world || draws < 100) return;
	PGFrameWork work{w.idle, w.pipeline, 0, w.uploads, w.uploadBytes, w.gpuWait, w.submit};
	if (!window.record(frameMs, draws, work)) return;
	if (!windowStart) windowStart = timeMs;
	if (timeMs - windowStart >= 15000) { enqueue(window.snapshot()); window.reset(); windowStart = timeMs; }
}
}  // namespace mr
