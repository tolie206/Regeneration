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
 static var hideBikeBody:Bool {
  get {UserDefaults.standard.object(forKey:"V5HideBikeBody") == nil ? true:UserDefaults.standard.bool(forKey:"V5HideBikeBody")}
  set {UserDefaults.standard.set(newValue,forKey:"V5HideBikeBody");apply()}
 }
 static func apply(){PGSetVehicleEngineGain(engineDB);PGSetFirstPersonWide(wide);PGSetHideBikeBody(hideBikeBody ? 1:0)}
}
final class ExperienceSettingsViewController: UITableViewController {
 var cameraSelected:((NativeCheatAction)->Void)?
 init(){super.init(style:.insetGrouped);title="Tiếng xe và góc nhìn"}
 required init?(coder:NSCoder){fatalError()}
 override func viewDidLoad(){super.viewDidLoad();Theme.styleSettingsTable(tableView)}
 override func numberOfSections(in tableView:UITableView)->Int{4}
 override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int{[5,2,5,1][section]}
 override func tableView(_ tableView:UITableView,titleForHeaderInSection section:Int)->String?{["Âm lượng động cơ", "Đổi góc nhìn khi đang chơi", "Góc nhìn thứ nhất rộng (thử nghiệm)","Tránh cơ thể che camera xe máy"][section]}
 override func tableView(_ tableView:UITableView,titleForFooterInSection section:Int)->String?{
  ["Tăng kênh granular của động cơ xe gốc và xe mod, không tăng radio/hội thoại/còi. +6 dB khoảng gấp đôi biên độ. Nếu rè hãy giảm mức.","Camera native cho đi bộ và trong xe, giữ animation tay cầm súng/lái xe nếu model có hỗ trợ. Áp dụng sau khi đóng menu. Không ép camera cutscene.","Tăng FOV góc nhìn thứ nhất khi đi bộ và trong xe (kể cả xe máy). Giữ zoom ngắm xa, không ghi vào trạng thái camera gốc. FOV rộng có thể tốn thêm GPU. Đây là chế độ native, không chạy plugin .asi Windows.","Chỉ ẩn nhân vật của bạn trên máy này khi đang đi xe máy/môtô, nhìn thứ nhất và bật FOV rộng. Có thể ẩn cả tay và bóng/phản chiếu. Tự hiện lại khi đổi góc nhìn, xuống xe hoặc tắt FOV. Không thay texture, va chạm hay nhân vật của người khác."][section]
 }
 override func tableView(_ tableView:UITableView,cellForRowAt p:IndexPath)->UITableViewCell{
  let c=UITableViewCell(style:.default,reuseIdentifier:nil)
  if p.section==3 {
   c.textLabel?.text="Ẩn cơ thể khi đi xe máy (FOV rộng)"
   let toggle=UISwitch();toggle.isOn=ExperienceSettings.hideBikeBody
   toggle.addAction(UIAction {[weak toggle] _ in if let toggle {ExperienceSettings.hideBikeBody=toggle.isOn}},for:.valueChanged)
   c.accessoryView=toggle;c.selectionStyle = .none;return c
  }
  if p.section==0 {let db=Float(p.row*3);c.textLabel?.text=p.row==0 ? "Gốc (0 dB)" : "+\(Int(db)) dB";c.accessoryType=ExperienceSettings.engineDB==db ? .checkmark:.none}
  else if p.section==1 {c.textLabel?.text=p.row==0 ? "Góc nhìn thứ nhất" : "Góc nhìn thứ ba";c.isUserInteractionEnabled=ModInstaller.gameRunning;c.textLabel?.isEnabled=ModInstaller.gameRunning}
  else {let extra=Float(p.row*5);c.textLabel?.text=p.row==0 ? "FOV gốc" : "Rộng thêm \(Int(extra))°";c.accessoryType=ExperienceSettings.wide==extra ? .checkmark:.none}
  return c
 }
 override func tableView(_ tableView:UITableView,didSelectRowAt p:IndexPath){
  tableView.deselectRow(at:p,animated:true)
  if p.section==3{return}
  if p.section==0 {ExperienceSettings.engineDB=Float(p.row*3)}
  else if p.section==2 {ExperienceSettings.wide=Float(p.row*5)}
  else {cameraSelected?(NativeCheatAction(title:p.row==0 ? "Góc nhìn thứ nhất":"Góc nhìn thứ ba",command:PGCheatCameraMode,value:p.row==0 ? 4:1));return}
  tableView.reloadData()
 }
}
