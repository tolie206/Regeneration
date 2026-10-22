import Foundation
/// Bundled mod overlays only; never writes the user's base game or save files.
enum BundledVietnamese {
 static func prepare() throws {
  let fm=FileManager.default,defaults=UserDefaults.standard
  let mode=defaults.object(forKey:"NewGenVietnameseMode")==nil ? 1:defaults.integer(forKey:"NewGenVietnameseMode")
  let root=ModInstaller.modsFolder,target=root.appendingPathComponent("_newgen_story_vietnamese")
  let marker=target.appendingPathComponent(".newgen-translation")
  let revision="1.4.4.1-\(mode)"
  if mode==0 {
   if fm.fileExists(atPath:marker.path){try fm.removeItem(at:target)};return
  }
  // Respect the mod manager's disabled state.
  if fm.fileExists(atPath:target.path+".off"){return}
  if (try? String(contentsOf:marker,encoding:.utf8))==revision{return}
  guard !fm.fileExists(atPath:target.path)||fm.fileExists(atPath:marker.path) else{throw ModError("Thư mục Việt hoá đã tồn tại nhưng không thuộc bản tích hợp; giữ nguyên để tránh mất dữ liệu.")}
  let resource=mode==2 ? "VietnamesePlain":"VietnameseAccented"
  guard let zip=Bundle.main.url(forResource:resource,withExtension:"zip") else{throw ModError("Thiếu Việt hoá tích hợp trong IPA.")}
  let unpacked=try ModInstaller.unpack(zip);defer{try? fm.removeItem(at:unpacked)}
  try revision.write(to:unpacked.appendingPathComponent(".newgen-translation"),atomically:true,encoding:.utf8)
  try fm.createDirectory(at:root,withIntermediateDirectories:true)
  let backup=root.appendingPathComponent(".newgen-translation-backup")
  if fm.fileExists(atPath:backup.path){throw ModError("Còn bản sao Việt hoá dự phòng; không ghi đè dữ liệu.")}
  let existed=fm.fileExists(atPath:target.path)
  if existed{try fm.moveItem(at:target,to:backup)}
  do {try fm.moveItem(at:unpacked,to:target)}
  catch{if existed{try? fm.moveItem(at:backup,to:target)};throw error}
  if existed{try? fm.removeItem(at:backup)}
 }
}
