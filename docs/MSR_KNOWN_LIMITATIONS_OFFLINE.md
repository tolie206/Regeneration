# V5R1 limitations
Spatial MetalFX cannot eliminate CPU/asset/shader stutter. No temporal history, motion vectors or generated frames. Composite HUD is upscaled too. Bilinear fallback is softer and explicitly identified in logs. Low input resolutions can lose fine detail. Device image/color validation and performance remain required.

Stock-engine silence: user confirms NPC engine audible until player takes vehicle, affecting every stock car. Existing log contains missing update:/x64/audio/sfx/RESIDENT/LOW_LATENCY.awc; base archives exist but their encrypted tables cannot be assumed to contain the missing update bank. This is an investigation lead, NOT a proven root cause or confirmed fix. No generic replacement of all vehicle audio and no speculative mixer/allocator change shipped.

No claim of complete RAM system port from another binary. Existing R008 safety, reserve/distance policy and reclaim remain unchanged. No online/multiplayer modifications.
