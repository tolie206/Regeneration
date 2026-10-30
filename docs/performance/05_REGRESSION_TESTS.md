# Targeted verification
Local Windows checks: release metadata5.1.1/5002 and core-preservation unittest PASS. Aggregate parser confirms all3 log sets/45 tuples; missing input inventory is reproducible. Windows cannot execute Metal/iOS binaries.

FIX CI checks (status in GitHub run, not claimed passed here before execution):
- Existing positive/negative sanitizer controls on macOS host.
- ASan/UBSan C++ query eligibility, bounded wait and actual concurrent trace-ring tests. Shared-buffer lifetime test is a deterministic MODEL, not Metal integration.
- ASan/UBSan actual speculative hint-queue test: normal work remains serviced with speculation disabled.
- Original iPhone SDK26.2 ObjC++ renderer/bridge syntax; actual extracted MSL FXAA helper compile.
- Actual new Swift settings/menu typecheck and affected controller syntax; full Release build catches integration errors.
- Existing protected core hashes, explicit reviewed FIX exceptions only.
- Single IPA architecture, release identity, paid-cert RAM entitlements and existing bundled-feature checks.

Previously passing V5R1 mod/importer/save/skin suites are not repeated because those implementations/assets are unchanged. This is targeted scope reduction requested by owner, not a claim all old tests were rerun. ccache only targets generated engine C; first cache is cold, later unchanged builds may reuse compiler-validated objects. iPhone compiler/optimization flags remain unchanged.

Required device acceptance: city/desert fast driving and reversal, camera occlusion, first mission explosion, helicopter aiming, death/restart, cutscene, pause-map-return, mod spawn/engine sound, radio, phone interruption/background-resume, MetalFX toggles next-start, FXAA HUD readability and30min memory/thermal run. ALL PENDING DEVICE TEST. CI cannot prove these.
