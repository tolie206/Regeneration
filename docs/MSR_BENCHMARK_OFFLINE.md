# V5R1 benchmark status
Device FPS/1%low/thermal/image quality: NOT MEASURED; no iPhone attached for automated gameplay.
Local performance reporting is opt-in, offline, one aggregate per15seconds of active world rendering. Median/P95/P99 use ceil-millisecond histograms (approximate). 1%low is1000 / mean of worst1% actual intervals, capped8192 samples/window; coverage is logged. Pipeline, upload, GPU-wait and submit counters reuse existing renderer work timings. These are not complete simulation or streaming-decode CPU costs.

Tester matrix: R008 then V5 Off/Quality/Balanced/Performance, same 900p output; Sandy Shores stationary pan and fast driving, city, mission/cutscene, death/reload, pause/map return, stock vehicle takeover and mod vehicle. Run20minutes for heat/memory. Compare max/P95/P99,1%low and frame stalls, not just FPS. Reject visual corruption, missing map, gamma changes, unusable HUD or crashes. Rollback to unchanged R008 branch if regression.

CI: V5 pushes run validation first. The single reusable IPA workflow starts only after validation succeeds and checks out the exact tested github.sha. It repeats device-SDK preflight before the expensive engine build. No parallel manual IPA dispatch is needed.
