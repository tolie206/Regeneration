import Foundation
import CryptoKit

enum BundledOptimizer {
 static let name="Mugoat-V5-OPTIMIZER"
 static let file="Mugoat-PortLike-Traffic-v1.oiv"
 static let installedKey="V5BundledOptimizerInstalled"
 static let sha="bb62bf8f4489ad8ada764552aa03792618ad301c8fedda606af264d65ff0873c"
 // Startup only, before NativeAssets reads Mods. A removed/disabled mod stays so.
 static func prepare(source:URL?=Bundle.main.url(forResource:"Mugoat-PortLike-Traffic-v1",withExtension:"oiv"),root:URL=ModInstaller.modsFolder,defaults:UserDefaults = .standard)throws->String {
  let fm=FileManager.default,on=root.appendingPathComponent(name),off=root.appendingPathComponent(name+".off")
  if fm.fileExists(atPath:on.path)||fm.fileExists(atPath:off.path){defaults.set(true,forKey:installedKey);return "Optimizer: gói đã có, giữ trạng thái bật/tắt và dữ liệu hiện tại."}
  if defaults.bool(forKey:installedKey){return "Optimizer: đã gỡ; không tự cài lại."}
  guard let source else{throw ModError("Thiếu optimizer tích hợp.")}
  let data=try Data(contentsOf:source)
  let hash=SHA256.hash(data:data).map{String(format:"%02x",$0)}.joined()
  guard hash==sha else{throw ModError("Optimizer không đúng bản đã kiểm thử; không cài.")}
  try fm.createDirectory(at:root,withIntermediateDirectories:true)
  let stage=root.appendingPathComponent(".optimizer-"+UUID().uuidString)
  try fm.createDirectory(at:stage,withIntermediateDirectories:false)
  defer{try? fm.removeItem(at:stage)}
  try data.write(to:stage.appendingPathComponent(file),options:.atomic)
  try fm.moveItem(at:stage,to:on)
  defaults.set(true,forKey:installedKey)
  return "Optimizer: tích hợp xe lưu thông tối đa20, xe đỗ15; tắt/gỡ tại Quản lý mod, áp dụng khi mở lại app."
 }
}
