import Foundation
import CryptoKit
@main struct Tests {
 static func main() throws {
  let fm = FileManager.default, root = fm.temporaryDirectory.appendingPathComponent("port-data-" + UUID().uuidString)
  try fm.createDirectory(at: root, withIntermediateDirectories: true)
  defer { try? fm.removeItem(at: root) }
  let base = root.appendingPathComponent("base.json"), folder = root.appendingPathComponent("data")
  try fm.createDirectory(at: folder, withIntermediateDirectories: true)
  let baseRows: [[Any]] = [["common/a", 2], ["x64/b.rpf", 3], ["x64/levels/env_test/c.rpf", 4]]
  let baseData = try JSONSerialization.data(withJSONObject: ["files": baseRows])
  try baseData.write(to: base)
  func hash(_ d: Data) -> String { SHA256.hash(data: d).map { String(format: "%02x", $0) }.joined() }
  func write(_ rows: [[Any]], baseHash: String? = nil, manifestHash: String? = nil) throws {
   let d = try JSONSerialization.data(withJSONObject: ["mount": "/game/", "files": rows])
   try d.write(to: folder.appendingPathComponent("manifest.json"))
   let marker = ["profile": "mugoat-port-converted-v1", "baseManifestSHA256": baseHash ?? hash(baseData), "manifestSHA256": manifestHash ?? hash(d)]
   try JSONSerialization.data(withJSONObject: marker).write(to: folder.appendingPathComponent(PortDataManifest.markerName))
  }
  func refused(_ rows: [[Any]], baseHash: String? = nil, manifestHash: String? = nil) throws {
   try write(rows, baseHash: baseHash, manifestHash: manifestHash)
   do { _ = try PortDataManifest.load(folder: folder, baseManifest: base); fatalError("accepted invalid dataset") } catch { }
  }
  let valid: [[Any]] = [["common/a", 8], ["x64/b.rpf", 9]]
  try write(valid); let loaded = try PortDataManifest.load(folder: folder, baseManifest: base)
  assert(loaded.files.count == 2 && loaded.files[1].1 == 9)
  try refused([["../a", 1], ["x64/b.rpf", 9]])
  try refused([["common/a", 8], ["common/a", 9]])
  try refused([["common/a", 8]])
  try refused([["x64/b.rpf", 9], ["common/a", 8]])
  try refused([["common/a", -1], ["x64/b.rpf", 9]])
  try refused([["common/a", true], ["x64/b.rpf", 9]])
  try refused([["common/a", 1.5], ["x64/b.rpf", 9]])
  try refused([["common/a", 3_000_000_000], ["x64/b.rpf", 9]])
  try refused(valid, baseHash: "wrong"); try refused(valid, manifestHash: "wrong")
  try fm.removeItem(at: folder.appendingPathComponent(PortDataManifest.markerName))
  assert(!PortDataManifest.hasMarker(folder))
  print("PASS converted manifest: exact engine identity/order, checksums, path safety, integral size, duplicate and corruption rejection")
 }
}
