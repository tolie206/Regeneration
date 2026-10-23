import UIKit
final class BundledMenyooViewController:UITableViewController {
 init(){super.init(style:.insetGrouped);title="Plugin Menyoo"}
 required init?(coder:NSCoder){fatalError()}
 override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int{1}
 override func tableView(_ tableView:UITableView,cellForRowAt indexPath:IndexPath)->UITableViewCell{
  let cell=UITableViewCell(style:.default,reuseIdentifier:nil);cell.textLabel?.text="Bật Menyoo tích hợp"
  let toggle=UISwitch();toggle.isOn=BundledMenyoo.enabled
  toggle.addAction(UIAction{action in guard let toggle=action.sender as? UISwitch else{return};UserDefaults.standard.set(toggle.isOn,forKey:"NewGenMenyooEnabled")},for:.valueChanged)
  cell.accessoryView=toggle;cell.selectionStyle = .none;return cell
 }
 override func tableView(_ tableView:UITableView,titleForFooterInSection section:Int)->String?{
  "Áp dụng sau khi tắt hẳn và mở lại app. Trong game: Plugin → F8 để mở Menyoo, dùng bàn phím số để chọn. Bản dịch tiếng Việt nằm trong Settings → Language của Menyoo. Menyoo mặc định tắt; bật plugin có thể tốn CPU/RAM. Không bật hiệu ứng hoặc tăng mật độ NPC nếu cần giữ FPS. Không dùng đồng thời một bản Menyoo khác."
 }
}
