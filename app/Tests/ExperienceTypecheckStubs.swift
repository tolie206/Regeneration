import UIKit
typealias PGCheatCommand = Int32
let PGCheatCameraMode:PGCheatCommand=5
func PGSetVehicleEngineGain(_ db:Float){}
func PGSetFirstPersonWide(_ degrees:Float){}
struct NativeCheatAction{let title:String;let command:PGCheatCommand;let value:Int32}
enum ModInstaller{static var gameRunning=false}
enum Theme{static func styleSettingsTable(_ table:UITableView){}}
