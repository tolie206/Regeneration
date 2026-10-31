# Mugoat PortData V1 — thử nghiệm độc lập

Base 099b0da / engine 0383f09. Renderer, WASM, shader inputs và các chính sách streaming giữ nguyên. Bundle ID vn.gta.newgen.portdata để cài song song, không thay Mugoat cũ. Không có lựa chọn GTA VI.

Data chuyển đổi offline từ bộ port của người dùng: EDX1/EDX3/EDX5/EAT1/EAT2 -> BC1/BC3/BC4/BC5, nén resource Deflate và dựng lại RPF lồng. Đây là transcode có mất mát; giữ kích thước và số mip, không hứa pixel giống hệt hoặc FPS giống runtime port. Mugoat vẫn có thể transcode BC sang ASTC trên iPhone.

Đây là bộ data lai tương thích engine: common/control/script và file không chuyển được giữ từ data Mugoat. Báo cáo nguồn/fallback từng file và SHA256 đi kèm dữ liệu trên PC. Không upload data game lên GitHub.

Manifest local chỉ được dùng khi có marker đúng profile, checksum manifest, checksum base và danh sách/THỨ TỰ đường dẫn khớp bản engine (bỏ phần env_test). Folder data cũ không có marker vẫn dùng manifest cũ. Kiểm tra file dùng kích thước mới, cùng manifest đó được truyền cho mod support và engine trước startup.

Kiểm thử: converter 5 định dạng, mọi mip của fixture, RPF lồng, đọc lại resource/RPF, payload binary giữ nguyên, đầu vào lỗi bị từ chối. Manifest Swift kiểm checksum, paths, size nguyên không âm, trùng tên, engine khác và thứ tự file.

Chỉ build sau khi các kiểm tra offline và Swift qua. Chưa có kiểm thử hiển thị trên iPhone: cần kiểm map, nhiệm vụ, cutscene, xe/audio và chạy lâu. Không gọi bản này là release đã ổn định.

Chạy công cụ bằng Python 3.14 (hoặc cài zstandard trên Python cũ):

    pip install -r tools/port_data/requirements.txt
    python tools/port_data/convert_data.py --source E:/GTAV_IOS --fallback E:/game/data --output E:/thu-muc-moi/data

Không chọn E:/GTAV_IOS nguyên bản trong app; chỉ dùng bộ đã chuyển và có marker sau kiểm tra đầy đủ.

Bản riêng chỉ dùng local data. Preloader không khởi tạo cache bằng manifest gốc trước engine (NativeAssets chỉ configure một lần). Không dùng tải cache nền/server data trong bản này.

Sau chuyển đổi chạy:

    python tools/port_data/finalize_data.py --data E:/thu-muc-moi/data --base-manifest E:/game/data/manifest.json
    python tools/port_data/verify_data.py E:/thu-muc-moi/data

Finalizer giữ archive gốc nếu số entry/kích thước bảng tên khác. Không tuyên bố so được tên trong bảng NG-encrypted của data cũ. Chỉ tạo marker sau checksum toàn bộ. Kiểm định độc lập đọc lại mọi resource đã chuyển; bộ data chỉ được coi là ứng viên offline, chưa xác nhận gameplay trên iPhone.

## FIX1 — lỗi startup NONE archives
Log thiết bị dừng rõ tại platform:/dlcPacks/mpBeach/dlc.rpf: Unencrypted archives no longer supported. Converter V1 giữ header key 0 của port; engine chỉ có nhánh OpenIV OPEN được vá sẵn trong prepare_mod_archives.py. Các test offline V1 đã cho phép cả NONE lẫn OPEN nên không bắt được lỗi này.

FIX1 ghi OPEN cho mọi RPF dựng lại và validator từ chối NONE. App chuẩn hóa key 0 -> OPEN cho bộ PortData có marker hợp lệ ngay trước startup, trên background queue. Quét cả RPF lồng, không động archive mã hoá hoặc payload, không bỏ DLC/điều kiện nhiệm vụ. Có journal các edit 4 byte để đối chiếu/rollback. Data V1 đang có trên điện thoại dùng lại được nếu thư mục cho phép ghi; không phải chép lại toàn bộ.

Bài test mới tái hiện NONE root/nested, OPEN parent chứa NONE child, giữ NG/byte payload, lặp an toàn và không ghi nếu phát hiện bảng lỗi khi lập kế hoạch. Chưa xác nhận gameplay sau FIX1 trên iPhone.
