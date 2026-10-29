# R008 build1020: scripted camera input compatibility

Tester log E:/mission log 2/native-port (3).log confirms the manual PAD is enabled while the mission requests INPUTGROUP_LOOK, SNIPER_ZOOM and INPUT_SCRIPT_RT. UI display alone does not establish that the scripted camera receives values.

Direct ARM64 inspection of the original 1.5.1 IPA found the compatibility branch in w2c_game_f56849 (GetControlNormal), f56857 (GetDisabledControlNormal), f56858 (GetDisabledControlUnboundNormal): if action290/291 and the original value is zero, reread the SAME original getter/control group for axis1/2. Nonzero original values remain untouched. This branch was absent in the R008 wrappers.

Ported this contract into the generated float control wrappers and the two inlined script UNBOUND_NORMAL wrappers. Enabled/disabled and bound/unbound getter types remain separate; control groups, button queries, unrelated inputs and valid scaled-axis values are unchanged. No camera angles, mission state, completion or input-disable flags are forced.

Tests compile exact production-emitted fallback snippets with ASAN/UBSAN:400actions x3control groups, native/script answer writes, positive/negative axes, zero fallback, preservation of nonzero originals, enabled vs disabled reads. Existing UI geometry/storage/controls tests remain.

Also removed duplicate script L3/R3 buttons from the manual layout; the dedicated editable L3/R3 buttons remain. Same branch regeneration-r008-native-reclaim, no renderer or memory-policy changes. Actual mission camera movement still requires iPhone confirmation after build.
