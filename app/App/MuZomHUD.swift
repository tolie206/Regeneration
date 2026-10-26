import UIKit
/// A small, throttled overlay; engine actions go through a bounded atomic mailbox.
final class MuZomHUD: UIView {
 private let status=UILabel(),objective=UILabel(),button=UIButton(type:.system)
 private let hunger=UIProgressView(progressViewStyle:.default),thirst=UIProgressView(progressViewStyle:.default)
 private weak var owner:UIViewController?
 private var snapshot=PGZombieHUD()
 func attach(to owner:UIViewController){
  self.owner=owner;translatesAutoresizingMaskIntoConstraints=false;owner.view.addSubview(self)
  backgroundColor=UIColor.black.withAlphaComponent(0.55);layer.cornerRadius=8
  status.font = .monospacedDigitSystemFont(ofSize:11,weight:.semibold);status.textColor = .white;status.adjustsFontSizeToFitWidth=true;status.minimumScaleFactor=0.75
  objective.font = .systemFont(ofSize:11);objective.textColor = .white;objective.numberOfLines=2
  hunger.progressTintColor = .systemOrange;thirst.progressTintColor = .systemCyan
  button.setTitle("Sinh tồn / Tương tác",for:.normal);button.titleLabel?.font = .systemFont(ofSize:12,weight:.semibold);button.addTarget(self,action:#selector(menu),for:.touchUpInside)
  let stack=UIStackView(arrangedSubviews:[status,hunger,thirst,objective,button]);stack.axis = .vertical;stack.spacing=4;stack.translatesAutoresizingMaskIntoConstraints=false;addSubview(stack)
  NSLayoutConstraint.activate([topAnchor.constraint(equalTo:owner.view.safeAreaLayoutGuide.topAnchor,constant:4),centerXAnchor.constraint(equalTo:owner.view.centerXAnchor),widthAnchor.constraint(equalToConstant:285),stack.topAnchor.constraint(equalTo:topAnchor,constant:6),stack.bottomAnchor.constraint(equalTo:bottomAnchor,constant:-4),stack.leadingAnchor.constraint(equalTo:leadingAnchor,constant:8),stack.trailingAnchor.constraint(equalTo:trailingAnchor,constant:-8)])
  isHidden=true
 }
 private var mission:String {
  switch snapshot.stage {
  case 0:return "1. Đến trại Legion Square (−172, −880), bấm Tương tác."
  case 1:return "2. Lấy túi y tế tại bệnh viện Pillbox (310, −593), bấm Tương tác."
  case 2:return "3. Hạ 5 zombie ban đêm: \(min(snapshot.kills,5))/5."
  case 3:return "4. Trở về trại Legion Square để nhận thưởng."
  default:return "Tiếp tục sinh tồn. Biểu tượng xanh lá dưới đất là vật phẩm."
  }
 }
 func refresh(active:Bool){
  var next=PGZombieHUD();let ready=PGZombieRead(&next);snapshot=next;isHidden = !active || !ready
  guard !isHidden else{return}
  status.text="\(next.night != 0 ? "Đêm":"Ngày") · \(max(0,next.minutes)) phút | Đói \(next.hunger)% · Khát \(next.thirst)% | $\(next.cash)"
  hunger.progress=Float(next.hunger)/100;thirst.progress=Float(next.thirst)/100;objective.text=mission + (next.notice == 1 ? " Không đủ vật phẩm/tiền hoặc chưa đúng vị trí." : next.notice == 2 ? " Đã nhặt đồ." : next.notice == 3 ? " Đã cập nhật nhiệm vụ." : "")
  button.setTitle(next.loot != 0 ? "Nhặt vật phẩm / Sinh tồn":next.shop != 0 ? "Cửa hàng / Sinh tồn":"Sinh tồn / Tương tác",for:.normal)
 }
 @objc private func menu(){
  guard let owner,owner.presentedViewController==nil else{return}
  let message=mission+"\nThức ăn: \(snapshot.food) · Nước: \(snapshot.water) · Y tế: \(snapshot.medkits)\nCửa hàng: trại Legion Square. Trò chơi vẫn tiếp diễn khi mở menu."
  let sheet=UIAlertController(title:"MuZom — Sinh tồn",message:message,preferredStyle:.actionSheet)
  func add(_ title:String,_ code:Int32){sheet.addAction(UIAlertAction(title:title,style:.default){_ in _=PGZombieAction(code)})}
  add("Tương tác / Nhặt vật phẩm",4);add("Ăn (+40) — còn \(snapshot.food)",1);add("Uống (+45) — còn \(snapshot.water)",2);add("Dùng túi y tế (+50 máu)",3)
  if snapshot.shop != 0 {add("Mua thức ăn — $15",10);add("Mua nước — $10",11);add("Mua y tế — $35",12);add("Mua 24 đạn lục — $25",13);add("Mua shotgun + 32 đạn — $180",14);add("Mua Micro SMG + 90 đạn — $250",15);add("Mua 24 đạn shotgun — $40",16);add("Mua 60 đạn SMG — $45",17)}
  sheet.addAction(UIAlertAction(title:"Đóng",style:.cancel));sheet.popoverPresentationController?.sourceView=button;sheet.popoverPresentationController?.sourceRect=button.bounds;owner.present(sheet,animated:true)
 }
}
