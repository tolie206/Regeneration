# Before / after
| Device | Before: observed isolated log window | FIX after |
|---|---|---|
| A13 | 24.3fps,21.2CB/frame,18.1idle | NOT MEASURED / NOT DEVICE TESTED |
| A15 | 28.1fps,21.3CB/frame,16.5idle | NOT MEASURED / NOT DEVICE TESTED |
| A16 | 44.8fps,28.7CB/frame,23.6idle; nearby p99 ceiling34ms | NOT MEASURED / NOT DEVICE TESTED |

Do not interpret this as a controlled baseline. Test A/B/A on the SAME phone, save, route, camera, mod set, resolution/internal scale, cap and thermal state. Begin after warmup, record at least3x90s city and desert routes plus stationary camera rotation. Separate cold loads, pauses and background intervals. Report p50/p95/p99,1%low, >50/>100ms hitches, query counts, command buffers, GPU times, footprint and thermal. No stable60fps claim if p99>16.67ms.

First A: FIX defaults (batch0, FXAAoff, speculationnormal, traceoff). B: change exactly one option, restart app; A again. First compare completed-EVENT fastpath ON/OFF. Then try batch.25ms only; revert if p99, drawing, latency or missions worsen. FXAA OFF/ON is a quality/cost experiment, not an FPS optimization. Instrumentation OFF/ON overhead is unmeasured; do not leave trace on during final scoring. Abort/rollback if geometry disappears, audio breaks or memory rises persistently.
