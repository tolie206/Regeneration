import UIKit
struct AppLanguage {static func choose(_ s:String)->String{s};static func interpolate(_ s:String,_ args:[String])->String{s}}
struct GameMode {var title:String;static let allCases=[GameMode(title:"Cốt truyện"),GameMode(title:"Tự do")]}
final class GameSettings {static let sandboxMapTitles=["GTA V","Thử nghiệm"]}
