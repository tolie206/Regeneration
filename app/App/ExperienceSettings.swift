import UIKit

enum ExperienceSettings {
 static var engineDB: Float {
  get { UserDefaults.standard.object(forKey:"V5EngineGainDB") == nil ? 6 : min(12,max(0,UserDefaults.standard.float(forKey:"V5EngineGainDB"))) }
  set { UserDefaults.standard.set(newValue,forKey:"V5EngineGainDB");apply() }
 }
 static var wide: Float {
  get { min(20,max(0,UserDefaults.standard.float(forKey:"V5FirstPersonExtra"))) }
  set { UserDefaults.standard.set(newValue,forKey:"V5FirstPersonExtra");apply() }
 }
 static func apply(){PGSetVehicleEngineGain(engineDB);PGSetFirstPersonWide(wide)}
}
final class ExperienceSettingsViewController: UITableViewController {
 var cameraSelected:((NativeCheatAction)->Void)?
 init(){super.init(style:.insetGrouped);title="Tiếng xe và góc nhìn"}
 required init?(coder:NSCoder){fatalError()}
 override func viewDidLoad(){super.viewDidLoad();Theme.styleSettingsTable(tableView)}
 override func numberOfSections(in tableView:UITableView)->Int{3}
 override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int{[5,2,5][section]}
 override func tableView(_ tableView:UITableView,titleForHeaderInSection section:Int)->String?{["Âm lượng động cơ", "Đổi góc nhìn khi đang chơi", "Góc nhìn thứ nhất rộng (thử nghiệm)"][section]}
 override func tableView(_ tableView:UITableView,titleForFooterInSection section:Int)->String?{
  ["Chỉ tăng tiếng động cơ xe gốc và xe mod, không tăng radio/hội thoại/còi. +6 dB khoảng gấp đôi biên độ. Nếu rè hãy giảm mức.","Camera native cho đi bộ và trong xe, giữ animation tay cầm súng/lái xe nếu model có hỗ trợ. Áp dụng sau khi đóng menu. Không ép camera cutscene.","Tăng FOV đi bộ, không thay zoom ngắm xa hoặc FOV trong xe. FOV rộng có thể tốn thêm GPU. Đây là chế độ native, không chạy plugin .asi Windows."][section]
 }
 override func tableView(_ tableView:UITableView,cellForRowAt p:IndexPath)->UITableViewCell{
  let c=UITableViewCell(style:.default,reuseIdentifier:nil)
  if p.section==0 {let db=Float(p.row*3);c.textLabel?.text=p.row==0 ? "Gốc (0 dB)" : "+\(Int(db)) dB";c.accessoryType=ExperienceSettings.engineDB==db ? .checkmark:.none}
  else if p.section==1 {c.textLabel?.text=p.row==0 ? "Góc nhìn thứ nhất" : "Góc nhìn thứ ba";c.isUserInteractionEnabled=ModInstaller.gameRunning;c.textLabel?.isEnabled=ModInstaller.gameRunning}
  else {let extra=Float(p.row*5);c.textLabel?.text=p.row==0 ? "FOV gốc" : "Rộng thêm \(Int(extra))°";c.accessoryType=ExperienceSettings.wide==extra ? .checkmark:.none}
  return c
 }
 override func tableView(_ tableView:UITableView,didSelectRowAt p:IndexPath){
  tableView.deselectRow(at:p,animated:true)
  if p.section==0 {ExperienceSettings.engineDB=Float(p.row*3)}
  else if p.section==2 {ExperienceSettings.wide=Float(p.row*5)}
  else {cameraSelected?(NativeCheatAction(title:p.row==0 ? "Góc nhìn thứ nhất":"Góc nhìn thứ ba",command:PGCheatCameraMode,value:p.row==0 ? 4:1));return}
  tableView.reloadData()
 }
}
