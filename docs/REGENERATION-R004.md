# Regeneration R004 — bản kiểm thử

Nhánh: regeneration-r004-scene-skins; dựa trên R003 71711c0. Main và regeneration-turbo-native vẫn nguyên baseline d32687d5. Build 1013, bundle vn.gta.newgen. Không merge vào main.

## Skin và resource
Stack native được đối chiếu với executable R003, không chỉ tên R002 còn sót trong log: wasm_rt_trap -> pgBase::pgBase -> texture dictionary PlaceResource -> ResourcePlacementThread. Ryoubi.ytd có virtual 10,240 byte, gồm trang 8,192 và 2,048 byte. Bộ mã hóa page map pinned engine dùng size>>13 và chỉ mã hóa được trang từ8KiB; trang nhỏ dẫn tới unreachable. Resource importer mới ghép/đệm virtual thành16,384byte, thêm đúng6,144byte padding; physical texture giữ nguyên. Không đổi pixel, geometry, mip hay shader. Kiểm tra raw DEFLATE đầy đủ; chấp nhận trailer Adler-32 khi checksum đúng (Bati2 hợp lệ cần điều này); từ chối dữ liệu hỏng.

Áp dụng lúc nhập skin/quartet và resource rời; không hứa sửa mọi mod PC/Enhanced, archive mã hóa hay DLL. Với skin đã cài: trước khi chơi, Mods -> Kiểm tra và sửa skin đã cài. Chỉ sửa các gói có skin-models.json; backup gốc ẩn .dlc.rpf.before-r004 cạnh DLC. Không quét lại trong gameplay. Gói Makima được gửi thiếu cuối archive (~15KB), phải tải lại bản đầy đủ; không thể dựng lại texture bị mất.

Tên model tùy chọn khi nhập một skin: chữ thường, bỏ dấu/whitespace, đ->d. Ví dụ Mỹ Nhân Đẹp01 -> mynhandep01. Đồng bộ bốn tên resource, peds.meta và danh sách Menyoo; chặn tên trùng giữa các gói. Nhập nhiều skin giữ tên gốc hoặc nhập riêng để đặt tên từng skin. Không chỉnh game data gốc. Hình render thực tế vẫn cần xác nhận iPhone.

## Tải chuyển cảnh
Log được cung cấp ghi hai load scene10.3s và4.9s, không ghi clamp/evict hay lỗi đọc file tại đó; chưa đo được đầy đủ khoảng vài phút tester mô tả. Không ép IsLoaded=true, rút bán kính mission, teleport lại, xóa map, bỏ điều kiện collision hay tăng heap.
Sửa lỗi lifecycle có thể chứng minh trong source: code cũ kiểm tra PGLoadSceneSeconds()!=0 nên giây đầu bị coi là không tải; timer còn hết hạn180s. Guard mới dùng cờ CLoadScene active thực tế và dấu bắt đầu, chặn spawn/cheat/audio override/turbo trong toàn pha tải. Điều này sửa khoảng hở can thiệp; CHƯA chứng minh là nguyên nhân chính hay đã rút tải từ phút xuống giây. Thêm trace phase/volume/entity/bounds/collision mỗi5giây sau3giây chờ, không scan asset mỗi frame. Tester cần gửi log đúng lần chết/qua mission còn chậm để phân biệt streaming đang chờ với script giữ điều khiển sau khi streaming kết thúc.

## Camera
Đọc Note.txt và README cả hai mod. Enhanced Camera yêu cầu ScriptHookVDotNet (Windows .NET), không dùng trực tiếp. Port có interpreter ASI giới hạn nên cũng không thể mặc định DynamicVehicleFirstPerson tương thích đầy đủ; không nhúng hai binary PC này.
Thêm Công cụ hỗ trợ -> Góc nhìn thứ nhất: camera native engine cho đi bộ và trong xe; có nút về góc nhìn thứ ba. Chạy một lần trên script thread khi game sẵn sàng, không ép camera mỗi frame và không ghi đè cutscene. Không mô phỏng đầy đủ inertia/horizon-lock/FOV-offset của mod PC, chưa được test cảm giác trên iPhone.

## Xác minh và rollback
Kiểm thử Swift thật với Ryoubi và Makima; xác minh byte từng segment, padding, idempotence, đổi tên, RPF lồng, reject corrupt. Test C lấy chính predicate lifecycle production, kiểm tra giây đầu/cờ còn active sau timeout/UI timer/release. Các kiểm thử đó không phải gameplay hay pixel rendering.
Shader source, Metal renderer, memory budget và streaming preset giữ baseline. EngineHost.c chỉ thêm đăng ký resource lớn khi mount archive; phần còn lại được khóa bằng hash baseline. Turbo chỉ thay guard active, không đổi thuật toán/audio. Không cam kết zero FPS regression nếu chưa benchmark trên máy.
Quay lại source R003: nhánh regeneration-mod-repair, commit71711c0; IPA gốc trên E:/New Project/Builds/Mugoat-NewGen-Regeneration-R003.ipa. Quay lại owner baseline: tag regeneration-baseline-20261024-d32687d5, IPA R002 được giữ riêng. Sao lưu Mods/save trước đổi app; rollback source không tự rollback dữ liệu. File backup resource có thể được chép lại thành dlc.rpf khi game đã tắt hoặc gỡ gói rồi nhập lại archive gốc.


## Bổ sung VF8 — sửa hệ thống resource lớn
Gói VF8 có vf8.yft17,512,137byte và vf8_hi.yft17,502,433byte. Cả hai dùng sentinel0xFFFFFF và kích thước32bit ở header mở rộng của RPF. Audit pinned engine và bài C thực thi cho thấy Size/Size64 cũ trả16,777,215byte. Recompress zlib level9 vẫn trên16MiB, nên không giả vờ nén lại là sửa được.

Bản sửa bổ sung index resource đã kiểm tra trước boot từ các gói mod đang bật, đối chiếu archive/device/path +system/graphics flags. Khi mount, cache kích thước thật theo địa chỉ entry và fingerprint16byte. Mọi resource thông thường giữ đường cũ; chỉ sentinel0xFFFFFF dùng lookup. Sửa14 điểm ở11hàm: liệt kê, Size/Size64/GetFileSize, ReadInternal, Seek64, pgStreamer::Read, RegisterObject, GetNextFilesOnCdNew, LoadRequestedObjects. Không giảm polygon/texture, không sửa tên riêng VF8 trong code production. Gói đã cài cũng được index; không bắt buộc nhập lại VF8 để hưởng sửa kích thước.

Kiểm thử trước IPA: Swift importer dùng ZIP VF8 thật -> index đúng cả2YFT với đường device thật dlc_vf8:/x64/levels/gta5/vehicles/vehicles.rpf. Test native Objective-C đọc chính index đó, kiểm tra case/slash/flags và từ chối archive khác. Test C dùng registry/walker production +body Size/Size64 từ pinned wasm2c: bản cũ tái hiện truncation, bản sửa trả đầy đủ17,512,137byte; fingerprint sai không lấy nhầm entry. Python kiểm tra cả14mask, idempotence và từ chối source engine không khớp. Validation40166605503 đã qua. Những bài này chưa chứng minh VF8 hiển thị trên iPhone hoặc mọi dependency của mod đều có.

Thông báo gọi xe giờ phân biệt chờ đóng pause/chuyển cảnh/gameplay với đang tải model; log trạng thái chờ mỗi2giây và tải model mỗi5giây, chỉ trong lúc có yêu cầu. Không dùng thông báo chung “đang chờ game” cho cả hai nữa. Vẫn cần log đúng lần gọi xe để biết xe khác hỏng vì size, dependency, RAM hay trạng thái gameplay; không cam kết tự sửa mọi file tùy ý.
