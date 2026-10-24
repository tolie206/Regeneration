"""Update only the bundled language dictionary; preserve the supplied plugin and licenses."""
from pathlib import Path
import json,zipfile,tempfile
root=Path(__file__).resolve().parents[1]
dictionary={}
for name in ['menyoo_vi.json','menyoo_vi_extra.json']:
    dictionary.update(json.loads((root/'tools'/name).read_text(encoding='utf8')))
target=root/'app/Resources/BundledMenyoo.zip'
temporary=target.with_suffix('.tmp')
with zipfile.ZipFile(target) as old,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as new:
    for entry in old.infolist():
        data=old.read(entry.filename)
        if entry.filename=='menyooStuff/Language/Vietnamese.json':data=(json.dumps(dictionary,ensure_ascii=False,indent=2)+'\n').encode()
        new.writestr(entry,data)
temporary.replace(target)
print('Bundled Menyoo:',len(dictionary),'Vietnamese entries; original binary preserved')
