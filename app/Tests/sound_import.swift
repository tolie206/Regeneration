import Foundation
#if canImport(FoundationXML)
import FoundationXML
#endif
@main struct SoundTest {
 static func main() throws {
  let fm=FileManager.default,fixture=URL(fileURLWithPath:CommandLine.arguments[1])
  let stage=try SoundInstaller.stage([fixture]);defer{try? fm.removeItem(at:stage)}
  let (plan,profiles)=try SoundInstaller.build(stage)
  precondition(profiles==["ta103ninjah2r"])
  let archive=try RPFArchive(url:plan.items.first!.source)
  let rel=archive.entries.first{$0.path=="audioconfig/ta103ninjah2r_sounds.dat54.rel"}!
  let native=archive.entries.first{$0.path=="audioconfig/ta103ninjah2r_sounds.dat54"}!
  let original=try archive.binary(rel),converted=try archive.binary(native)
  let expected=try ModAudio.nativeSoundData(original);precondition(converted==expected);precondition(original != converted)
  let bank=archive.entries.first{$0.path=="sfx/dlc_ta103ninjah2r/ta103ninjah2r.awc"}!
  let got=try archive.binary(bank),source=try Data(contentsOf:fixture.appendingPathComponent("sfx/dlc_ta103ninjah2r/ta103ninjah2r.awc"));precondition(got==source)
  for name in ["setup2.xml","content.xml"] {
   let e=archive.entries.first{$0.path==name}!;let xml=try archive.metadata(e);precondition(XMLParser(data:xml).parse())
  }
  let bad=stage.appendingPathComponent("audioconfig");try fm.createDirectory(at:bad,withIntermediateDirectories:true)
  try Data([54,0,0,0]).write(to:bad.appendingPathComponent("broken_sounds.dat54.rel"))
  do{_ = try SoundInstaller.build(stage);fatalError("truncated REL accepted")}catch is ModError{}
  print("PASS: actual H2R FiveM folder import, native REL54 alias, unchanged AWC, valid DLC XML and corrupt input rejection")
 }
}
