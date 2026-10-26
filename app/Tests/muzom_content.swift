import Foundation
@main struct MuZomContentTest {
 static func main() throws {
  let fm=FileManager.default,zip=URL(fileURLWithPath:CommandLine.arguments[1]),docs=fm.urls(for:.documentDirectory,in:.userDomainMask)[0]
  try MuZomContent.prepare(archive:zip)
  let names=SkinInstaller.models();precondition(names.contains("mz_human")&&names.contains("mz_docz"))
  let mods=ModInstaller.installed().filter{$0.name.hasPrefix("_muzom_")};precondition(mods.count==3&&mods.allSatisfy{$0.enabled})
  for mod in mods where mod.name != "_muzom_guns" {
   let files=(fm.enumerator(at:mod.url,includingPropertiesForKeys:nil)!.allObjects as! [URL]).filter{$0.lastPathComponent=="dlc.rpf"};precondition(files.count==1)
   let rpf=try RPFArchive(url:files[0]),ped=try rpf.nested(rpf.entries.first{$0.path=="peds.rpf"}!)
   precondition(ped.entries.filter{$0.resourceVersion != nil}.count==4)
   let meta=String(data:try rpf.metadata(rpf.entries.first{$0.path=="peds.meta"}!),encoding:.utf8)!;precondition(meta.contains("mz_"))
  }
  let guns=mods.first{$0.name=="_muzom_guns"}!
  let banks=(fm.enumerator(at:guns.url,includingPropertiesForKeys:nil)!.allObjects as! [URL]).filter{$0.pathExtension=="awc"};precondition(banks.count==24)
  for bank in banks {let bytes=try Data(contentsOf:bank);precondition(bytes.prefix(4)==Data("ADAT".utf8))}
  for i in 0..<8 {precondition(fm.fileExists(atPath:docs.appendingPathComponent("MuZomAudio/groan\(i).wav").path))}
  let before=try fm.attributesOfItem(atPath:banks[0].path)[.modificationDate] as! Date
  try MuZomContent.prepare(archive:zip)
  let after=try fm.attributesOfItem(atPath:banks[0].path)[.modificationDate] as! Date;precondition(after==before)
  print("PASS actual bundled content: 2 complete validated peds, 24 sound-only banks, 8 WAV, idempotent install")
 }
}
