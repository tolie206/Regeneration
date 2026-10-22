# MuLone-V002

## Evidence from four supplied phone logs
- All three MuLone sessions mounted SH150 but failed its YFT streaming dependency. Its original vehicles.meta references vehicles_biker_shared. That texture dictionary is absent from the pinned game manifest. This is a concrete missing dependency; phone retest is still required after remapping it.
- SH150 also ships newer vehiclelayouts flags and a liveries array of 8 where this engine expects 30. Those parser diagnostics remain; no blanket metadata stripping or mission bypass was introduced.
- MuLone sessions used 1170x540 uncapped or 1560x720 at 60; the original used 1950x900 at 60, different positions and different vehicle packs. MuLone log 3 records thermal serious and 34 FPS, with roughly 2 GB available and no memory-guard evictions. The original also reports thermal serious. These runs do not isolate a renderer regression.
- MuLone uncapped sessions report 79–120 FPS and progress to thermal serious. For sustained testing use the same 60 FPS cap, graphics, route, mods and initial phone temperature. No promise of a measured FPS uplift from these source changes.

## Changes
- Sound selection lists enabled imported vehicle model names from actual vehicles.meta, without typing. Catalog refreshed before startup; restart after adding a vehicle.
- Before engine startup inspect mod metadata and texture names. When the confirmed absent vehicles_biker_shared dependency is required, point it to existing vehshare. Leave other unknown parents unchanged and report them.
- Rewrite only the outer RPF metadata entry by appending an uncompressed replacement. Nested RPF/model/texture bytes stay intact. Hidden .dlc.rpf.mulone-original backup allows restoring the original pack. No base game/save writes.
- Sample verbose model suspension and streaming queue diagnostic logs after 16 lines, with aggregate counts. Error, health and renderer reports remain available.
- Renderer, shader cache, audio mixer, graphics presets and saved preferences unchanged.

## Validation
Local translation checks passed. CI tests exercise missing-parent repair, unchanged nested RPF bytes, original backup, idempotence, vehicle catalog and existing H2R sound importer. Release IPA requires phone testing of SH150, assigned sound, and an equal-settings performance comparison. No phone gameplay verification on the build host.
