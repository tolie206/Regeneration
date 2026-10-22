import Foundation
enum SoundAssignments {
 static var choices:[String:String] {
  get{UserDefaults.standard.dictionary(forKey:"NewGenSoundChoices") as? [String:String] ?? [:]}
  set{UserDefaults.standard.set(newValue,forKey:"NewGenSoundChoices")}
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
