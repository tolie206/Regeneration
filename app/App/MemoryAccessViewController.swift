import UIKit
import os
/// Reports actual process headroom; never pretends a UI action grants an iOS entitlement.
final class MemoryAccessViewController: UITableViewController {
 private var tier=DeviceTier.probe()
 private let running:Bool
 init(engineRunning:Bool){running=engineRunning;super.init(style:.insetGrouped);title="RAM và quyền bộ nhớ"}
 required init?(coder:NSCoder){fatalError("init(coder:) has not been implemented")}
 override func viewDidLoad(){super.viewDidLoad();Theme.styleSettingsTable(tableView)}
 override func numberOfSections(in tableView:UITableView)->Int{1}
 override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int{6}
 override func tableView(_ tableView:UITableView,cellForRowAt indexPath:IndexPath)->UITableViewCell{
  let cell=UITableViewCell(style:.subtitle,reuseIdentifier:nil);var c=cell.defaultContentConfiguration()
  switch indexPath.row {
  case 0:
   c.text="RAM iOS đang cho phép (ước tính)";c.secondaryText="\(tier.memoryLimitMB) MiB · RAM máy \(tier.physicalMemoryMB) MiB. Thay đổi theo thiết bị, chữ ký và áp lực bộ nhớ."
  case 1:
   c.text="Quyền tăng RAM trên bản đã cài"
   c.secondaryText=DeviceTier.increasedMemoryGranted.map{$0 ? "Có entitlement tăng RAM trong chữ ký.":"Không thấy entitlement tăng RAM trong chữ ký. Cần kiểm tra khi ký lại."} ?? "Không đọc được entitlement của bản đã cài."
  case 2:
   c.text="Kiểm tra lại quyền và RAM";c.secondaryText="Đo lại bộ nhớ hiện tại; không cấp quyền giả và không ép cấp phát RAM.";cell.accessoryType = .disclosureIndicator
  case 3:
   let cap=GameSettings.shared.memoryCapMB
   c.text="Dùng toàn bộ RAM iOS cho phép";c.secondaryText=cap==0 ? "Đang tự động: không đặt cap riêng trong app. Vùng nhớ engine ~4 GiB KHÁC tổng RAM của app.":"Cap hiện tại \(cap) MiB. Nhấn để về Tự động; áp dụng lần mở game tiếp theo."
   cell.accessoryType = cap==0 ? .checkmark:.disclosureIndicator
  case 4:
   c.text="Xuất file quyền RAM để ký lại";c.secondaryText="Chia sẻ plist entitlement cho công cụ ký hỗ trợ. Chứng chỉ/profile phải cho phép; không có hộp thoại xin RAM của iOS.";cell.accessoryType = .disclosureIndicator
  default:
   c.text="Vì sao không tự nâng lên 5 GB?";c.secondaryText="App đã yêu cầu increased-memory-limit và extended-virtual-addressing trong IPA. iOS quyết định mức thực tế. Nút bên trên không thay chữ ký, không bypass giới hạn và không đổi giới hạn engine để tránh crash."
  }
  c.textProperties.color=Theme.text;c.secondaryTextProperties.color=Theme.secondaryText;c.secondaryTextProperties.numberOfLines=0;cell.contentConfiguration=c;return cell
 }
 override func tableView(_ tableView:UITableView,didSelectRowAt indexPath:IndexPath){
  tableView.deselectRow(at:indexPath,animated:true)
  if indexPath.row==2 {tier=DeviceTier.probe();GameSettings.shared.tier=tier;tableView.reloadData()}
  if indexPath.row==3 {GameSettings.shared.memoryCapMB=0;tableView.reloadData();if running{let a=UIAlertController(title:"Đã chọn RAM tự động",message:"Áp dụng lần mở game tiếp theo. Quyền iOS không thay đổi trong phiên đang chạy.",preferredStyle:.alert);a.addAction(UIAlertAction(title:"OK",style:.default));present(a,animated:true)}}
  if indexPath.row==4 {
   let values:[String:Bool]=["com.apple.developer.kernel.increased-memory-limit":true,"com.apple.developer.kernel.extended-virtual-addressing":true]
   let url=FileManager.default.temporaryDirectory.appendingPathComponent("Mugoat-NewGen-RAM.entitlements")
   do{let data=try PropertyListSerialization.data(fromPropertyList:values,format:.xml,options:0);try data.write(to:url,options:.atomic)
    let share=UIActivityViewController(activityItems:[url],applicationActivities:nil);share.popoverPresentationController?.sourceView=tableView.cellForRow(at:indexPath);present(share,animated:true)
   }catch{let a=UIAlertController(title:"Không thể xuất file",message:error.localizedDescription,preferredStyle:.alert);a.addAction(UIAlertAction(title:"OK",style:.default));present(a,animated:true)}
  }
 }
}
