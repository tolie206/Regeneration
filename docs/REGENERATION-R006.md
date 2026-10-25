# R006 — distance-based host streaming policy

Base R005 e4f87a6; separate branch regeneration-r006-distance-streaming. R005 and main preserved.

## Evidence
New log: C:/Users/Admin/Downloads/new gray log/native-port.log, R005, Apple A15/iPhone14,5 (log identifier is not iPhone12), process limit2098 MiB, increased-memory-limit not granted. Battery preset540p, automatic texture budget640 MiB, four addon packs. Free241–474 MiB; thousands of host budget clamps/negative answers per health interval, zero Metal texture create/decode failures. Thermal fair, so this recording does not establish overheating as the main cause. Last syscall/read errors0. Native cache/object lifetime remains a distinct cause to diagnose.

Old unloaded metric was RemoveObject entry calls, including no-op calls for already-unloaded objects; NOT proof of millions of actual unloads. Skip NOT_LOADED callbacks before taking diagnostic lock and label remaining metric remove calls. Checked pinned RemoveObject6056 and cache functions9976/9977 in original wasm; unmodified game.wasm.

## Implementation
Default enabled setting RAM -> Thu hồi theo di chuyển. Disabled restores R005 pressure policy at next boot.
- System-memory host query uses actual process/engine headroom with no fixed reserve/band in this mode. Does not allocate artificial filler RAM or grant an iOS entitlement.
- Read-only player position sampling every250ms on existing main script tick, no extra worker/native script calls.
- Host-forced reclamation only receives a single-use2-second permit after160m from last anchor or an active engine load scene (scene permits at most once/sec).
- A permit can request at most16MiB and only if headroom<256MiB. No repeated requests for stationary allocation polls.
- Does not pin every texture forever: engine cache budgets, reference counts, normal obsolete-asset retirement, heap/address-space refusal remain authoritative. Negative native cache budget is preserved. Not a promise that only distant objects can ever be removed; selecting safe objects remains the engine's job.
- Health log reports native budget, effective headroom and cumulative host-forced reclamations every10s. No per-frame verbose logging.
- No renderer/shader, render-height/texture-quality or heap-size changes. Drive-by and all previous mod/skin/audio changes preserved.

## Verification scope
Production header with ASAN/UBSAN: stationary,159/160m, one million repeated allocation polls, permit expiry, invalid coordinates, active scenes, native negative budgets, zero headroom and engine ceiling. Production streaming-health test excludes one million no-op removal calls. Previous full mod/skin/audio/resource32/input tests retained. Host tests do not establish iPhone appearance/frame-time or absence of jetsam. Compare R005/R006 with identical mods/settings on the same route, pause-map-return, respawn and20-minute session. Send new log if grey materials remain; distinguish native budget depletion from host-forced reclamation via new diagnostic.

## Apple references
https://developer.apple.com/documentation/os/os_proc_available_memory
https://developer.apple.com/documentation/metal/reducing-the-memory-footprint-of-metal-apps
https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports
Apple documents that available headroom is bytes before the process limit, not an allocation guarantee; Metal and CPU share app memory and iOS can terminate on excessive use. Hence no claim that unlimited texture retention is stable.
