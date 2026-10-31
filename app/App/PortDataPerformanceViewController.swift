import UIKit
final class PortDataPerformanceViewController: UITableViewController {
    init() { super.init(style: .insetGrouped); title = "Tối ưu PortData" }
    required init?(coder: NSCoder) { fatalError() }
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int { PortDataPerformance.Mode.allCases.count }
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let mode = PortDataPerformance.Mode.allCases[indexPath.row], cell = UITableViewCell(style: .subtitle, reuseIdentifier: nil)
        cell.textLabel?.text = mode.title
        cell.detailTextLabel?.text = mode == .original ? "Dùng đúng thiết lập ở mục Đồ hoạ" : "Giảm texture, bóng, cỏ và tầm nhìn; đầu ra tối đa \(mode.heightCap)p"
        cell.detailTextLabel?.numberOfLines = 0
        cell.accessoryType = PortDataPerformance.mode == mode ? .checkmark : .none
        return cell
    }
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        PortDataPerformance.mode = PortDataPerformance.Mode.allCases[indexPath.row];tableView.reloadData()
    }
    override func tableView(_ tableView: UITableView, titleForFooterInSection section: Int) -> String? {
        "Áp dụng khi tắt hẳn rồi mở lại app. Khi bật, profile giới hạn các chi tiết cao hơn trong mục Đồ hoạ để giảm tải CPU/GPU và RAM. Không xóa cài đặt cũ; chọn Tắt để khôi phục. MSR vẫn hoạt động. Không tắt bảo vệ RAM, không bỏ vật thể nhiệm vụ. FPS thực tế phụ thuộc cảnh và nhiệt độ."
    }
}
