import zipfile,plistlib,sys,subprocess,tempfile,pathlib
with zipfile.ZipFile(sys.argv[1]) as z, tempfile.TemporaryDirectory() as folder:
 z.extractall(folder);apps=list((pathlib.Path(folder)/"Payload").glob("*.app"));assert len(apps)==1
 app=apps[0];info=plistlib.loads((app/"Info.plist").read_bytes())
 assert info['CFBundleIdentifier']=='vn.hutaolee264.gtanewgen'
 assert info['CFBundleShortVersionString']=='1.4.4' and info['CFBundleVersion']=='1001'
 assert (app/'VietnameseAccented.zip').is_file() and (app/'VietnamesePlain.zip').is_file()
 result=subprocess.run(['codesign','-d','--entitlements',':-',str(app)],capture_output=True,check=True)
 data=result.stdout or result.stderr
 start=data.find(b'<?xml');end=data.find(b'</plist>',start)+len(b'</plist>')
 entitlements=plistlib.loads(data[start:end])
 assert entitlements.get('com.apple.developer.kernel.increased-memory-limit') is True
 assert entitlements.get('com.apple.developer.kernel.extended-virtual-addressing') is True
 assert not entitlements.get('com.apple.security.cs.allow-jit')
 print('PASS: single native IPA, fork identity, bundled translation and Paid Cert RAM entitlements')
