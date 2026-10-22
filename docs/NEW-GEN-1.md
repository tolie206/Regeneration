# GTA NEW GEN — bản thử đầu trên nền 1.4.4

## Nền tảng
Giữ wasm2c → ARM64 và Metal, toàn bộ shader translator, pipeline cache, texture BC/ASTC, streaming, memory guard và luồng engine của source 1.4.4. Không chuyển renderer, prewarm, giới hạn heap, skin hoặc multiplayer của Mugoat sang. Cả hai dự án đều có đường render Metal; chưa có phép đo đối chứng để quy toàn bộ chênh lệch FPS cho một thành phần.

Changelog 1.4.4 ghi tối ưu biên dịch lớp engine thấp nhất (~17% CPU trong simulator), nén BC3 cho thiết bị trước 15 Pro, budget texture theo số đo thực tế và sửa stale jobs/render phases. Các mặc định hiệu năng được giữ nguyên. Không cam kết 60 FPS/1080p trên mọi thiết bị hoặc mod.

## Thay đổi
- Tên launcher GTA NEW GEN, bundle ID vn.hutaolee264.gtanewgen, version 1.4.4 build 1001. Mặc định giao diện vi và vuốt camera swipeMouse. Người chơi có thể đổi lại analog; không ghi đè lựa chọn đã lưu.
- Bổ sung bản dịch Việt cho 235 key giao diện (màn hình chính và thao tác chính). Một số mô tả dài/lỗi chuyên sâu vẫn fallback tiếng Anh; không gọi đây là bản dịch đầy đủ mọi thông báo.
- Không gửi telemetry, log/save đến backend tác giả cũ. Link dự án/hỗ trợ/cập nhật trỏ về repo mới. Giữ MIT LICENSE, third-party notices và upstream changelog/provenance theo giấy phép.
- Việt hoá được đóng sẵn: 602 GXT2, 213.683 label, 41.106 label khớp được cập nhật từ phần update2. Có dấu kèm đúng 5 file font/fontmap; không thay script, menu GFX hay toàn bộ archive PC. Không dấu giữ font gốc. Giữ ID và token điều khiển giữa hai bản. Overlay trong Mods, không sửa game gốc/save; đổi chế độ áp dụng sau khi mở lại app.
- Menu Mods: Nhập âm thanh xe (ZIP/RAR/OIV/RPF/thư mục FiveM) và Chọn tiếng cho xe (xe đang ngồi hoặc spawn name). REL151/54 và AWC phải đầy đủ. Giữ tên wavepack dlc_*; chọn từng AWC làm mất tên thư mục cần dùng ZIP/folder thay thế. Không chạy fxmanifest.lua/OIV installer scripts.
- Audio importer chỉ mang bộ chuyển REL54 và RPF utility đã kiểm chứng từ Mugoat. Sinh DLC native có alias .dat; rebase index/relocation khi mở rộng header. AWC nguyên byte. Kiểm tra profile động cơ trước khi bind, không thay mixer hoặc tăng gain. Gán trên script thread, tối đa kiểm tra 2 lần/giây khi có audio mod; bind một lần khi đổi xe/selection, không reset âm thanh mỗi frame. Import cần thực hiện trước khi chơi và khởi động lại app để mount bank.

## Kiểm chứng
Local: kiểm tra checksum dữ liệu build riêng; toàn bộ nhãn/tokens và placeholder Việt hoá. CI: compile/test importer Swift với bộ H2R FiveM thật, AWC so sánh từng byte, XML parse, REL54 alias và từ chối dữ liệu hỏng; Release iOS; kiểm tra identity, một IPA, không JIT, hai entitlement RAM.

Chưa kiểm thử trực tiếp trên iPhone: font có dấu, nghe sound mod, nhiệt độ, frame time/FPS và nhiệm vụ. Có lựa chọn không dấu/tắt Việt hoá; mod âm thanh có thể tắt/gỡ bằng Mod Manager rồi khởi động lại app. Không khẳng định mọi sound pack GTA V/Enhanced sẽ tương thích.

## Tester
1. Cài một IPA Paid Cert bằng ESign, giữ entitlement RAM; app mới có container riêng. Chọn lại dữ liệu game hoặc chuyển dữ liệu vào thư mục GTA NEW GEN.
2. Camera mặc định Vuốt. Thử Story/cutscene, chữ có dấu; nếu font lỗi chọn Mods → Việt hoá cốt truyện → Không dấu và mở lại app.
3. Trước khi chơi: Mods → Nhập âm thanh xe → chọn ZIP/FiveM folder hoặc OIV/RPF. Mở lại app, Mods → Chọn tiếng cho xe → nhập spawn name hoặc đang ngồi trên xe → chọn profile.
4. Báo model iPhone, preset, độ phân giải, chế độ Việt hoá, tên gói audio và gửi native-port.log cùng native-port-previous.log bằng Chia sẻ nhật ký.
