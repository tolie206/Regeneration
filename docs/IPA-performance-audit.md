# Đối chiếu IPA gốc và MuLone — 22/10/2026

## Kết luận có bằng chứng
- IPA gốc: Xcode 26.2 (17C52), iPhoneOS SDK 26.2 (23C53). MuLone V001: Xcode 16.4 (16F6), SDK 18.5 (22F76). Workflow trước đây không chọn Xcode, nên dùng bản mặc định của runner. Đây là thiếu sót trong việc tái tạo môi trường build của bản gốc.
- Shader compiler gốc metalfe-32023.864, MuLone metalfe-32023.620. Metallib khác byte; reflection giống hoàn toàn. Cùng source renderer không có nghĩa cùng GPU executable.
- Cả hai IPA có increased-memory-limit và extended-virtual-addressing; deployment target iOS 16.0, PGLiteMode=false, cho phép frame rate ProMotion. Chưa thấy bằng chứng quyền RAM thiếu ở MuLone.
- So sánh 100.927 hàm wasm2c chung: 99.478 hàm (98,56%) có cùng kích thước. Tổng mã nhóm này gốc 85.793.640 byte, MuLone 85.768.152 byte. Không có dấu hiệu toàn bộ engine bị build O0 so với bản gốc. Đây không phải benchmark; call/address relocation làm hash mã khác và kích thước không đo tốc độ.
- Một số hàm host render có mã khác sau compile: drawInner 13.132/13.768 byte, execute 22.940/23.948 byte. Có thể do compiler/libc++/inlining; không thể suy ra chậm bao nhiêu từ số byte hoặc số lệnh tĩnh.
- Cùng 5.814 tên file manifest. 22 hàng khác metadata; chỉ 2 file HTML chẩn đoán parser khác kích thước 2 byte. Các file timecycle khác timestamp, không khác kích thước. Manifest không chứa hash nội dung nên không thể kết luận toàn bộ data giống byte chỉ dựa manifest.
- Phần lớn tài nguyên đóng gói giống hoàn toàn: shader-reflection, intro, asi table, bootset. MuLone thêm 2 gói Việt hoá và sound hook; chưa có đo runtime chứng minh chúng vô hại hay gây regression. ZIP Việt hoá không tự giải nén mỗi frame; overlay/font đã nạp vẫn có thể thay workload.

## Đối chiếu log
Bản gốc 1950x900/60 FPS ghi các mẫu 63,55,54 FPS, thermal serious. MuLone 1560x720/60 ghi 34 FPS, thermal serious. Máy nóng không giải thích đầy đủ chênh lệch. Những lần 540p uncapped không thay thế so sánh 900p/60. Số GPU ms không đại diện tổng frame time; có CPU scheduling và chờ main/render/visibility.

## Kiểm chứng tiếp theo
V003 chỉ đổi toolchain so với code V002, khóa Xcode 26.2 build 17C52 và xác minh SDK trong IPA, không thay thuật toán render, heap hoặc prewarm. Mục đích tái tạo môi trường compiler của bản gốc. Chưa được phép tuyên bố đây là nguyên nhân đã chứng minh hoặc bảo đảm phục hồi 60 FPS trước khi test trên điện thoại.
Nếu V003 vẫn chậm, bước tiếp theo là tách Việt hoá/font, sound hook và dữ liệu cấu hình theo từng biến trong cùng toolchain. Không thêm nhiều tối ưu không liên quan trước khi xác định tác nhân.

## Tệp bằng chứng
comparison.json: hash IPA/shader, Info.plist, entitlements, section và kích thước hàm.
disassembly-summary.json và *.asm: ARM64 của các hàm đã chọn. Phân tích tĩnh, không phải sampling khi chơi.

## Rollback
Giữ nguyên IPA gốc, V001 và V002; thay đổi source lưu theo commit. Không sửa data gốc hoặc save trong phân tích này.
