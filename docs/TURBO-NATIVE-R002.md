# Turbo / backfire native — experimental R002, build 1011

This is an original, opt-in implementation for the pinned native iOS engine,
not execution of the owner's Windows TurboFix.asi. The regeneration memory,
renderer, asset reclamation and streaming policies are unchanged. The stable
R001 build remains separately available. Never describe this as a verified
complete port of every TurboFix feature.

## Implemented for testing

- Player-driven vehicle only, with an actual turbo upgrade. Optional install
  on entering the vehicle; that upgrade remains installed when the feature
  is switched off. Passenger/NPC vehicles retain their stock behavior.
- Turbo spool/unspool, off-throttle vacuum, high-RPM falloff, ten gear limits
  and anti-lag. Smoothing uses elapsed seconds, independent of frame rate.
- Native `core/veh_backfire` effects at existing exhaust bones, up to four
  exhausts per burst. Missing bones produce no invented center-of-car flame.
- The owner's 46 PCM WAV files in three selectable sets, including the
  supplied credits. Existing filenames are enumerated; the missing
  `Default/EX_POP_34.wav` cannot be selected accidentally. Native iOS audio
  reuses prepared players, with at most four pop and three bass voices.
- Anti-lag interval/randomness, loud-burst spacing, volume and all turbo
  parameters adjustable in Vietnamese through Settings → Turbo và lửa bô.
- Optional on-screen boost/RPM/gear readout at 4 Hz. This is an engine boost
  value, not a calibrated bar/PSI reading or DashHook vehicle dial.

All switches and numbers are persisted. Master defaults OFF. To test, turn
on the master and optional turbo installation, enter a supported car, rev it
above the anti-lag RPM threshold and release the accelerator. Native turbo
updates require the stock transmission's turbo branch to execute. A car
using a separate CVT/unsupported drivetrain path may show no telemetry.

## Deliberate limits and remaining work

- The original ASI's executable scanning, boost-limiter machine-code patch,
  Windows DLL imports, F10 menu and exports to other PC plugins are not used.
- DashHook, original gauge offsets/scales, automatic model/plate INI preset
  selection, NPC management and tuned-exhaust matrix overrides have not
  been ported. Current settings are one global profile for the driven car.
- The supplied `default.ini` has BoostByGear enabled with 14,384 numeric
  entries all zero. It is not imported blindly: gear caps default to one,
  gear limiting defaults off. Only ten actual gears are configurable.
- The supplied 50 ms FX interval is raised to a minimum 100 ms for this
  implementation. At most ten bursts/second, at most four exhausts/burst,
  no catch-up on resume. Missing particle assets retry at most ten times.
- Sound uses local player audio, not the original irrKlang 3D engine. No
  audio session category, engine mixer or streaming budget is reconfigured.
- Exhaust bone fallback may differ from a vehicle's tuned exhaust outlets.
  Flame alignment, audibility, handling and frame-time cost still require
  on-device validation, particularly on 4 GB iPhones.

## Verification

- C math tests: 30 vs 120 Hz, vacuum, anti-lag, reverse/high gears and input
  validation. C bridge tests: disabled/other-vehicle passthrough, driver
  gating, telemetry, correct exhaust/native arguments, independent audio,
  cooldown, bounded asset retries, pause and balanced script context.
- Python tests check every bundled WAV hash/PCM header and fail-closed,
  idempotent engine patch behavior. Existing translation/release tests run.
- Build preparation resolves the transmission by its exact name and checks
  the exact boost-store anchor. A changed engine stops the build.
- These are host-side and build checks; they do not prove a flame rendered
  or a sample was audible on an iPhone. There is no connected iPhone test
  device in this workspace.

Reference inspected: public TurboFix fork commit
`8e78045e9907029881bd0ea2026aedf4bb3e41b1`; no source license was found, so
its implementation was not vendored. The owner's original files remain
unchanged at `C:\Users\SongLam\Downloads\TurboFix`.
