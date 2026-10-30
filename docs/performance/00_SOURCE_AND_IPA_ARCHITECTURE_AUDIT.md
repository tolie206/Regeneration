# V5R1-FIX source audit
Baseline: `7e066da`, branch `mugoat-v5r1`; isolated changes on `mugoat-v5r1-fix`. Baseline was clean. No reset/clean or save/mod migrations. Version 5.1.1 / build 5002. Windows host has no Xcode or attached iPhone; native checks/build run on GitHub's Intel macOS host using the original Xcode 26.2 iPhone toolchain. Host sanitizer runtime uses Xcode 26.6 in isolation because the 26.2 runtime failed before main on that host; device compiler remains unchanged.

Actual path: UIKit -> native engine bridge (wasm2c-generated ARM64 C) -> graphics opcode ring -> custom Metal renderer -> existing MetalFX Spatial -> drawable. This is not DXMT, an iOS browser or a newly introduced Wasm runtime.

| File | Function/site (FIX line) | Finding/action |
|---|---|---|
| app/Source/MetalRenderer/MRRenderer.mm | commandBuffer 292; commit 325; waitSerial 383 | Retained-reference buffers; explicit fences kept. Old visibility storage could be reset while a completion reader still held it. Rotate storage, keep old readers alive. |
| same | storeResult 443; beginOcclusionInPass 1016; execute 2307 | Only already-completed type-0 EVENT may avoid empty GPU submission. Occlusion/timestamp results still come from normal completion. |
| same | drawInner 1568; createShader 2212; report 2439 | Missing shader binding diagnostic is opt-in and once/hash. Pipeline pending counts are skipped draws. |
| same | uploadTextureInner 647; readback 1930 | CPU texture decode/upload and mandatory readback remain intact. |
| same | upscaled 2074; present 2110 | Existing Spatial scaler retained; optional final-pass FXAA, no extra render target. Composite HUD is filtered too. |
| same | loop 2494 | Default query delay remains 0; optional <=1ms batching uses remaining deadline instead of a fixed 2ms wait. |
| app/Source/NativeAssets.m | pg_assets_configure 489; pg_asset_hint_next call 1081 | Normal-priority hints retained; optional speculative-only disable. |
| app/Source/NativeThreads.c | initialization 18 | Existing worker user-initiated QoS retained; no global priority escalation. |
| app/Source/EngineHost.c | memory budget 335; engine argv 2952 | Existing app-limit based policy and unknown -wgpu argument unchanged. No new reclamation or resolution downgrade. |
| app/App/NativePortViewController.swift | observeAudioSession / resumeAudio around 875 | Cancel scheduled retries on inactivity/interruption; restart only active/non-interrupted. Guest audio synchronization untouched. |

Line numbers are navigation hints for this patch; use function names after later edits. Pipeline ABI inputs MRInternal.h/MRShaders.mm/pgmsl.cc are unchanged. Existing pinned shader build inputs are reused by the existing build path, not copied from the comparison IPA. No comparison binary, raw tester log, game data or credential was added by FIX.
