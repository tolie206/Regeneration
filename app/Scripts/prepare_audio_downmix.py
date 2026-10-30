"""Pinned stereo-ring producer loses4of6 channels; insert downmix after its mix."""
from pathlib import Path
import re

def patch(text,number,mix):
 head=f'void w2c_game_f{number}(w2c_game* instance, u64 var_p0) {{'
 if head not in text:return None
 a=text.index(head);b=text.index('\n}\n',a);body=text[a:b]
 if 'pg_audio_downmix_output(' in body:return text
 pattern=rf'(?P<i> +)var_B9:;\n(?P=i)var_j0 = var_p0;\n(?P=i)w2c_game_f{mix}\(instance, var_j0\);\n'
 matches=list(re.finditer(pattern,body))
 if len(matches)!=1 or '75424u' not in body or '75420u' not in body:raise RuntimeError('Pinned audio output layout changed')
 m=matches[0];body=body[:m.end()]+m['i']+'pg_audio_downmix_output(instance, var_p0);\n'+body[m.end():]
 text=text[:a]+body+text[b:];first=text.index('\n',text.index('#include'))+1
 return text[:first]+'extern void pg_audio_downmix_output(w2c_game*, u64);\n'+text[first:]

def main():
 from engine_names import fn
 root=Path(__file__).resolve().parents[1]
 number=fn('rage::audMixerDeviceWasmDiscard::MixThread(void*)');mix=fn('rage::audMixerDevice::MixBuffers()')
 for p in sorted((root/'Generated').glob('game_*.c')):
  result=patch(p.read_text(),number,mix)
  if result is not None:p.write_text(result);print('Audio downmix patched',p.name);return
 raise RuntimeError('Pinned mixer thread missing')
if __name__=='__main__':main()
