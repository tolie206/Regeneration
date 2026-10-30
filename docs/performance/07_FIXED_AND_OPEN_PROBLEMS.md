# Retained changes and limits
Implemented: safe visibility-buffer epochs, move capture instead of query-list copy, completed-EVENT fastpath, bounded query/submit diagnostics, optional bounded query batch deadline, speculative-only A/B, active/non-interrupted audio retry guard, optional final-pass FXAA, targeted CI and generated-C compiler cache, release identity V5R1-FIX.

Not proven fixed: total FPS drop, PVS/critical entity scans, guest audio semaphore stalls, cloth GPU-version warnings, absent shader pass coverage, thermal throttling, launcher contribution, full input latency. See all25 dispositions in03; none are silently counted as resolved.

No new memory reclamation, global graphics downgrade, mod/save change or comparison binary injection. FXAA may blur HUD and lower FPS; MSAA not added because arbitrary sample-count changes require renderer/resolve/shader compatibility and testing. No measured performance claims. No experiment was rolled back after a device test because no device test was possible; risky speculative/batch/FXAA paths are opt-in.
