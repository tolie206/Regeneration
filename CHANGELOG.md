# MuZom changelog

## V002 — build 2002

- Zombie-only launcher. Engine remains on the existing native Sandbox startup path.
- Correct low-headroom actor admission: reserve + 24 MiB for peds; expensive scenery/cars retain reserve + 128 MiB. RAM reserve and R007 streaming protection remain enabled.
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
