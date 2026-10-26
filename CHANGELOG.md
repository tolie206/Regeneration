# MuZom changelog

## V002 — build 2002

- User-supplied zombie logo/app icon and apocalypse artwork for launcher/settings backgrounds.
- Zombie-only launcher. Engine remains on the existing native Sandbox startup path.
- Correct low-headroom actor admission: reserve + 12 MiB for compact infected, +24 MiB for survivors, +48 MiB for scenery, +128 MiB for cars. RAM reserve and R007 streaming protection remain enabled.
- Velocity-predicted spawn center (up to 140 m ahead), bounded model requests and stale-position cancellation. Zombie cap remains 6/10/14 by app memory quota.
- Civilian/police survivors: 2 on low-quota devices, 3 otherwise. Armed, target nearby infected; individual self-defense only after player damage. Separate neutral relationship group; no wanted-star gameplay.
- Day 5 minutes, night 15 minutes; no owned infected during day. Overcast daylight and foggy night, no rain or renderer modifications.
- Two bundled validated addon zombie skins, stock zombie fallback only. Removed ordinary-human infected pool.
- Eight short groans, three simultaneous voices maximum, attenuated by distance and preloaded at startup. Gun sound-only banks; no weapon damage edits.
- Hunger/thirst HUD, inventory, bounded loot drops, proximity-validated camp shop, pistol and crowbar starter equipment.
- Four opening objectives: reach Legion Square camp, retrieve Pillbox medical supplies, defeat five infected, return for reward. Native GPS waypoint and local interaction markers.
- Atomic JSON survival save, validated schema and bounded integers; no disk I/O for HUD polling.
- Camps, procedural debris and original converted scenery share fixed entity budgets. No whole-city XML/script execution.
- Rollback tag: `muzom-v001-tested-rollback` (90151b9); original V001 IPA retained.

### Verification scope

Automated tests cover runtime ownership/memory/scene handling, moving spawn coordinates, day/night, retaliation, mission conditions, economy bounds, actual bundled skin import, audio payloads and iOS SDK typechecking. They do not prove on-device FPS, visible placement, skin animation or audible mix. Those require iPhone testing.

## V001 — build 2001

Initial bounded native zombie mode, nearby converted The Dead Among Us scenery, isolated MuZom identity and R007 memory policy. Baseline tested by users before V002.

---

## Inherited project history

# MuLone

## MuLone-V001
- Nền source 1.4.4; giữ nguyên lõi renderer/texture/streaming và tối ưu runtime mới.
- Launcher tiếng Việt, camera Swipe mặc định, bundle ID riêng.
- Việt hoá Story có dấu tích hợp sẵn, thêm lựa chọn không dấu/tắt Việt hoá.
- Import âm thanh ZIP/OIV/RPF/FiveM; chuyển REL54, giữ AWC nguyên byte; gán tiếng cho xe bằng spawn name hoặc xe đang dùng.
- Không gửi telemetry, log hay save sang backend cũ.
- Tự cung cấp shader translator đúng checksum sau khi upstream release bị 404.
- Một file MuLone-V001.ipa có entitlement RAM; ký bằng ESign.

Bản đầu cần tester xác nhận font, sound, nhiệm vụ và FPS trên iPhone. Một số thông báo chuyên sâu vẫn hiển thị tiếng Anh. Xem docs/NEW-GEN-1.md và LICENSE.
