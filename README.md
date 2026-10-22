# GTA NEW GEN

Bản iOS tiếng Việt dựa trên source 1.4.4. Duy trì renderer Metal, texture compression và streaming của source mới. Không ghép renderer/hệ thống skin Mugoat.

Build từ Actions → Build MuLone → Run workflow. Tên bản đầu: MuLone-V001.ipa; các bản tiếp theo tăng V002, V003… Chỉ build một IPA, giữ entitlement RAM để ký bằng ESign. Bundle ID riêng: `vn.hutaolee264.gtanewgen`. Dữ liệu game cần do người chơi cung cấp; không chứa bộ 20 GB hay save.

Giữ LICENSE và UPSTREAM-NOTICES.md theo giấy phép của source gốc. Các đường dẫn hỗ trợ, cập nhật và giao diện được đổi cho fork này. Không gửi telemetry/log/save đến dịch vụ tác giả cũ.

Hướng dẫn tester và giới hạn: [docs/NEW-GEN-1.md](docs/NEW-GEN-1.md). Renderer được đối chiếu nguyên byte với source 1.4.4 trong docs/RENDERER-BASELINE.json.
