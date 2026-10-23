# MuLone-V006 — kết quả triển khai

Build Release thành công: https://github.com/Living-NG/GTA-NEW-GEN-2/actions/runs/39897220186
Source build: b52561d86d11159e6b4ce1779eddaeefe9df65f5. Một IPA duy nhất: MuLone-V006.ipa, app Mugoat NewGen, bundle vn.gta.newgen, build 1006.

## Đã làm
- Máy cài mới dùng mức đồ hoạ thấp nhất; giữ nguyên lựa chọn đã lưu của người dùng cũ.
- Áp dụng chính sách vùng địa chỉ engine đã đối chiếu IPA 1.4.7: tối đa 7 GiB khi ngân sách đủ lớn. Giữ guard theo RAM thực tế, dự phòng và cơ chế hạn chế streaming. Máy 4 GB không bị ép cấp phát thêm. Entitlement không phải lời hứa iOS cấp đủ mức RAM mong muốn.
- Script ASI được tiếp tục qua frame thay vì bị dừng khi hết một lượt xử lý; vẫn giới hạn callback và script chạy mãi không nhường.
- Nhập xe qua ZIP hoặc chọn nhiều file cùng lần. Bổ sung tra model xe gốc khi chỉ mục runtime thiếu; đưa xe replace vào danh sách xe mod.
- Sửa importer sound không duyệt nhầm RPF xe/ngôn ngữ không thuộc âm thanh trong DLC hỗn hợp. Bộ test đầu dừng ở lỗi bảng RPF mã hoá; sau sửa, toàn bộ ba gói mẫu qua.
- Việt hoá thêm 816 nhãn menu/map còn tiếng Anh, tương ứng 79 nội dung khác nhau. Chọn đúng archive ngôn ngữ khi bật Việt hoá tích hợp.
- Nhập save bằng folder/ZIP/RAR: chỉ lấy save SGTA5 hợp lệ vào ô trống; không chép pc_settings.bin hoặc settings.xml từ gói ngoài. Không xoá hay ghi đè save cũ.
- Tích hợp Menyoo 1.0.5 và bản dịch 234 mục từ từ điển mẫu, kèm lựa chọn không dấu và giấy phép gốc. Mặc định tắt để tránh thêm tải CPU khi không dùng. Thêm nút Plugin trên HUD.
- Đổi độ phân giải khi đang chơi sẽ lưu cho lần khởi động sau, tránh thay backbuffer đang dùng.
- Không sửa thuật toán renderer Metal, texture hoặc luồng render cốt lõi; giữ Xcode 26.2 build 17C52/SDK 26.2.

## Đã kiểm chứng
- Toàn bộ 17 bước workflow thành công, gồm kiểm thử và build/kiểm tra IPA.
- Maybach: chọn cùng ba file và ZIP đều tạo đúng kế hoạch thay tailgater.
- Lamborghini HAMMER Legacy và gói 27rev được nhận; HAMMER Enhanced bị từ chối.
- Benze55 ZIP: 1 profile; H2R ZIP: 1 profile; Aquaphobic RAR: 13 profile.
- Save thật trong mẫu EngineFiles được nhập mà không đổi cấu hình người chơi hiện có.
- Bộ test trước đó về native REL54, giữ nguyên AWC, xung đột bank, metadata xe, vụ nổ, phụ đề có/không dấu đều qua.
- IPA tải về đúng ARM64, bundle/build, toolchain, entitlement RAM và CRC/inventory của gói Việt hoá/Menyoo. Không chứa bộ mod/save dùng kiểm thử.

## Cách thử
1. Ký/cài MuLone-V006.ipa bằng ESign như trước. Để so FPS, trước tiên giữ Menyoo tắt và dùng cùng thiết lập/đường chạy.
2. Cài Maybach bằng ZIP hoặc chọn cả ba file trong một lần ở mục nhập mod. Nhập Lamborghini bằng bản Legacy, không dùng Enhanced.
3. Nhập gói sound riêng ở mục âm thanh, chọn xe đã mod rồi chọn profile; mở lại app sau khi nhập gói.
4. Bật Menyoo trong Cài đặt → Plugin Menyoo, tắt hẳn/mở lại app. Trong game nhấn Plugin → F8. Dùng bàn phím số của khay plugin để điều khiển.
5. Nhập save bằng mục nhập save của app thay vì chép cả EngineFiles. Nếu không hiện phụ đề, kiểm tra tuỳ chọn Phụ đề trong cài đặt game.

## Giới hạn còn lại
Đây là kiểm thử importer và build, chưa phải chơi thử trên iPhone. Cần tester xác nhận model xuất hiện, tiếng phát đúng, Menyoo chạy và FPS thực tế. Plugin ASI dùng trình thông dịch nên có thể tốn CPU; bật nhiều tính năng có thể giảm FPS. Chưa có cơ sở hứa 60 FPS hay toàn bộ Menyoo hoạt động.

Việt hoá chưa phủ mọi nhãn/tên riêng. Đường nhập save mới bảo vệ cấu hình; chưa thể khẳng định mọi trường hợp chép thủ công profile ngoài vào app đã được giải quyết. Không sửa offset cấu hình chưa được xác minh.

Chính iOS/chứng chỉ/profile và áp lực bộ nhớ quyết định RAM thực dùng. iPad 16 GB không đồng nghĩa app được dùng cả 16 GB. Những sửa camera trực thăng, tiếng Trung và tối ưu mỗi frame chưa xác minh của 1.4.7 không được ghép mù từ IPA.

SHA-256 IPA: `0ffa63d3c000ef7c067b878318b4d36d2666669b54479114e6a8cc8595bc6832`
