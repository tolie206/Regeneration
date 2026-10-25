# R007 — small reserve profiles and earlier distance cleanup

Base a9b29f8 (R006), independent branch regeneration-r007-reserve-profiles. R006 IPA/source kept for rollback.

## Logs and limits of evidence
Provided 1-native-port.log: A13, iPhone12,1, actual process limit2348 MiB, increased entitlement true,720p Lite/unlimited, Menyoo on, texture budget384 MiB.93 health samples (~15.5 minutes if regular10-second sampling): headroom527 ->12 MiB, median249,18 samples below128 MiB. Largest sampled decrease83 MiB in this log; the shorter second log has a122 MiB decrease. No native trap/fault recorded. This strongly supports memory-pressure risk at long-session end, but a jetsam report is still needed to prove iOS termination. Do not generalize this one device log as a diagnosis of every tester's crash.
Second log:10 health samples, free605 ->390 MiB, app backgrounds at end; no recorded native crash. Both show serious thermal state later. No renderer changes based on speculation; native heap physical pools and GPU texture/mesh working sets grow during travel, not proof of a leak.

Old thresholds: R002–R004 reserve384 MiB plus growth band256(normal)/64(Lite); R005 reserve256 on process limits<=2560 MiB,384 otherwise, same bands. R006 distance mode reserve0, no growth band. These are budgeting thresholds, not physically allocated empty RAM.

## New settings
RAM and memory rights -> distance mode:
- Automatic (default): <=4 GB hardware128 MiB;6–<8 GB192 MiB;>=8 GB256 MiB. Eight GB belongs to the upper group. Hardware bins allow for usable physical memory reported below nominal capacity.
- Manual profile options plus0 MiB opt-out.
- Requested reserve is capped to about1/16 of actual process quota, rounded down16 MiB (e.g.256 request/2098 quota =>128). Actual reserve logged at boot; manual app cap also respected.
- Distance default80m (half R006160m); selectable40/60/80/120/160m.

128 MiB is a starting reserve near the largest observed10-second headroom drop122 MiB, not a guarantee against larger unobserved bursts.192/256 provide more room on higher quotas without returning to384+256 legacy thresholds. New mode subtracts reserve only, no old growth band: free265 MiB with128 reserve still offers137 MiB for growth, whereas old256+64 blocked it.

Reclamation stays16 MiB per request. Movement/scene permit is single use; critical headroom below half reserve can reclaim even while stationary, with500ms cooldown (max2 host requests/sec). Emergency exception is needed to avoid waiting for80m when only12 MiB remains; it is shown in UI. Native cache negative budgets/refcounts/heap refusals remain authoritative. Does not force-unload visible map, fake asset loading, alter quality or raise app entitlement.

## Tests required before IPA
Original input/audio/vehicle/skin/cache/translation tests retained. Production policy tested with3 profiles, default80m vs79m,1 million repeated polls, emergency recovery/cooldown, native negative budgets,0-reserve opt-out and quota caps. Production Swift tested for defaults/migration/hardware bins/options/env exports/invalid values. Actual host bridge replays93 observed headroom samples arithmetically; this is not a runtime memory simulation and proves no iPhone FPS or visual outcome. Renderer/shader/turbo baseline hash gate retained with explicitly reviewed R007 hunks.

A real15–20 minute device test remains necessary to verify no grey-texture regression and whether long-session terminations are reduced. No host test can guarantee both for all devices.
