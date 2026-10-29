# V5R1 implementation
MSR Off: render/output 100%. Quality:85% dimensions, Balanced:75%, Performance:67%, even-aligned with 320x180 internal minimum. Thus pixel workload is about72%,56%,45% before scaler overhead; these are mathematical ratios, NOT FPS predictions. Output resolution is the chosen graphics resolution rather than an unconditional native-screen upscale. Default Off, settings changes apply next app start.

Preset LOD is reduced by25% when nonzero, non-Lite shadow quality capped Low and grass/reflection/particles atHigh. Lowest presets are already at minimum; Ultra Performance engine options remain exact. Original textures, mission data, handling, navmesh and audio data are not overwritten with the supplied fixlag folder. Only grass shadow fade distances are disabled in a cached, same-length visual XML overlay for non-Lite presets.

Launcher uses supplied gold icon and sunset background, reordered layout, vertical utility rail and a single Reduce-Motion-aware entrance transition. No continuously running decorative timer.
