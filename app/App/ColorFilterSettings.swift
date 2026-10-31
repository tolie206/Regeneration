import UIKit

enum ColorFilterSettings {
 static let titles=["Tắt — màu gốc","Tự nhiên (khuyên dùng)","Cây cối tươi hơn","Rực rỡ nhẹ"]
 static var mode:Int {
  get {min(3,max(0,UserDefaults.standard.integer(forKey:"V5ColorFilter")))}
  set {UserDefaults.standard.set(newValue,forKey:"V5ColorFilter");apply()}
 }
 static func apply(){PGSetColorFilter(Int32(mode))}
}
final class ColorFilterViewController:UITableViewController {
 init(){super.init(style:.insetGrouped);title="Filter màu cảnh quan"}
 required init?(coder:NSCoder){fatalError()}
 override func viewDidLoad(){super.viewDidLoad();Theme.styleSettingsTable(tableView)}
 override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int{ColorFilterSettings.titles.count}
 override func tableView(_ tableView:UITableView,titleForFooterInSection section:Int)->String?{
  "Áp dụng ngay, có lưu lựa chọn. Không thêm lượt render, texture hay hiệu ứng nặng; vẫn cần đo FPS trên iPhone. Màu xanh được nhận diện theo màu pixel nên xe/quần áo xanh và HUD cũng có thể thay đổi. Không thay texture, ánh sáng hoặc thời tiết. Chọn Tắt để về màu gốc."
 }
 override func tableView(_ tableView:UITableView,cellForRowAt p:IndexPath)->UITableViewCell{
  let c=UITableViewCell(style:.default,reuseIdentifier:nil);c.textLabel?.text=ColorFilterSettings.titles[p.row];c.accessoryType=ColorFilterSettings.mode==p.row ? .checkmark:.none;return c
 }
 override func tableView(_ tableView:UITableView,didSelectRowAt p:IndexPath){
  tableView.deselectRow(at:p,animated:true);ColorFilterSettings.mode=p.row;tableView.reloadData()
 }
}
