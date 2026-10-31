# FIX6 — latest FPS and body visibility regression

Input: C:/Users/Admin/Desktop/native-port (1).log, FIX5 iOS18.6.1. MSR Quality1044x482 ->1560x720, FXAA on, color filter requested1/effective1.

## FPS: evidence vs inference
16periodic health samples: nominal3median60FPS/reported GPU-total8.3ms; fair3median60FPS/11.8ms; serious10median48.5FPS/19.3ms. Scene workload and heat both change, so these medians do not isolate thermal throttling or a filter regression. No core-frequency measurement or matched filter-off A/B is present.

At line17083,42FPS coincides with1421streamed assets/133.8MBread/2.60CPUcores. Storage averages0.5ms with0slow/errors; streaming CPU/decode/upload/visibility work is a plausible contributor, not a confirmed slow-storage fault. Later30–39FPS samples have thermal serious and roughly1.4–1.5GB process allowance remaining, guard0growth-stops/0evictions and0streaming waiters. Repeated readback-wait counters0. This does not support blaming RAM guard or GPU readback stalls. Main-thread profiles show visibility/rasterizer waits; render profiles show main-thread waits plus shadow/gbuffer work. CPU/GPU scheduling and scene work warrant targeted profiling; percentages of engine event samples are not direct GPU cost percentages.

Shader creation still contributes transiently: startup928pipeline-wait skips and longest1647ms gap, plus isolated later10/347pipeline-wait skips. The startup interval includes loading, so the entire gap cannot be attributed to shader compilation. Sustained35–43FPS also occurs with0pipeline-wait skips; shader cache is not a complete remedy. At38.8FPS,26frames exceed50ms with longest76ms. Body skip count stays7384 across30/35/39FPS intervals: active suppression is not required for the observed drop.

No speculative graphics/memory/streaming changes shipped in this fix. Filter is demonstrably active, but its FPS cost is not isolated. Same-scene/same-thermal/resolution A/B required to quantify it.

## Body root cause and correction
FIX5 assumed GetVehiclePedIsIn(ped,false) implied currently seated. Actual pinned function57184 reads CPed+5576 directly and can return a retained last-vehicle pointer without checking the in-vehicle flag. Separate IsPedInAnyVehicle(ped,false), function57118, checks CPed+5291 bit64 and nonnull vehicle; false explicitly excludes entering tasks. This was absent from the mock and previous gate.

Add strict live occupancy validation at draw submission, not only on script tick. Recheck local ped identity, current vehicle, bike model, gameplay camera, and vehicle follow-camera view mode4. Remove the generic on-foot/aim/first-person query from the bike rule; the vehicle camera has its own context. Vehicle view getter49065 delegates to GetViewModeForContext(1), matching the vehicle mode setter used by our own camera toggle. The supplied log has no camera-state trace to prove that the old generic query alone caused the bike failure; selecting the specific context removes that ambiguity.

Script tick now caches identity only; it never caches a true hide decision across dismounts. Render predicate independently excludes walking even if the old bike handle remains nonzero, rejects car/thirdperson/cutscene/invalidped immediately before the next tick, and accepts bike vehicle-view4 without requiring the generic first-person predicate. Original render submission remains unchanged whenever the guard fails. Whole-body/hands/shadow tradeoff and user toggle remain as disclosed in FIX5. No entity/material/network mutations.

Health line gains reason code:1identity,2not seated,3no vehicle,4not motorcycle,5vehicle view not4,6pause/load/non-gameplay,7actual draw skipped;0off/no candidate. This is bounded to the existing periodic line.

New runtime tests reproduce on-foot+remembered bike, generic FP query false in vehicle, and dismount/car/camera/player transitions between script ticks. Real device visibility and FPS acceptance still pending. Optimizer, audio, filter shader math, FOV output and streaming behavior unchanged except release labels and diagnostics. FIX5 commit69742bc remains rollback point.
