# FIX5 — bike body and built-in traffic optimizer

## Bike body clipping
Optional switch (default on) in Tiếng xe và góc nhìn. Only local player on an actual motorcycle model, gameplay first-person camera and positive extra FOV. Uses a render-submission guard in CPedDrawHandler::AddToDrawList(this,fwEntity*,params): matched local ped returns native no-draw0 before the wasm prologue/stack allocation. No physics/entity flags, network state, material/texture replacement, near-plane alteration or camera reset. Other peds and the motorcycle still render. Hands, shadows/reflections of the local player can disappear too; this is an explicit tradeoff, not selective torso geometry removal.

Main-script tick caches only the player's ped address. Camera rendering guards also recheck at render submission to stop hiding on third-person/cutscene changes. Off, on foot, automobile, pause/load, respawn, FOV0 and setting-off invalidate the selection. No new thread, nearby-ped scan or per-frame logging. Existing health line reports successful local render skips. Compatibility with all custom skins/attachments still needs device visual testing.

## Integrated package
Verbatim E:/New Project/Mugoat-Data-PortLike-v1/Mugoat-V5-OPTIMIZER/Mugoat-PortLike-Traffic-v1.oiv,701bytes, SHA256 bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c. Only PC VehicleUpperLimit20 and VehicleParkedUpperLimit15; other gameconfig values/pools, graphics, textures, scripts remain untouched. Not an ETC2 conversion, memory/map fix or FPS guarantee.

First game startup installs to Documents/Mods/Mugoat-V5-OPTIMIZER, before NativeAssets reads mods. Existing on/off directory honored without overwriting. A persisted installed-once marker prevents reinstating a package the user removes. Visible in the existing mod manager; disable/remove applies after full app restart. Original game data and saves remain unchanged. Package size adds under1KB of actual payload, no game assets.

## Tests
New native runtime eligibility/restore test, actual pinned ped draw ABI audit/idempotence, exact package hash/XML delta, real Swift installer lifecycle tests (disabled, removed, existing custom folder) and settings typecheck. Final IPA verifies package SHA and entitlements. Existing FIX4 camera/audio/filter tests not rerun; preserved source review checks cover all other core areas. Device rendering/real FPS acceptance remains pending.
