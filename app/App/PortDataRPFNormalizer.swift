import Foundation

/// Key 0 is rejected by this engine. OPEN takes its existing OpenIV path.
/// Only normalizes verified local PortData datasets, before any engine thread starts.
enum PortDataRPFNormalizer {
    static let open: UInt32 = 0x4e45504f
    struct Plan { let name: String; let offsets: [UInt64] }
    private static func bad(_ text: String) -> NSError {
        NSError(domain: "PortDataRPF", code: 1, userInfo: [NSLocalizedDescriptionKey: text])
    }
    static func word(_ data: Data, _ at: Int) -> UInt32 {
        (0..<4).reduce(UInt32(0)) { $0 | UInt32(data[at + $1]) << ($1 * 8) }
    }
    static func plan(file: URL, size: UInt64) throws -> [UInt64] {
        let handle = try FileHandle(forReadingFrom: file)
        defer { try? handle.close() }
        func read(_ at: UInt64, _ count: Int) throws -> Data {
            guard at <= size, UInt64(count) <= size - at else { throw bad("RPF vượt giới hạn: " + file.lastPathComponent) }
            try handle.seek(toOffset: at)
            guard let bytes = try handle.read(upToCount: count), bytes.count == count else { throw bad("RPF bị cắt: " + file.lastPathComponent) }
            return bytes
        }
        var offsets: [UInt64] = [], visited = Set<UInt64>()
        func scan(_ base: UInt64, _ length: UInt64, _ depth: Int) throws {
            guard depth <= 16, length >= 16, base <= size, length <= size - base,
                  visited.insert(base).inserted else { throw bad("Cấu trúc RPF lồng không hợp lệ.") }
            let header = try read(base, 16)
            guard word(header, 0) == 0x52504637 else { throw bad("Không phải RPF7: " + file.lastPathComponent) }
            let key = word(header, 12)
            // Encrypted originals remain untouched, including their unreadable table.
            guard key == 0 || key == open else { return }
            let count = Int(word(header, 4)), names = Int(word(header, 8))
            guard count > 0, count <= 100_000, names > 0, names <= 8_388_608,
                  UInt64(16 + count * 16 + names) <= length else { throw bad("Bảng RPF không hợp lệ.") }
            let table = try read(base + 16, count * 16)
            let strings = try read(base + UInt64(16 + count * 16), names)
            if key == 0 { offsets.append(base + 12) }
            for i in 0..<count {
                let first = word(table, i * 16), second = word(table, i * 16 + 4)
                if second == 0x7fffff00 || second & 0x80000000 != 0 { continue }
                let nameOffset = Int(first & 0xffff)
                guard nameOffset < strings.count,
                      let end = strings[nameOffset...].firstIndex(of: 0) else { throw bad("Tên trong RPF không hợp lệ.") }
                let name = String(decoding: strings[nameOffset..<end], as: UTF8.self).lowercased()
                guard name.hasSuffix(".rpf") else { continue }
                let packed = UInt64(first) | UInt64(second) << 32
                let compressed = (packed >> 16) & 0xffffff
                guard compressed == 0, word(table, i * 16 + 12) == 0 else { throw bad("RPF lồng bị nén/mã hoá chưa được hỗ trợ.") }
                let offset = ((packed >> 40) & 0xffffff) * 512
                let bytes = UInt64(word(table, i * 16 + 8))
                guard offset >= UInt64(16 + count * 16 + names), offset <= length, bytes <= length - offset else { throw bad("RPF lồng vượt kích thước archive.") }
                try scan(base + offset, bytes, depth + 1)
            }
        }
        try scan(0, size, 0)
        return offsets
    }
    @discardableResult static func prepare(folder: URL, files: [(String, UInt64)]) throws -> Int {
        let root = folder.resolvingSymlinksInPath().path
        var plans: [Plan] = []
        // Plan the entire change first. A malformed archive never gets a partial header rewrite.
        for (name, expected) in files where name.lowercased().hasSuffix(".rpf") {
            let file = folder.appendingPathComponent(name).resolvingSymlinksInPath()
            guard file.path.hasPrefix(root + "/"),
                  let actual = try file.resourceValues(forKeys: [.fileSizeKey]).fileSize,
                  UInt64(actual) == expected else { throw bad("Kích thước/đường dẫn data đã thay đổi: " + name) }
            let offsets = try plan(file: file, size: expected)
            if !offsets.isEmpty { plans.append(Plan(name: name, offsets: offsets)) }
        }
        guard !plans.isEmpty else { return 0 }
        var journal = plans.map { ["path": $0.name, "offsets": $0.offsets, "original": 0, "replacement": open] as [String: Any] }
        let journalURL = folder.appendingPathComponent("mugoat-rpf-open-repair.json")
        if let previous = try? Data(contentsOf: journalURL), previous.count <= 2_000_000,
           let json = try? JSONSerialization.jsonObject(with: previous) as? [String: Any],
           json["profile"] as? String == "rpf-open-repair-v1",
           let changes = json["changes"] as? [[String: Any]] { journal.insert(contentsOf: changes, at: 0) }
        let record = try JSONSerialization.data(withJSONObject: ["profile": "rpf-open-repair-v1", "changes": journal], options: [.sortedKeys])
        // Saves the precise reversible 4-byte edits BEFORE modifying any archive.
        try record.write(to: folder.appendingPathComponent("mugoat-rpf-open-repair.json"), options: .atomic)
        var changed = 0
        for item in plans {
            let h = try FileHandle(forUpdating: folder.appendingPathComponent(item.name))
            do {
                for offset in item.offsets {
                    try h.seek(toOffset: offset)
                    guard let data = try h.read(upToCount: 4), data.count == 4 else { throw bad("Không đọc được header để sửa.") }
                    let value = word(data, 0)
                    guard value == 0 || value == open else { throw bad("Header đã thay đổi trong khi chuẩn hoá.") }
                    if value == 0 {
                        try h.seek(toOffset: offset)
                        try h.write(contentsOf: Data([0x4f, 0x50, 0x45, 0x4e]))
                        changed += 1
                    }
                }
                try h.synchronize(); try h.close()
            } catch { try? h.close(); throw error }
        }
        return changed
    }
}
