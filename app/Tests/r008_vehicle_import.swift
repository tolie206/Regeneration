import Foundation
import Darwin
#if canImport(FoundationXML)
import FoundationXML
#endif
@main struct R008Vehicles {
 static func main() throws {
  setbuf(stdout,nil)
  let fm=FileManager.default,root=URL(fileURLWithPath:CommandLine.arguments[1])
  let uri="dlc_test:/%PLATFORM%/vehiclemods/VEHICLE_mods.rpf"
  let xml="<root><filename>\(uri)</filename><Item>\(uri)</Item></root>"
  let fixed=ModVehicleSupport.repairContentMounts(xml,paths:["x64/vehiclemods/test_mods.rpf"],log:{print($0)})
  precondition(fixed.components(separatedBy:"test_mods.rpf").count==3)
  precondition(ModVehicleSupport.repairContentMounts(fixed,paths:["x64/vehiclemods/test_mods.rpf"],log:{_ in})==fixed)
  precondition(ModVehicleSupport.repairContentMounts(xml,paths:["x64/vehiclemods/a_mods.rpf","x64/vehiclemods/b_mods.rpf"],log:{_ in})==xml)
  precondition(ModVehicleSupport.repairContentMounts(xml,paths:["x64/vehiclemods/VEHICLE_mods.rpf"],log:{_ in})==xml)
  precondition(ModVehicleSupport.repairContentMounts(xml,paths:["other/test_mods.rpf"],log:{_ in})==xml)
  var hashes:[UInt32]=[]
  for (name,model) in [("sh150.zip","sh150"),("vision.zip","vision"),("27rev.zip","27rev")] {
   let stage=try ModInstaller.unpack(root.appendingPathComponent(name));defer{try? fm.removeItem(at:stage)}
   let plan=ModInstaller.plan(folder:stage,name:"r008-test-"+model,index:.init())
   precondition(plan.items.count==1 && plan.items[0].target.hasSuffix("/dlc.rpf"),"DLC import failed: \(name): \(plan.skipped)")
   let original=try RPFArchive(url:plan.items[0].source)
   let target=try ModInstaller.install(plan);defer{try? fm.removeItem(at:target)}
   let manifest=root.appendingPathComponent("manifest-"+model+".json")
   try JSONSerialization.data(withJSONObject:["files":[[Any]]()]).write(to:manifest)
   ModVehicleSupport.prepare(manifestPath:manifest.path,log:{print($0)})
   let installed=try RPFArchive(url:target.appendingPathComponent(plan.items[0].target))
   precondition(ModVehicleSupport.vehicles().contains(model),"Model absent from production mod picker")
   let meta=try installed.metadata(installed.entries.first{$0.path.hasSuffix("vehicles.meta")}!)
   precondition(XMLParser(data:meta).parse());precondition(String(data:meta,encoding:.utf8)!.contains("<modelName>"+model+"</modelName>"))
   if model=="27rev" {precondition(String(data:meta,encoding:.utf8)!.contains("<parent>vehshare</parent>"),"Missing race DLC parent not resolved")}
   let content=try installed.metadata(installed.entries.first{$0.path=="content.xml"}!)
   precondition(XMLParser(data:content).parse())
   if model=="sh150" {
    let text=String(data:content,encoding:.utf8)!
    precondition(!text.contains("VEHICLE_mods.rpf") && text.contains("sh150_mods.rpf"),"Confirmed missing mount not repaired")
   }
   // Every nested archive, geometry and texture payload remains byte-identical.
   for e in original.entries where e.path.hasSuffix(".rpf") {
    let after=installed.entries.first{$0.path==e.path}!
    precondition(e.size==after.size && original.bytes[e.offset..<(e.offset+e.size)]==installed.bytes[after.offset..<(after.offset+after.size)])
   }
   var geometry=Set<String>(),textures=Set<String>(),count=0
   func walk(_ a:RPFArchive,_ depth:Int)throws {
    precondition(depth<8)
    for e in a.entries {
     if e.path.hasSuffix(".rpf"){try walk(a.nested(e),depth+1)}
     else if let version=e.resourceVersion {
      let source=try a.resourceData(e)
      _=try ModResource.normalize(source,name:e.path) // Inflate and validate actual complete payload.
      if e.path.hasSuffix(".yft"){precondition(version==162);geometry.insert((e.path as NSString).lastPathComponent)}
      if e.path.hasSuffix(".ytd"){precondition(version==13);textures.insert((e.path as NSString).lastPathComponent)}
      count+=1
     }
    }
   }
   try walk(installed,0)
   precondition(geometry.contains(model+".yft") && geometry.contains(model+"_hi.yft") && textures.contains(model+".ytd"))
   let before=try Data(contentsOf:target.appendingPathComponent(plan.items[0].target))
   ModVehicleSupport.prepare(manifestPath:manifest.path,log:{_ in})
   let afterSecondPrepare=try Data(contentsOf:target.appendingPathComponent(plan.items[0].target))
   precondition(before==afterSecondPrepare,"Preparation must be idempotent")
   if model=="27rev" {
    // An actually supplied parent must not be substituted on another installation.
    let provider=ModInstaller.Plan(name:"r008-provider")
    let providerSource=root.appendingPathComponent("provider.meta")
    let providerXML="<root><parent>vehshare</parent><child>vehicles_race_generic</child></root>"
    let providerPack=try VehicleInstaller.pack(["data/vehicles.meta":Data(providerXML.utf8)])
    let provided=root.appendingPathComponent("provider.rpf");try providerPack.write(to:provided)
    var providerPlan=provider
    providerPlan.items=[.init(source:provided,target:"update/x64/dlcpacks/provider/dlc.rpf",note:"")]
    let providerTarget=try ModInstaller.install(providerPlan);defer{try? fm.removeItem(at:providerTarget)}
    // Reinstall pristine 27rev, then prepare alongside a virtual provider.
    try fm.removeItem(at:target);_ = try ModInstaller.install(plan)
    ModVehicleSupport.prepare(manifestPath:manifest.path,log:{_ in})
    let preserved=try RPFArchive(url:target.appendingPathComponent(plan.items[0].target))
    let pm=try preserved.metadata(preserved.entries.first{$0.path.hasSuffix("vehicles.meta")}!)
    precondition(String(data:pm,encoding:.utf8)!.contains("<parent>vehicles_race_generic</parent>"),"Existing virtual TXD provider must be retained")
    _ = providerSource
   }
   // The exact names/hashes registered by the real packs feed the native bridge simulation.
   var hash:UInt32=0;for c in model.utf8{hash &+= UInt32(c);hash &+= hash<<10;hash ^= hash>>6};hash &+= hash<<3;hash ^= hash>>11;hash &+= hash<<15;hashes.append(hash)
   print("PASS actual vehicle pack: \(model), \(count) full resource payloads, picker registration, metadata, mount, unchanged model/texture bytes; hash \(hash)")
  }
  try hashes.map{String($0)}.joined(separator:"\n").write(to:root.appendingPathComponent("model-hashes.txt"),atomically:true,encoding:.utf8)
  print("NOT VERIFIED: iPhone rendered pixels, model streaming success or driving. Native command simulation is a separate test, not a physical-device spawn.")
 }
}
