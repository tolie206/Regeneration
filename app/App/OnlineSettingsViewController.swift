import UIKit
import Darwin
enum OnlineSettings {
 static var server:String {get{UserDefaults.standard.string(forKey:"OnlineRPServer") ?? ""}set{UserDefaults.standard.set(newValue,forKey:"OnlineRPServer")}}
 static var name:String {get{UserDefaults.standard.string(forKey:"OnlineRPName") ?? "Player"}set{UserDefaults.standard.set(newValue,forKey:"OnlineRPName")}}
 static func configure()->Bool{
  guard !server.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty else{return false}
  setenv("MUGUET_PVP","0",1)
  return server.withCString{s in name.withCString{n in "roleplay".withCString{room in MugoatOnlineConfigure(s,n,room,2)}}}
 }
}
final class OnlineSettingsViewController:UIViewController{
 private let server=UITextField(),name=UITextField()
 override func viewDidLoad(){super.viewDidLoad();title="Máy chủ Roleplay";view.backgroundColor = .systemBackground
  server.placeholder="IP máy chủ:47520";server.text=OnlineSettings.server;server.autocapitalizationType = .none;server.autocorrectionType = .no
  name.placeholder="Tên người chơi";name.text=OnlineSettings.name
  for field in [server,name]{field.borderStyle = .roundedRect}
  let note=UILabel();note.numberOfLines=0;note.text="Bản thử nghiệm PC/LAN. IP là địa chỉ của máy chạy server, không phải IP điện thoại. Chưa có hệ thống tài khoản production; không nhập mật khẩu tại đây."
  let button=UIButton(type:.system);button.setTitle("Lưu máy chủ",for:.normal);button.addTarget(self,action:#selector(save),for:.touchUpInside)
  let stack=UIStackView(arrangedSubviews:[server,name,note,button]);stack.axis = .vertical;stack.spacing=16;stack.translatesAutoresizingMaskIntoConstraints=false;view.addSubview(stack)
  NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.leadingAnchor,constant:20),stack.trailingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.trailingAnchor,constant:-20),stack.topAnchor.constraint(equalTo:view.safeAreaLayoutGuide.topAnchor,constant:20)])
 }
 @objc private func save(){OnlineSettings.server=server.text ?? "";OnlineSettings.name=name.text ?? "Player";dismiss(animated:true)}
}
