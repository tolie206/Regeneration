# R008 hotfix / build1018
Same branch regeneration-r008-native-reclaim.

Tester log E:/log r008/native-port.log confirms 27rev REQUEST_MODEL dependency failure, then status5 timeout, with plenty of headroom and zero host growth clamps. This is a distinct failure from the earlier status8 RAM gate. Missing vehicles_race_generic is now aliased to vehshare only when neither a real dictionary nor a virtual relationship provider is present. Tests cover absence and preservation of an installed virtual provider. Actual on-device success still requires tester confirmation.

Experimental lazy CPU hooks are removed from production preparation/EngineHost and the engine-function bridge. This restores the original R007 D3D allocation paths, rather than assuming the experiment is proven responsible for all drops. The log also reports thermal serious, GPU frame time up to54ms and a large informational speech-failure log flood. Exact speech-failure messages are now sampled; streaming/parser failures and health logs remain. No quality settings or shader changes.
