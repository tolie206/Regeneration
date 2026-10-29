import Foundation
#if canImport(FoundationXML)
import FoundationXML
#endif
enum SoundAssignments {
 static var choices:[String:String] {
  get{UserDefaults.standard.dictionary(forKey:"NewGenSoundChoices") as? [String:String] ?? [:]}
  set{UserDefaults.standard.set(newValue,forKey:"NewGenSoundChoices")}
 }
 /// A raw sound-only DLC and its converted import must not both register one profile.
 static func resolveDuplicatePacks(log:(String)->Void){
  let imported=Set(SoundInstaller.available());guard !imported.isEmpty else{return}
  let fm=FileManager.default
  for mod in ModInstaller.installed() where mod.enabled {
   if fm.fileExists(atPath:mod.url.appendingPathComponent("sound-profiles.json").path){continue}
   var profiles=Set<String>(),vehicle=false,uncertain=false
   func scan(_ archive:RPFArchive,_ depth:Int){
    guard depth<5 else{uncertain=true;return}
    for e in archive.entries {
     if e.path.hasSuffix(".yft") || e.path.hasSuffix(".ytd") || e.path.hasSuffix("vehicles.meta"){vehicle=true}
     if e.path.hasSuffix(".rpf") {
      if let child=try? archive.nested(e){scan(child,depth+1)}else{uncertain=true}
     }else if e.path.hasSuffix("_game.dat151.rel") || e.path.hasSuffix("_game.dat151") {
      if let data=try? archive.binary(e),let names=try? ModAudio.profiles(data,filename:e.path.hasSuffix(".rel") ? e.path:e.path+".rel"){profiles.formUnion(names)}else{uncertain=true}
     }
    }
   }
   if let walk=fm.enumerator(at:mod.url,includingPropertiesForKeys:nil,options:.skipsHiddenFiles){
    for case let url as URL in walk where url.lastPathComponent.lowercased()=="dlc.rpf" {
     if let archive=try? RPFArchive(url:url){scan(archive,0)}else{uncertain=true}
    }
   }
   guard !vehicle,!uncertain,!profiles.isEmpty,profiles.isSubset(of:imported) else{continue}
   let off=URL(fileURLWithPath:mod.url.path+".off")
   guard !fm.fileExists(atPath:off.path) else{log("Sound conflict: duplicate backup already exists for \(mod.name); left unchanged.");continue}
   do{try fm.moveItem(at:mod.url,to:off);log("Sound conflict: disabled duplicate sound-only pack \(mod.name); converted import takes priority. Original kept as .off.")}
   catch{log("Sound conflict: \(error.localizedDescription)")}
  }
 }
 /// Rebind only the original road-vehicle profile, read from this installed
 /// game, on ambient NPC -> player takeover. No generic substitute profile.
 static func registerStockAudio(data:URL,log:(String)->Void){
  let url=data.appendingPathComponent("common/data/levels/gta5/vehicles.meta")
  guard let bytes=try? Data(contentsOf:url),bytes.count<=8*1024*1024 else{return}
  let parser=XMLParser(data:bytes),reader=StockVehicleAudioReader(excluded:Set(ModVehicleSupport.vehicles()))
  parser.delegate=reader
  guard parser.parse() else{log("Original vehicle audio: metadata invalid; no recovery profiles registered.");return}
  var count=0
  for (model,profile) in reader.profiles {
   var h:UInt32=0;for c in model.utf8 {h &+= UInt32(c);h &+= h << 10;h ^= h >> 6};h &+= h << 3;h ^= h >> 11;h &+= h << 15
   if PGRegisterStockVehicleSound(h,profile){count+=1}
  }
  log("Original vehicle audio: \(count) exact road-vehicle profiles available for ambient driver takeover; custom mods excluded.")
 }
 static func configure(){
  let available=Set(SoundInstaller.available());PGEnableSoundMods(!available.isEmpty)
  for (key,value) in choices where available.contains(value) {
   if let model=UInt32(key){_ = PGSelectVehicleSound(model,value)}
  }
 }
 static func set(_ model:UInt32,_ profile:String){
  var saved=choices
  if profile.isEmpty {saved.removeValue(forKey:String(model))}else{saved[String(model)]=profile}
  choices=saved;_ = PGSelectVehicleSound(model,profile)
 }
}

private final class StockVehicleAudioReader:NSObject,XMLParserDelegate {
 let excluded:Set<String>
 var profiles:[String:String]=[:]
 private var model="",audio="",kind="",field="",buffer=""
 init(excluded:Set<String>){self.excluded=excluded}
 private func finish(){
  guard !model.isEmpty,["VEHICLE_TYPE_CAR","VEHICLE_TYPE_BIKE","VEHICLE_TYPE_QUADBIKE"].contains(kind),!excluded.contains(model) else{return}
  let profile=audio.isEmpty ? model:audio
  let valid: (String)->Bool = { !$0.isEmpty && $0.utf8.count<=63 && $0.utf8.allSatisfy{($0>=97&&$0<=122)||($0>=48&&$0<=57)||$0==95} }
  if valid(model)&&valid(profile){profiles[model]=profile}
 }
 func parser(_ parser:XMLParser,didStartElement name:String,namespaceURI:String?,qualifiedName:String?,attributes:[String:String]){
  if name=="modelName"{finish();model="";audio="";kind=""}
  if ["modelName","audioNameHash","type"].contains(name){field=name;buffer=""}
 }
 func parser(_ parser:XMLParser,foundCharacters text:String){if !field.isEmpty{buffer+=text}}
 func parser(_ parser:XMLParser,didEndElement name:String,namespaceURI:String?,qualifiedName:String?){
  guard name==field else{return}
  let value=buffer.trimmingCharacters(in:.whitespacesAndNewlines)
  if name=="modelName"{model=value.lowercased()};if name=="audioNameHash"{audio=value.lowercased()};if name=="type"{kind=value}
  field="";buffer=""
 }
 func parserDidEndDocument(_ parser:XMLParser){finish()}
}
