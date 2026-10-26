# MuZom V002 — triển khai và kiểm thử

## Nguyên nhân từ log V001

- A13: quota app khoảng 2098 MiB, headroom 145–218 MiB. Ngưỡng cũ reserve + 128 MiB ngừng bổ sung zombie sau khi giết hoặc rời khu vực. Không phải bằng chứng máy thiếu tổng RAM vật lý.
- Điểm sinh chỉ cách vị trí cũ 30–49 m, không dự đoán xe chạy; model pending có thể bị bỏ lại phía sau.
- Pool cũ chứa người thường. Xoá truy nã chỉ chạy một lần. Không có groans, nhiệm vụ hay kinh tế sinh tồn.
- A13 còn dùng 720p/unlocked và log báo nhiệt cao, GPU frame time cao. Các thay đổi gameplay không thể bảo đảm 60 FPS ở cấu hình đó.

## Cách chơi

Chỉ có Zombie. Tìm đường GPS đến trại Legion Square; bấm **Sinh tồn / Tương tác** để nhận nhiệm vụ. Lấy đồ ở Pillbox, hạ 5 zombie rồi trở về. Cửa hàng chỉ giao dịch trong 12 m quanh trại. Vật phẩm đánh dấu xanh lá, nhặt trong 5 m. Ăn/uống/y tế qua menu sinh tồn; game vẫn chạy khi mở menu.

Đêm 15 phút, ngày 5 phút, không tính thời gian ở pause/loading. Ban ngày dọn zombie thuộc chế độ này. Tiến trình riêng `Documents/MuZom-survival.json`, autosave mỗi 15 giây và sau giao dịch/tương tác. Trang bị mua được và đạn được phục hồi; vị trí nhân vật vẫn do engine Sandbox xử lý.

Người sống sót/cảnh sát dùng súng, không được chủ động nhắm người chơi. Khi người chơi gây sát thương trực tiếp cho một NPC, NPC đó phản công. Giới hạn 2/3 người theo quota app, cùng vùng dọn entity; không thêm cảnh sát truy nã.

## Tài nguyên

Hai quartet Human Zombie/DocZ đi qua SkinInstaller và Resource normalizer thật. Gói skidrow chỉ gồm PNG chưa tích hợp. 24 AWC sound-only, không đưa collision/explosion bank lớn hay .NET zombie DLL vào app. 8 WAV mono ngắn từ gói được cung cấp; giữ nguyên thông báo tác giả trong ZIP và credits. Quyền phân phối âm thanh vẫn theo thông báo gói gốc.

## Giới hạn kiểm chứng

Test native chạy trên runner macOS với mock thế giới; importer dùng file thật; HUD/Objective-C kiểm tra bằng iOS SDK. Kiểm tra hình ảnh/âm thanh và FPS cần tester chạy IPA trên iPhone, không thể suy ra từ unit test. Các lều/đạo cụ dùng model gốc, thiếu model sẽ bỏ qua an toàn. Không sửa renderer/Metal hoặc shader cache nền.

## Rollback

Nhánh vẫn `muzom-v001`. Tag `muzom-v001-tested-rollback` trỏ V001 (90151b9), IPA V001 còn ở ổ E. Không dùng `reset --hard` để rollback khi còn thay đổi chưa lưu; tạo bản checkout từ tag hoặc cài lại IPA V001. Save sinh tồn V002 tách khỏi dữ liệu game ngoài `E:/game`.
