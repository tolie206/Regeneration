# Mugoat Online O001 — nền online tách R007

## Quyết định kiến trúc

Dùng R007 b5b0d53d3d7440378b21ecc6f9f1a9916b629154 làm nền. Giữ CPU wasm2c, Metal, shaders, pipeline cache và chính sách bộ nhớ R007; thêm Rust staticlib cho mạng. Không mang renderer Wasmtime/wgpu hoặc các thử nghiệm streaming của Mugoat cũ sang.

Bản đầu chạy PC/LAN vì chưa có VPS. Tên người chơi chỉ là tên hiển thị, không phải tài khoản đã xác thực. Trước khi mở server công cộng phải có tài khoản/nhân vật lưu server, phiên đăng nhập an toàn, hạn mức gói tin, kiểm tra trạng thái/model và manifest tài nguyên server. Không dùng tên hoặc vai trò tự khai làm quyền quản trị.

## Sao lưu trước khi upstream đóng

Sao lưu ngoài checkout: `E:/New Project/Mugoat-Online/backups/mugoat-upstream-20261027.git` (mirror), và `.bundle` cùng tên (đủ lịch sử, đã `git bundle verify`). SHA256 bundle: `471dcb88fadb68691ae79d857340242aebc47b8a68c546794cddcd3fd676f96d`.

- main: 6f061d12c58c23dbf99da7d4225996a6d586ab89
- codex/native-hybrid-controls-online: 45db2646c903823af99dc53f18469f8c3b254379
- mugoat-r007-engine: cbc1b4b675bb54687889a105a95e78d83306d7e3

Không phụ thuộc upstream còn mở để khôi phục source. Giữ giấy phép và attribution trong network/LICENSE-upstream. Sáu repo tham khảo đã clone riêng ở `E:/New Project/Mugoat-Online/references`; manifest commit tại backups/backup-manifest.json.

## Đã triển khai trong bản nền

- App riêng `vn.gta.mugoat.online`, tên Mugoat Online; chỉ vào sandbox phục vụ kết nối online, khoá Story và test map.
- Cầu nối lệnh native có kiểm tra kiểu/tham số; metadata lấy từ engine gốc. Không sửa export/name Wasm làm đổi chỉ số hàm/globals của R007.
- Server UDP và logic đồng bộ người chơi/phương tiện kế thừa upstream; tên/phòng kết nối trong launcher.
- Không nạp Documents/Mods, không ASI/Menyoo, chặn API cheat/spawn/tiền phía client và cheat handler của engine. Việt hoá đọc từ tài nguyên đóng trong app.
- Server gán ID người gửi; từ chối lệnh tiền/vai trò tự khai của giao thức cũ, gói quá lớn và REL lồng nhau. Mặc định bind localhost; launcher server thử LAN chỉ chọn IP riêng.
- Tách RP domain SQLite: nhân vật, cash/bank, giao dịch có receipt, inventory và ví dụ job với chủ sở hữu, trả thưởng một lần. Có kiểm thử rollback, chống gửi lại và lưu qua restart.

## Giới hạn cần nói rõ

Đây chưa phải gamemode RP hoàn chỉnh. RP domain chưa nối RPC/UI gameplay: chưa có đăng nhập, garage, nhà, job chơi được hoặc admin panel. UDP hiện vẫn là relay trạng thái client, không phải mô phỏng authoritative hoàn chỉnh. Tài nguyên server ký/xác thực chưa có; vì vậy chưa cho mod cá nhân hay server skin trong O001. Chặn menu/plugin trong app không phải chống mọi client chỉnh sửa hoặc data game bị sửa. Ambient NPC, explosion/killfeed mở rộng và voice UI chưa được xác nhận trong fork này.

Test localhost hai socket không thay thế test hai iPhone. Cần kiểm tra thực tế spawn, di chuyển/lái xe, reconnect, FPS và phiên dài trên iPhone trước khi công bố ổn định hay mở public.

## Chạy thử

Dùng gói Windows LAN Release: mở PowerShell tại thư mục server, chạy `./Start-LAN.ps1`. Nếu có nhiều IP: `./Start-LAN.ps1 -BindAddress 192.168.1.10`. Script không tự mở firewall/router. Nếu Windows hỏi quyền mạng, chỉ cho mạng riêng mà bạn muốn thử. Hai điện thoại cùng Wi-Fi (không guest isolation), cấp Local Network cho app. Trong launcher chọn Máy chủ, nhập IP hiển thị kèm :47520, đặt tên rồi Chơi. Phòng cố định roleplay.

Nếu chưa kết nối server, điều khiển nhân vật bị khoá; bản này không dành chơi offline. Tắt hẳn app trước khi đổi máy chủ vì engine khởi tạo một lần.

## Tham khảo và lựa chọn

vRP modules/money.lua và identity.lua (MIT): tách identity khỏi tên hiển thị, wallet/bank thành module server. CloudRoleplay WorldSystems/BanksAtms (MIT): chia hệ thống ngân hàng và hành vi gameplay. qb-core server/player.lua (GPL3): vòng đời player và API tiền/job; ox_core lib/server/player.lua (LGPL3): player wrapper/state. ox_inventory modules/inventory/server.lua và qb-inventory server/functions.lua (GPL3): inventory ở server, thao tác chuyển đồ phải kiểm tra số lượng/chủ sở hữu và rollback. Các framework này dựa FiveM/RAGE MP, không chạy trực tiếp trên runtime Mugoat. Chỉ tham khảo tổ chức; core Rust mới không nhúng resource Lua/C# nguyên khối.

## Rollback

Nhánh offline và IPA R007 không bị sửa. Online nằm nhánh mugoat-online-rp-m0, bundle ID riêng; cài song song. Có thể quay về IPA R007 mà không đổi source offline. Backup source upstream độc lập như trên.
