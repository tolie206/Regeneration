import Foundation
/// One-time, atomic mod installs use the same validator as user imports.
/// The external game folder is never changed.
enum MuZomContent {
 static func prepare(archive:URL? = nil) throws {
  let fm=FileManager.default,docs=fm.urls(for:.documentDirectory,in:.userDomainMask)[0]
  let marker=docs.appendingPathComponent(".muzom-content-v2")
  let names=["_muzom_human","_muzom_docz","_muzom_guns"]
  let installed=Set(ModInstaller.installed().filter{$0.enabled}.map{$0.name})
  if fm.fileExists(atPath:marker.path),names.allSatisfy({installed.contains($0)}),fm.fileExists(atPath:docs.appendingPathComponent("MuZomAudio/groan0.wav").path){return}
  guard let zip=archive ?? Bundle.main.url(forResource:"MuZomContent",withExtension:"zip") else{throw ModError("Thiếu gói sinh tồn MuZom.")}
  let stage=try ModInstaller.unpack(zip);defer{try? fm.removeItem(at:stage)}
  for alias in ["mz_human","mz_docz"] {
   let name=alias=="mz_human" ? names[0]:names[1]
   if !installed.contains(name){let plan=try SkinInstaller.plan(folder:stage.appendingPathComponent(alias),name:name,female:false,modelName:alias);try ModInstaller.install(plan)}
  }
  if !installed.contains(names[2]){
   var plan=ModInstaller.Plan(name:names[2]);plan.kinds.insert("sound")
   let root=stage.appendingPathComponent("guns")
   guard let walk=fm.enumerator(at:root,includingPropertiesForKeys:[.isRegularFileKey]) else{throw ModError("Thiếu tiếng súng.")}
   for case let file as URL in walk where file.pathExtension.lowercased()=="awc" {let relative=String(file.path.dropFirst(root.path.count+1));plan.items.append(.init(source:file,target:relative,note:"MuZom sound-only; không thay sát thương"))}
   guard plan.items.count==24 else{throw ModError("Gói tiếng súng không đầy đủ.")};try ModInstaller.install(plan)
  }
  let audio=docs.appendingPathComponent("MuZomAudio");try fm.createDirectory(at:audio,withIntermediateDirectories:true)
  for i in 0..<8 {let data=try Data(contentsOf:stage.appendingPathComponent("groans/groan\(i).wav"));try data.write(to:audio.appendingPathComponent("groan\(i).wav"),options:.atomic)}
  try "2".write(to:marker,atomically:true,encoding:.utf8)
 }
}
