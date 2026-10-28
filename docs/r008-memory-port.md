# R008: verified, limited memory port from 1.5.1

Base: R007 b5b0d53d3d7440378b21ecc6f9f1a9916b629154. Isolated branch regeneration-r008-native-reclaim; original R007 IPA and source retained.

## Evidence
Audited original 1.5.1 IPA SHA256 046ea27038e9804f13569accee3bcb88506cb383658c8ba30849b545d53ddbfe (unencrypted ARM64, local symbols). Direct calls show lazy creation in CreateBuffer/CreateTexture1D/2D/3D and materialization in Map/CopySubresourceRegion/GpuReadback/CopyResource/UpdateSubresource.

Two E:/log gray r007 logs both report process limit 2348 MiB and reserve 128 MiB. A14 has late headroom 95-109 MiB, 1841-3664 growth clamps per health interval and 187 cumulative host reclaim events. A15 has 125-141 MiB, 2359-3521 clamps per interval and 54 reclaim events. Both report serious thermal state; native budget reaches 2097151 KiB. Pressure and throttling are confirmed; these logs cannot prove every grey object has the same cause, or that either session ended in jetsam. Mod texture-parent warnings remain independent.

1.5.1 comparison logs have zero host clamps/reclaims with >1 GiB headroom; their different device, route and thermal state do not establish a controlled FPS comparison.

## Implementation
Defer ONLY zero-initialized CPU shadow storage until a CPU operation needs it. Preserve initial-data resources and all GPU resources. Register four verified vtable/field layouts, bounds-check memory, materialize once under a lock, refresh memory after guest calloc, maintain original guest allocation counters for its destructors. Both source and destination are covered. No hook on draw/frame loops. Statistics are emitted only alongside existing memory-pool reports and are explicitly cumulative, not a claim of current bytes saved. PG_LAZY_CPU_COPIES=0 restores eager allocation at launch for A/B debugging.

Existing R007 reserve/distance settings, mesh renderer, Metal shaders, texture resolution, skins and audio remain unchanged; the additional confirmed vehicle mount/spawn fixes are described below. No world object deletion is added.

## Scope
1.5.1 also has a separate protected-page mesh source release/restore system, including GPU mirrors, I/O touch hooks and SIGBUS/SIGSEGV restoration. It is NOT reproduced incompletely: R007 has its own ASI fault handler and blindly discarding those live pages can corrupt game or mods. R007 already returns buddy-allocator blocks freed by the engine to iOS. This release ports deferred CPU shadows, not the whole 1.5.1 runtime.

## Validation
Pinned-engine fixture patch checks, idempotence, fail-closed changed layouts, four destructors checking nonnull, host baseline preservation. Runtime test covers four layouts, initial payload fallback, bounds, unknown interfaces, repeated reads, concurrent materialization, counters, allocation failure and disabled mode. macOS CI runs actual implementation with ASAN/UBSAN before building the iOS Release. iPhone visual correctness, actual memory reduction, FPS and 20-minute stability still require on-device tester confirmation. No performance improvement is claimed from host unit tests alone.

## Rollback
Reinstall E:/New Project/Builds/Mugoat-NewGen-Regeneration-R007.ipa or build unchanged regeneration-r007-reserve-profiles at b5b0d53. Do not replace the current MuZom checkout.

## Vehicle regressions added after tester logs
E:/log không gọi được xe/native-port (1).log records two successful launcher spawns (vario150, NEMESIS), then yadi_x5_1_cpgta REQUEST_MODEL followed by status 8 (LowMemory). The active distance reserve is 144 MiB, but launcher code still checked legacy guardReserve (256 MiB on this process). Fix: use distanceStreaming.reserveBytes when that policy is enabled, otherwise retain legacy guardReserve; report rejection threshold once. Regression reproduces 258 -> 200 MiB during loading, verifies success above 144 MiB, rejection below 144 MiB, and unchanged legacy mode. This fixes a confirmed cancellation path; it does not prove all other vehicle failures have the same cause.

E:/mod xe contains SH150, Vision and 27rev. All nested resource payloads independently inflated successfully; YFT version162 and YTD13. SH150 content.xml references nonexistent VEHICLE_mods.rpf while the actual sibling is sh150_mods.rpf. Preboot metadata repair now resolves this specific generic placeholder only when exactly one *_mods.rpf exists in the same directory, with backup, idempotence and byte-identical nested archives. Ambiguous/unknown references remain unchanged.

CI tests production unpack/plan/install/prepare, metadata XML, picker model names, actual complete YFT/YTD payloads, mount repair, idempotence, geometry byte identity and actual model hashes passed through the native spawn command simulation. These do not prove visible iPhone spawns. User explicitly authorized publishing the 29 MB 27rev sample and building the public repository on 2026-10-28.
