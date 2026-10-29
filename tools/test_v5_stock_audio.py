from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'app/App/SoundAssignments.swift').read_text();s=s[s.index('private final class StockVehicleAudioReader'):]
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder)/'main.swift';p.write_text('import Foundation\n#if canImport(FoundationXML)\nimport FoundationXML\n#endif\n'+s+'''
let xml="<Root><Item><modelName>ASEA</modelName><audioNameHash/><type>VEHICLE_TYPE_CAR</type></Item><Item><modelName>bati</modelName><audioNameHash>BATI2</audioNameHash><type>VEHICLE_TYPE_BIKE</type></Item><Item><modelName>adder</modelName><type>VEHICLE_TYPE_CAR</type></Item><Item><modelName>plane</modelName><type>VEHICLE_TYPE_PLANE</type></Item></Root>"
private let reader=StockVehicleAudioReader(excluded:["adder"]),parser=XMLParser(data:Data(xml.utf8));parser.delegate=reader
assert(parser.parse());assert(reader.profiles==["asea":"asea","bati":"bati2"])
print("PASS: actual original-profile parser, explicit aliases, empty default, mod exclusion, aircraft exclusion")
''');subprocess.run(['swiftc',str(p),'-o',folder+'/stock'],check=True);subprocess.run([folder+'/stock'],check=True)
