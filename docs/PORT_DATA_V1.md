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

## FIX2 — tải cảnh và data
Log A16: mẫu Health lượt dài xuống 6 FPS, đạt 3.904/4.095 MB, 1.391 lần chặn tăng streaming, 23 yêu cầu thu hồi; tất cả mẫu ghi thermal serious. Lượt ngắn vẫn 23–38 FPS khi còn hơn 1 GB headroom, nên RAM không giải thích toàn bộ. Mesh GPU cuối lượt dài ~747 MB, các cửa sổ lên ~4.155 draw/frame ở lượt trước. Không có lỗi đọc/slow-read >250 ms trong các mẫu. Pipeline có tác động từng cửa sổ, nhưng FPS thấp cả cửa sổ không chờ pipeline. Menyoo có overhead đo được; không tự tắt mod của người chơi.

Thêm profile Tối ưu PortData (mặc định Ổn định FPS): đầu ra tối đa720p, texture0, bóng tắt, cỏ/reflection/particle thấp, LOD tối đa0.15, cityDensity tối đa0.2. Chế độ tối đa540p/LOD0; Tắt trả lại thiết lập cũ. Chi tiết thấp hơn vẫn giữ nguyên, shader≥1, script/mission/collision/thu hồi và query/readback không sửa. Đây là giảm chất lượng có chủ đích, không phải tăng FPS miễn phí. Log ghi đầy đủ giá trị effective.

Data V2 là tuỳ chọn riêng: dictionary YTD legacy phù hợp giới hạn mip có sẵn256 và gói lại physical thành một page hợp lệ, đổi GraphicsFlags trong cả resource header và RPF entry, cập nhật GraphicsPagesCount. Giữ tên/hash, loại texture, các byte mip còn lại; không giảm số mesh/hình học/collision/script. File/layout lạ hoặc HUD/phông/chức năng UI nhận diện được giữ nguyên. Tắt profile app không thể phục hồi mip đã bỏ: chọn lại data V1 để rollback đồ hoạ data.

Không nói phần dữ liệu mượt tương đương engine port: chuyển ETC2/EAC về BC làm Mugoat tiếp tục transcode sang ASTC. Chưa có A/B iPhone đo FPS/frame pacing sau FIX2.

Ngân sách boot: log dùng129% để tính1779MiB video trong khi BC cuối lượt có368/185~199%. Profile hiệu năng dùng cache riêng và floor200% (1148MiB ở limit4096), giữ số đo cao hơn nếu có. Tắt profile dùng lại cache/cách tính cũ; GPU đọc BC native giữ100%. Không thêm memory cap hay thay ngưỡng thu hồi. Renderer/draw/visibility/query và game.wasm không đổi.
