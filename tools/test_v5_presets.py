from pathlib import Path
import tempfile,subprocess
root=Path(__file__).resolve().parents[1]
s=(root/'app/App/GraphicsOptions.swift').read_text();s=s[s.index('enum GraphicsPreset:'):s.index('/// One detail')]
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder)/'main.swift';p.write_text('import Foundation\nenum AppLanguage {static func choose(_ s:String)->String{s}}\n'+s+'''
let lite=["-shaderQuality=1","-textureQuality=0","-shadowQuality=-1","-reflectionQuality=0","-particleQuality=0","-grassQuality=0","-cityDensity=0","-lodScale=0","-pedLodBias=0","-vehicleLodBias=0","-pedVariety=0","-vehicleVariety=0"]
assert(GraphicsPreset.lite.engineOptions==lite)
for p in GraphicsPreset.allCases {for opt in p.engineOptions {assert(!opt.contains("nan"))};assert(p.height>=432)}
assert(GraphicsPreset.max.engineOptions.contains("-lodScale=0.75"))
assert(GraphicsPreset.ultra.engineOptions.contains("-shadowQuality=0"))
print("PASS: actual presets; Ultra Performance options unchanged, high presets lighter")
''');subprocess.run(['swiftc',str(p),'-o',folder+'/presets'],check=True);subprocess.run([folder+'/presets'],check=True)
