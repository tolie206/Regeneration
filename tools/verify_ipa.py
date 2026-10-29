import zipfile,plistlib,sys,subprocess,tempfile,pathlib,struct
from release_metadata import validate_sources
expected=validate_sources()
with zipfile.ZipFile(sys.argv[1]) as z, tempfile.TemporaryDirectory() as folder:
 z.extractall(folder);apps=list((pathlib.Path(folder)/"Payload").glob("*.app"));assert len(apps)==1
 app=apps[0];info=plistlib.loads((app/"Info.plist").read_bytes())
 assert info['CFBundleIdentifier']=='vn.gta.newgen'
 for key,value in expected.items():
  assert info.get(key)==value, f'IPA {key}={info.get(key)!r}; expected {value!r}'
 assert info['DTXcode']=='2620' and info['DTXcodeBuild']=='17C52'
 assert info['DTSDKName']=='iphoneos26.2'
 executable=(app/info['CFBundleExecutable']).read_bytes()
 magic,cpu=struct.unpack_from('<II',executable)
 assert magic==0xfeedfacf and cpu==0x0100000c, 'IPA executable must be thin iPhone ARM64, regardless of build host'
 assert (app/'VietnameseAccented.zip').is_file() and (app/'VietnamesePlain.zip').is_file()
 with zipfile.ZipFile(app/'BundledMenyoo.zip') as m:
  assert m.testzip() is None and 'menyooStuff/Language/Vietnamese.json' in m.namelist()
  assert 'LICENSE.txt' in m.namelist() and m.read('Menyoo-iOS.asi')[:2]==b'MZ'
 result=subprocess.run(['codesign','-d','--entitlements',':-',str(app)],capture_output=True,check=True)
 data=result.stdout or result.stderr
 start=data.find(b'<?xml');end=data.find(b'</plist>',start)+len(b'</plist>')
 entitlements=plistlib.loads(data[start:end])
 assert entitlements.get('com.apple.developer.kernel.increased-memory-limit') is True
 assert entitlements.get('com.apple.developer.kernel.extended-virtual-addressing') is True
 assert not entitlements.get('com.apple.security.cs.allow-jit')
 print('PASS: single native IPA, fork identity, bundled translation and Paid Cert RAM entitlements')
