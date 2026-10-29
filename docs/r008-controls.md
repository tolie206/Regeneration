# R008 build1019 controls
Mission logs show script-camera help INPUTGROUP_LOOK while Touch layout stays prompt (Accept/Back). The automatic prompt/flying gates disable swipe even though the mission still needs analog look.

Added top PAD toggle for a complete native controller: visible left/right sticks, LB/LT/RT/RB, ABXY, L3/R3 and D-pad. Manual mode overrides prompt and swipe routing, sends real analog axes and held triggers; no mission completion/camera state hacks. Toggle off returns to the prior auto/swipe controls.

The separate fixed layout ignores custom gameplay positions/scales to prevent overlaps. Tests measure visual and expanded touch bounds for eight iPhone/iPad safe-area sizes. Normal utility toolbar spacing is also clamped.

External controllers or keyboard/mouse still hide gameplay controls when requested, but the overlay retains Settings and Plugin. Blank areas pass through and no touch pad axes are sent in utility-only mode.

Build1019 on the same regeneration-r008-native-reclaim branch. Renderer, shaders and memory policy unchanged. Actual helicopter mission usability still needs iPhone confirmation after the automated geometry/input regressions and iOS build.
