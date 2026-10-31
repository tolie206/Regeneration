import Foundation
struct ModError:Error {let message:String;init(_ s:String){message=s}}
enum ModInstaller{static var modsFolder:URL {FileManager.default.temporaryDirectory.appendingPathComponent("unused-optimizer-root")}}
@main struct Tests {
 static func main() throws {
  let fm=FileManager.default,root=fm.temporaryDirectory.appendingPathComponent("optimizer-test-"+UUID().uuidString)
  let suite="optimizer-"+UUID().uuidString,d=UserDefaults(suiteName:suite)!
  defer{try? fm.removeItem(at:root);d.removePersistentDomain(forName:suite)}
  let source=URL(fileURLWithPath:CommandLine.arguments[1]),on=root.appendingPathComponent(BundledOptimizer.name),off=root.appendingPathComponent(BundledOptimizer.name+".off")
  _=try BundledOptimizer.prepare(source:source,root:root,defaults:d)
  let installed=try Data(contentsOf:on.appendingPathComponent(BundledOptimizer.file)),original=try Data(contentsOf:source);assert(installed==original)
  try fm.moveItem(at:on,to:off);_=try BundledOptimizer.prepare(source:source,root:root,defaults:d);assert(fm.fileExists(atPath:off.path) && !fm.fileExists(atPath:on.path))
  try fm.removeItem(at:off);_=try BundledOptimizer.prepare(source:source,root:root,defaults:d);assert(!fm.fileExists(atPath:on.path))
  d.removeObject(forKey:BundledOptimizer.installedKey);try fm.createDirectory(at:on,withIntermediateDirectories:true)
  let custom=on.appendingPathComponent("custom.txt");try Data("keep".utf8).write(to:custom)
  _=try BundledOptimizer.prepare(source:source,root:root,defaults:d);assert(fm.fileExists(atPath:custom.path));assert(!fm.fileExists(atPath:on.appendingPathComponent(BundledOptimizer.file).path))
  print("PASS bundled optimizer exact bytes, disabled/removal honored, existing mod never overwritten")
 }
}
