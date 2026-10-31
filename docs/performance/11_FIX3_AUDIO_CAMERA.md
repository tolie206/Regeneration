# V5R1-FIX3 — audio, native first person, launcher mods

## Evidence from two supplied logs (E:/log sound)
Both are FIX2 on A16, iOS18.6.1. Mixer logs 6 channels, granularEnabled=1 and stock profile requests. Neither contains the successful output-downmix diagnostic. A profile request alone is not proof of audible playback.

Source audit found an error in FIX2: mixer+75420 was treated as the channel count. It is the output-buffer enabled/valid flag. MixBuffers actually iterates channel planes using mixer+75484; buffer pointer remains +75424. FIX3 corrects this and validates these markers during preparation. Prior synthetic test wrongly populated the flag with6 and therefore missed the real layout. The new regression fixture explicitly uses flag1 / channel6, disabled, stereo, truncated and invalid-pointer cases. I acknowledge this concrete prior implementation error.

Gain is inserted only at audRequestedSettings::SetVolume calls inside audVehicleEngineComponent::Update (6 sites) and audGranularEngineComponent::Update (4 sites). Default+6dB; choices0/3/6/9/12. Stop/silence <=-96dB retained. Global SetVolume, music, speech, horn and pitch functions untouched. Applies to engine components of NPC and player vehicles, not only the currently driven vehicle. Peak-safe stereo fold remains. Audible gain/quality must still be checked on iPhone; this cannot repair an absent or invalid sound bank.

## Performance interpretation
Log native-port(3): 8 health samples, all thermal serious, median38FPS, reported GPU-total23.25ms. Previous: nominal4samples median60FPS/GPU12.75ms; fair2 median57.5/GPU14.6ms; serious8 median60/GPU18.6ms. Heat alone does not explain the difference: scene workload also differs. 16 vs7 logged >50ms frames are interval totals, not 1%low. Late current frame profiles show main visibility/rasterizer waits; renderer ~3457draws/frame, pipelines0compiling and0skips in that sample. Last asset reads average0.8ms,0slow/errors; guard0evictions. No evidence justifies disabling RAM protection, changing streaming limits or culling mission assets here. No speculative renderer/streaming changes or FPS guarantee. Wider FOV may cost GPU; default0extra preserves prior camera rendering. The single new output-layout diagnostic logs once, not per frame. Keep existing lower-resolution MSR/thermal choices for hot devices.

## Camera
Supplied Alternate First Person is an x64 Windows ASI requiring ScriptHookV, optional ReShade. Current iOS has an ASI compatibility layer, but this package imports unsupported keybd_event/XInputGetState and ReShade is not part of iOS. It has not been run or certified compatible, and is not bundled.

Instead add a native first-person controls page: switch native ped+vehicle mode4, return mode1 using existing guarded script-thread queue. Native animation system handles arms/guns/steering when models support it. Optional on-foot widening0/5/10/15/20deg only patches camFirstPersonShooterCamera::UpdateZoom's three FOV stores. Offset160 independently verified by CommandSetCamFov. Inputs<50deg (scope zoom), >85deg and nonfinite values unchanged; final cap100deg. No scripted-camera creation, head-bone polling, per-frame script enforcement or cutscene override. Vehicle interior FOV remains native; parity with the Windows bodycam mod is NOT claimed. Visual acceptance of hands/model clipping is device pending.

## UI and testing
Home has a full-width Quản lý mod button in the scrollable content, reusing the existing manager. Manager header shows installed/enabled counts; no new importer/runtime scan. Settings has Tiếng xe và góc nhìn.

Local: actual pinned C hooks audited and idempotence tested. New Python isolation/changed-layout tests. CI runs only new audio/downmix/FOV sanitizer tests, new Swift typecheck and changed UI parse, then Release build and IPA metadata/entitlement verification. Existing renderer/asset/import/save regression suites not rerun. Build and gameplay outcome must be reported separately.

Rollback: tag/checkpoint before FIX3; engine0dB, FOV0 and old downmix switch restore corresponding paths. Original data/save untouched. FIX2 commit0383f09 remains available.
