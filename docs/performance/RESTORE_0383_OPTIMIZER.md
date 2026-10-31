# Restore0383f09 + requested OIV only

Parent0383f09b08004319c2fd87db96d454eb9696fe45, user-requested baseline. All app/Source, app/Scripts, engine inputs, renderer, audio, scheduling, memory policy, camera and graphics configuration are unchanged from that commit. No fixes/features from FIX3–FIX6 are carried into engine code, including later FOV, filter, gain or body-hiding hooks. Baseline behavior is intentionally restored exactly, including its known limitations.

Only functional addition: standalone BundledOptimizer installs the exact701-byte Mugoat-PortLike-Traffic-v1.oiv at startup before asset mounting. Two PC population caps20moving/15parked, no other gameconfig edits. Source SHA256 bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c. Installed/disabled/imported copies and prior removal choices are honored; manage via original Settings/Mods. Original game data/save files not overwritten. The OIV is optional and not a texture conversion or FPS guarantee.

Label V5R1-FIX2-OPTIMIZER, short version5.1.2, build5009. Existing graphics/user settings and save/mod folders remain user-owned; this restores source, not a fresh-install preferences snapshot.

Exact tree whitelist check requires byte-identical engine/renderer/scripts vs0383f09, verifies original controller differs only by one optimizer startup call and UI changes only release labels. New optimizer XML/hash and Swift lifecycle tests, unchanged baseline toolchain and final IPA entitlement/resource verification. No unchanged original feature test suites rerun. Existing newer branch retained for rollback. Device performance remains to be tested by user.
