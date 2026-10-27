from pathlib import Path
import argparse,json,re
from prepare_online_exports import prepare
p=argparse.ArgumentParser();p.add_argument('engine',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]
text=(root/'network/src/mp.rs').read_text(encoding='utf8').split('const ACTIVE_THREAD_TLS')[0]
commands=re.findall(r'\("([^\"]+)", "([^\"]+)"\)',text)
_,metadata=prepare(a.engine.read_bytes(),commands)
metadata['strategy']='original wasm2c internal ABI; input wasm is never rewritten'
a.out.write_text(json.dumps(metadata,indent=2));print('Native online readonly metadata:',len(metadata['indices']),'commands')
