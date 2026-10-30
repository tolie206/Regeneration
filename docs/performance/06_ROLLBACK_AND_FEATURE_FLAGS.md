# Rollback and isolated options
Source baseline `7e066da` remains on `mugoat-v5r1`; FIX branch separate. To inspect/build original without overwriting work: `git worktree add <new-empty-directory> 7e066da`. Do not reset/clean an existing worktree. Install original IPA only after backing up saves; FIX does not migrate/delete user data.

Settings -> graphics/upscale submenu contains FIX options. Changes apply on NEXT full app start. Defaults:
- completed EVENT optimization ON (`V5FixEventFast`); OFF restores normal event submission.
- query batching0ms (`V5FixQueryBatch`), optional.25/.5/1ms.0 is original timing.
- FXAA OFF (`V5FixFXAA`); OFF original presentation. Optional softens edges AND HUD, costs GPU; not upscaling or MSAA.
- speculative-only disable OFF (`V5FixNoSpeculation`): original speculation ON. Setting this ON never removes demand or normal-priority work.
- bounded trace OFF (`V5FixTrace`); no network/export. One aggregate line per10s always; trace adds at most8recent records per report.

Visibility lifetime correction is not exposed as an unsafe runtime switch: reverting it requires building the original baseline. No debug conservative-visible occlusion bypass, fake query values, fence removal, QoS escalation, memory reserve deletion or mission bypass is shipped.
