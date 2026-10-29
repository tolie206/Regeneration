import Foundation

/// MSR modes are independent of the detail preset and apply at the next start.
enum MSRMode:Int,CaseIterable {
 case off=0,quality,balanced,performance
 var title:String { ["Tắt (độ phân giải gốc)","MSR Chất lượng · 85%","MSR Cân bằng · 75%","MSR Hiệu năng · 67%"][rawValue] }
 var scale:Double { [1,0.85,0.75,0.67][rawValue] }
 func renderSize(outputWidth:Int,outputHeight:Int)->(Int,Int) {
  guard self != .off else{return(outputWidth,outputHeight)}
  let factor=max(scale,max(320.0/Double(max(1,outputWidth)),180.0/Double(max(1,outputHeight))))
  return(max(320,Int((Double(outputWidth)*factor).rounded()) & ~1),max(180,Int((Double(outputHeight)*factor).rounded()) & ~1))
 }
}
extension GameSettings {
 var msrMode:MSRMode {
  get {MSRMode(rawValue:UserDefaults.standard.integer(forKey:"V5MSRMode")) ?? .off}
  set {UserDefaults.standard.set(newValue.rawValue,forKey:"V5MSRMode")}
 }
 var offlinePerfReports:Bool {
  get {UserDefaults.standard.bool(forKey:"V5OfflinePerfReports")}
  set {UserDefaults.standard.set(newValue,forKey:"V5OfflinePerfReports")}
 }
}
