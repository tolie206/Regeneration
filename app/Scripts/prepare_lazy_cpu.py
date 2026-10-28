"""Defer only zero-initialized CPU copies; materialize before every D3D CPU access.
Pinned engine layouts are checked before any generated file is written.
"""
from pathlib import Path
import re
from engine_names import fn
ROOT=Path(__file__).resolve().parents[1]
CREATE={
 'wasm_null_d3d::NullDevice::CreateBuffer(D3D11_BUFFER_DESC const*, D3D11_SUBRESOURCE_DATA const*, ID3D11Buffer**)':(1,120,'var_B7'),
 'wasm_null_d3d::NullDevice::CreateTexture1D(D3D11_TEXTURE1D_DESC const*, D3D11_SUBRESOURCE_DATA const*, ID3D11Texture1D**)':(2,128,'var_B9'),
 'wasm_null_d3d::NullDevice::CreateTexture2D(D3D11_TEXTURE2D_DESC const*, D3D11_SUBRESOURCE_DATA const*, ID3D11Texture2D**)':(3,144,'var_B4'),
 'wasm_null_d3d::NullDevice::CreateTexture3D(D3D11_TEXTURE3D_DESC const*, D3D11_SUBRESOURCE_DATA const*, ID3D11Texture3D**)':(4,136,'var_B9'),
}
ACCESS={
 'wasm_null_d3d::NullContext::Map(ID3D11Resource*, unsigned int, D3D11_MAP, unsigned int, D3D11_MAPPED_SUBRESOURCE*)':('var_p1',),
 'wasm_null_d3d::NullContext::CopySubresourceRegion(ID3D11Resource*, unsigned int, unsigned int, unsigned int, unsigned int, ID3D11Resource*, unsigned int, D3D11_BOX const*)':('var_p1',),
 'wasm_null_d3d::GpuReadback(ID3D11Resource*, unsigned int, ID3D11Resource*, unsigned int, D3D11_BOX const*)':('var_p0',),
 'wasm_null_d3d::NullContext::CopyResource(ID3D11Resource*, ID3D11Resource*)':('var_p1','var_p2'),
 'wasm_null_d3d::NullContext::UpdateSubresource(ID3D11Resource*, unsigned int, D3D11_BOX const*, void const*, unsigned int, unsigned int)':('var_p1',),
}
DECL='extern int pg_lazy_cpu_create(w2c_game*, u64, u64, u64, unsigned);\nextern void pg_lazy_cpu_need(w2c_game*, u64);\n'
PROLOGUE='  (void)wasm_rt_local_memory_size;\n'
MARK='/* R008 deferred CPU shadows */'
def patch_body(body,name):
 if MARK in body:return body
 if name in CREATE:
  kind,offset,label=CREATE[name]
  anchor=f'    var_j1 = var_p0;\n    var_j2 = var_p1;\n    i64_store_shared(wasm_rt_local_memory_base, wasm_rt_local_memory_size, instance->w2c_env_memory, (u64)checked_add_u64(var_j1, {offset+8}u), var_j2);'
  if body.count(anchor)!=1 or body.count(label+':;')!=1:raise RuntimeError(f'D3D CPU allocation layout changed: {name}')
  # This is after GPU upload and GetMemorySize, before the original calloc and counters.
  call=f'    {MARK}\n    if (pg_lazy_cpu_create(instance,var_p0,var_p1,var_p2,{kind})) goto {label};\n'
  return body.replace(anchor,call+anchor,1)
 if body.count(PROLOGUE)!=1:raise RuntimeError(f'D3D CPU access prologue changed: {name}')
 calls='  '+MARK+'\n'+''.join(f'  pg_lazy_cpu_need(instance,{arg});\n' for arg in ACCESS[name])
 return body.replace(PROLOGUE,PROLOGUE+calls,1)
def patch_files(folder,resolve=fn):
 files={p:p.read_text() for p in sorted(folder.glob('game_*.c'))}
 for name in (*CREATE,*ACCESS):
  index=resolve(name);rx=re.compile(r'^\w+ w2c_game_f'+str(index)+r'\([^;{]*\)\s*\{',re.M)
  hits=[(p,rx.search(s)) for p,s in files.items() if rx.search(s)]
  if len(hits)!=1:raise RuntimeError(f'Expected one D3D definition: {name}, found {len(hits)}')
  p,m=hits[0];s=files[p];end=s.index('\n}\n',m.end())+3;body=s[m.start():end]
  changed=patch_body(body,name)
  if changed!=body:
   s=s[:m.start()]+changed+s[end:]
   if DECL not in s:
    include=re.search(r'^#include "game-[a-z-]*impl\.h"$',s,re.M)
    if not include:raise RuntimeError('Missing generated implementation include')
    s=s[:include.end()]+'\n'+DECL+s[include.end():]
   files[p]=s
 for p,s in files.items():
  if s!=p.read_text():p.write_text(s)
 print('lazy CPU shadows: verified 4 creation paths and 5 access paths')
if __name__=='__main__':patch_files(ROOT/'Generated')
