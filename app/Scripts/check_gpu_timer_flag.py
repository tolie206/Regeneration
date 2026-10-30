"""Assert the audited noGPUTimers entry points still have the known native guards."""
from pathlib import Path
from engine_names import fn
root=Path(__file__).resolve().parents[1]
checks={
 fn('CSystem::RenderThreadInit()'):['12433536ull','12433568ull'],
 fn('rage::grcGpuTimer::Start()'):['12433568ull','goto var_B0'],
 fn('rage::grcGpuTimer::Stop()'):['12433568ull','goto var_B0'],
}
for p in sorted((root/'Generated').glob('game_*.c')):
 text=p.read_text()
 for n,markers in list(checks.items()):
  import re
  m=re.search(r'(?:void|u32|u64) w2c_game_f'+str(n)+r'\([^;]*?\) \{',text)
  if not m:continue
  body=text[m.start():text.index('\n}',m.end())]
  if not all(s in body for s in markers):raise RuntimeError('Pinned noGPUTimers guard changed')
  del checks[n]
if checks:raise RuntimeError('GPU timer guard functions missing')
print('PASS pinned engine noGPUTimers initialization and Start/Stop guards')
