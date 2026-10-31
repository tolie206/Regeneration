import Foundation
import CryptoKit
import CoreFoundation

/// Opt-in offline converted data. Original data folders still use the bundled manifest.
/// Never accepts arbitrary paths or a different engine's file list.
enum PortDataManifest {
    static let localOnly = true
    static let markerName = "mugoat-port-data.json"
    struct Loaded { let url: URL; let files: [(String, UInt64)] }
    static func hasMarker(_ folder: URL) -> Bool {
        FileManager.default.fileExists(atPath: folder.appendingPathComponent(markerName).path)
    }
    private static func reject(_ text: String) -> NSError {
        NSError(domain: "MugoatPortData", code: 1, userInfo: [NSLocalizedDescriptionKey: text])
    }
    static func load(folder: URL, baseManifest: URL) throws -> Loaded {
        func bounded(_ url: URL, _ max: Int) throws -> Data {
            let n = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? -1
            guard n > 0 && n <= max else { throw reject("Manifest data chuyển đổi không hợp lệ hoặc quá lớn.") }
            return try Data(contentsOf: url)
        }
        func hash(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }
        let markerData = try bounded(folder.appendingPathComponent(markerName), 16_384)
        let baseData = try bounded(baseManifest, 2_000_000)
        let url = folder.appendingPathComponent("manifest.json")
        let data = try bounded(url, 2_000_000)
        guard let marker = try JSONSerialization.jsonObject(with: markerData) as? [String: Any],
              marker["profile"] as? String == "mugoat-port-converted-v1",
              marker["baseManifestSHA256"] as? String == hash(baseData),
              marker["manifestSHA256"] as? String == hash(data),
              let base = try JSONSerialization.jsonObject(with: baseData) as? [String: Any],
              let baseRows = base["files"] as? [[Any]],
              let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              json["mount"] as? String == "/game/",
              let rows = json["files"] as? [[Any]] else {
            throw reject("Data chuyển đổi không khớp phiên bản engine hoặc sai checksum manifest.")
        }
        let expected = baseRows.compactMap { $0.first as? String }.filter { !isTestMap($0) }
        var files: [(String, UInt64)] = []; var seen = Set<String>(); var total: UInt64 = 0
        for row in rows {
            guard row.count >= 2, let name = row[0] as? String,
                  let number = row[1] as? NSNumber, CFGetTypeID(number) != CFBooleanGetTypeID(),
                  number.doubleValue >= 0, number.doubleValue.rounded(.towardZero) == number.doubleValue,
                  number.doubleValue <= 2_147_483_647,
                  !name.contains("\\"), !name.contains("\0"), !name.hasPrefix("/"),
                  name.split(separator: "/", omittingEmptySubsequences: false).allSatisfy({ !$0.isEmpty && $0 != "." && $0 != ".." }),
                  seen.insert(name.lowercased()).inserted else { throw reject("Đường dẫn hoặc kích thước trong manifest không an toàn.") }
            let size = number.uint64Value; total += size
            guard total <= 64_000_000_000 else { throw reject("Bộ data vượt giới hạn kiểm tra.") }
            files.append((name, size))
        }
        guard files.map({ $0.0 }) == expected else { throw reject("Danh sách file không khớp engine Mugoat; không thể dùng data port nguyên bản.") }
        return Loaded(url: url, files: files)
    }
    static func isTestMap(_ name: String) -> Bool {
        name.contains("levels/env_test/") || name.hasPrefix("common/data/env_test_")
    }
}
