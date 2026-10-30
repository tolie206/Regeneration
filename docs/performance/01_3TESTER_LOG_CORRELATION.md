# Raw-log verification (local files, aggregated output only)
All three supplied raw logs were read, including newly added A15 `native-port-previous (1).log`. Reproducible extraction: `python tools/analyze_v5_fix_logs.py <local-log-directory> --index <local-shader-index>`. Results: log_summary.json, renderer_windows.csv, missing_shaders.csv. These tables are observations, not a clean gameplay benchmark.

| Chip/file | Lines | Renderer windows | Missing tuples | GPU-version warnings |
|---|---:|---:|---:|---:|
| A13 native-port(2).log | 25505 | 29 | 45 | 80 |
| A15 native-port-previous (1).log | 19670 | 16 | 45 | 48 |
| A16 native-port(3).log | 17094 | 9 | 45 | 47 |

Verified examples: A13 line25103 24.3fps/800 draws/21.2 CB, next line18.1 idle +2.0 readback. A15 line18147 37.4fps/1813 draws/20.9 CB, next line15.8 idle +4.1 readback; line19174 28.1fps/1954 draws/21.3 CB and16.5 idle. A16 line16989 44.8fps/3055 draws/28.7 CB, next line23.6 idle +4.1 readback. A15 line19504 62.5fps with0.1 idle CB then line19552 30.9fps with14.7 idle CB. This association is strong enough to investigate submission but does NOT prove that batching improves either scene.

The 45 hash/stage sets are identical, each warning occurs once/log. All hashes are absent from the available 4808-entry shader index; effect/pass names cannot be recovered from that index. They are not 45 confirmed compilation stalls. New optional binding diagnostics distinguish requested but unused shaders from actual skipped draws.

A16 OfflinePerf line16988: fps44.52, low1=20.92, p99CeilMs34. A15 line19622: fps33.27, low1=16.48, p99CeilMs50. These are distinct windows, not a merged score. A13 cap2348MB with roughly257MB headroom and serious thermal pressure late in log. A15/A16 cap4096MB. Displayed physical RAM uses truncated GiB; it does not mean an advertised6GB device has5GB hardware.

Startup, pause, background/resume and loading windows are not automatically classified as gameplay in renderer_windows.csv. No whole-log FPS average is reported. Profiler percentages are sample shares, not per-frame milliseconds. CPU renderer-busy and GPU total durations have different windows. Audio waits near lifecycle transitions are analyzed separately from sustained gameplay. No device-to-device ranking is valid because resolution, scene, caps, mods/Menyoo and thermal state differ.
