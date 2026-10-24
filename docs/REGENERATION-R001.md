# Mugoat NewGen — Regeneration R001

Base: `regeneration` at `1ff094d` (V007), not `main` at `f9422f5`.
Bundle version: 1010. Output: `Mugoat-NewGen-Regeneration-R001.ipa`.

## Build metadata correction

Run `40065259521` compiled successfully and produced an IPA, then failed its post-build version check. `app/project.yml` still declared build 1007, so XcodeGen overwrote the intended 1010 in `Info.plist`. Both now declare 1010. A pre-build source consistency gate rejects mismatches before compiling, and the final IPA verifier checks the packaged values against those consistent sources with an explicit diagnostic. Regression tests cover stale build and marketing versions. The final IPA version, toolchain, bundled resources and memory entitlement checks remain enabled.

## Changes

- Preserve the branch's renderer, heap, streaming guard and asset-reclamation policy. No later `main` reclaim/recovery changes were merged.
- Vehicle import retains ZIP/RAR and multi-selection. Archive detection is done by libarchive, including RAR files incorrectly named `.zip`.
- Normalize dash-only decorative comments in vehicle metadata, discovered in the supplied SH150 `vehicles.meta`; this retains a valid XML separator. Real startup preparation and unchanged nested RPF bytes are checked on all three owner vehicle packs.
- General import recognizes sound-only DLCs and uses the existing native REL54 conversion instead of installing the incompatible raw audio pack. The explicit sound-import row remains available. Delayed profile registration now retries at two-second intervals, at most ten times, then stops. A successful assignment runs once per vehicle/selection.
- The launcher catalog has Vietnamese values for every one of its 668 keys, with format placeholders preserved. The supplied Vietnamese OIV has 1,211 GXT2 files and 457,478 source label entries: all their label hashes exist in the already bundled accented overlay. The bundled overlay includes additional aliases/common-label translations, with 487,918 entries across 1,216 GXT2 files. This measures label coverage, not whether every source line was translated correctly by the original mod author.
- Save import continues to accept only validated SGTA5 saves. It does not import `settings.xml`, `pc_settings.bin`, mod overlays or launcher language preferences. The existing real-save regression verifies the PC settings file is preserved. The full-language archive overlay test remains a required CI gate.
- The supplied Menyoo 1.0.5 ASI is byte-identical to the bundled ASI. Original licenses remain included. Vietnamese dictionary expanded from 236 to 333 entries, including addon model input and outfit navigation; owned previous installs receive the dictionary update while retaining their configuration. The bundled configuration selects Vietnamese. Menyoo remains opt-in, with no additional interpreter work when disabled.
- New **Mods → Nhập skin addon (Menyoo)** imports ZIP/RAR, a folder, or a four-file selection. Each non-streamed model requires YDD/YFT/YMT/YTD and is registered in its own startup DLC with `peds.meta` and a `peds.rpf`. Models and textures are not converted. The 15 supplied NIER 2B/A2 variants are included in the compatibility tests. Incomplete/ambiguous groups fail before installation. Streamed peds or other ped types require a correctly prepared DLC; do not treat a loose streamed folder as a four-file ped.
- On launch, enabled addon models populate the bundled Menyoo's **Player Options → Model Changer → Skin addon NewGen** list. Updating this generated category is idempotent; other categories stay in place. Skins disabled in Mods leave this category on the next launch.
- Only an owned, unambiguous bundled Menyoo package receives the generated skin category; an unowned folder with the same name is left intact.
- **Settings → Tầm nhìn và texture (4 GB)** exposes boot-only Extended Distance Scaling (`-MaxLODScale`, separately from `lodScale`) and Extended Texture Budget. The latter controls the port's existing `PG_VIDEO_MEMORY_MB` video-budget hook. It is not an extra physical RAM allocation and does not bypass the iOS process limit. Automatic preserves the branch's behavior; explicit values are 384–1280 MiB. Increasing the budget can worsen out-of-memory crashes; lowering it too far can worsen missing textures. These controls are experiments, not proof that the 4 GB map-loss issue is fixed.

## Compatibility gates before the IPA build

CI must pass the existing Python, archive-overlay, runtime-policy, memory-budget, real-save and real-import tests, plus:

1. Native sound-tick regression: delayed availability, one successful force, bounded retry/logging, balanced guest stack.
2. Original owner archives (SHA-256 verified): Ferrari LaFerrari, SH150, Honda Vision, Aquaphobic v1.7SP, NIER v2.1 and Menyoo 1.0.5.
3. Actual Swift import of all three cars; all 13 sound profiles with REL54 conversion and AWC bank mounts; all 15 skin packs with byte-for-byte restored resources, multi-select/ZIP equivalence, missing-file rejection and Menyoo XML registration.
4. Streaming preference validation and automatic reset.

All local source, fixtures, extraction directories and reports for this work are under `F:\Output`. `F:\game` and the original mod folders are read-only inputs.

## On-device validation still required

Import/format tests do not render vehicles, audition engine sounds or execute Menyoo inside a running iOS game. No connected iPhone or Apple Silicon simulator is available in the Windows workspace. A successful CI importer test is not a successful in-game spawn. Test on a signed IPA before accepting the build as playable:

- Start with the same route/save on a 4 GB iPhone; record preset, FPS, signing memory entitlement and both new settings. Change one setting at a time and test at least 15–20 minutes, including fast travel and driving into a new district.
- Import each supplied vehicle; restart and spawn it, check textures and handling. Select an imported sound profile and listen both inside/outside the vehicle after restart.
- Enable bundled Menyoo before Play, open F8 and select each addon model from the generated category. Verify model visibility, clothing components, animation and return to the original character before a story mission/save.
- Import a story save, restart, load it and check Vietnamese menu/subtitles plus accented fonts. Some proper names, asset names and original untranslated source-pack strings can remain English; the hash-coverage audit is not a claim that all game dialogue and every Menyoo string has been human-reviewed.

Metadata reference: [Cfx data-file types](https://docs.fivem.net/docs/game-references/data-files/) (`PED_METADATA_FILE`).
