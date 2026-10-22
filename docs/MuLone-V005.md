# MuLone-V005

- Fix V004 compile error: Objective-C NSUserDefaults.standard -> [NSUserDefaults standardUserDefaults]. V004 sound/visual tests passed; whole NativeAssets.m had not been compiled by those isolated tests. Added iPhoneOS clang syntax check of full NativeAssets.m and VisualEffects.m before large engine build.
- Keep V003 Xcode 26.2/17C52 and V004 fixes. No new arbitrary heap or memory guard changes.
- Add RAM page: refresh actual DeviceTier measurement, show installed signature entitlement status, clear app-imposed cap to automatic, export the two already-required RAM entitlements for a compatible signing tool. No fake permission success or allocation stress test. No claim that a button can raise iOS process limit.
- Old Mugoat and current Full.entitlements are byte-equivalent in requested rights. Current code does NOT hard-cap process RAM at 4 GB: 4095 MB is normally engine virtual reservation, while Metal/app RAM counts separately. Real available process RAM can vary with iOS, device and signing profile. Need signed phone logs to explain specific 5 GB vs 4 GB report.
- New destination repo Living-NG/GTA-NEW-GEN-2 (Private). Preserve source history; merge its README-only initial commit without force push. Credentials stay in GCM, not source/IPA. Existing repo remains intact as rollback.

Phone verification: app installs with the intended certificate, Settings > RAM reports entitlement and estimated budget, automatic cap chosen before start, tester log includes process limit and engine virtual reservation separately. Low-memory 2.1 GB devices still cannot be promised stable high-detail gameplay without granted headroom.

Apple reference: https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.kernel.increased-memory-limit
