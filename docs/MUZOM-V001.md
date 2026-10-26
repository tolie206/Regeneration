# MuZom V001

Separate branch muzom-v001 based on R007 b5b0d53. Bundle vn.gta.muzom, display name MuZom, build2001. Existing R007/R006 branches and IPAs retained; E:/game read only during development. iOS sandbox is separate: choose the game folder again in the MuZom app; game data is not embedded in IPA.

Three choices: Story, Free roam, Zombie. Zombie host value4 maps explicitly to native Sandbox2, never to GTA VI test mode3 or unknown engine mode4. Zombie logic runs only for that selected mode; restart required to change mode. Story/free start behavior preserved.

Supplied GTZ and ZombiesMod DLLs require Windows .NET/SHVDN and are not executed or bundled. Dead Among Us XML has5450 placements, matching the supplied AI analysis after independent XML parsing. It is scenery, not zombie AI.741 visible/non-burning stock-looking debris/vehicle placements are selected; remaining peds/foliage/fires/attachments/tasks/clear-world/global weather/IPLs excluded. Credits and source readme retained; missing/custom models checked in live registry and skipped.

Native runtime: unarmed infected chase/attack player, optional stock zombie appearance or ragged civilians, drunk movement clipset when loaded. Suppresses ambient population/traffic only in zombie mode, disables police wanted pressure. Abandoned drivable damaged cars plus nearby authored wreckage. Auto caps by process quota:6/10/14 infected including corpses,2/3/4 vehicles,16/24/32 scenery;64 slots hard cap. Spawn work every500ms, one outstanding model request,5s timeout, no busywait. Nearby120m scenery, old entities removed after180m (occupied cars preserved), corpses after20s. No global object scans/huge map loads/fire storms. R007 RAM profiles/distance cleanup, renderer, Metal shaders and shader cache retained.

Safety: all natives on existing main script tick with script owner, no UIKit engine calls. Check runtime native availability, CD-image and correct model class; navmesh or road-node placement; creation verified by entity existence/model/ownership, visible flag logged. Invalid/failed assets blacklisted per session. Models released through requesting script owner. Pause/cutscene/load scene gates. Old pending positions canceled after fast travel. No deletion of foreign/reused/occupied entities. Emergency memory gate blocks new entities; cleanup remains active when headroom low.

Preflight:13 Python tests; production runtime with ASAN/UBSAN and Werror: mode isolation, missing native, pauses/scenes, caps, ownership, player immunity from accidental mutation, model release, dead cleanup, occupied car protection, low memory, timeouts/resume and stale coordinates. Actual game.wasm native audit31 calls; generated dispatch checked again before compilation. XML conversion deterministic with source hashes. Native RAM/input/audio/skin/import tests retained. No host test proves iPhone pixels, zombie pathfinding quality or actual FPS. Needs device testing before public release.

V001 is a playable prototype candidate, not a port of Simple Zombies: hunger/thirst/crafting/inventory/quests are not implemented. Original map visuals not fully reproduced. No multiplayer zombie synchronization claimed.

Sources: https://www.gta5-mods.com/maps/the-dead-among-us-project-menyoo-zombie-maps and citizenfx/natives API definitions.
