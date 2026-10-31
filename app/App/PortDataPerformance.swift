import Foundation

enum PortDataPerformance {
    enum Mode: Int, CaseIterable {
        case original = 0, balanced = 1, maximum = 2
        var title: String { ["Tắt — giữ cấu hình tự chọn", "Ổn định FPS (khuyên dùng)", "Ưu tiên FPS tối đa"][rawValue] }
        var heightCap: Int { self == .original ? 0 : self == .balanced ? 720 : 540 }
    }
    static var mode: Mode {
        get { Mode(rawValue: UserDefaults.standard.object(forKey: "PortDataPerformanceMode") as? Int ?? 1) ?? .balanced }
        set { UserDefaults.standard.set(newValue.rawValue, forKey: "PortDataPerformanceMode") }
    }
    static func height(_ requested: Int, mode: Mode) -> Int {
        mode.heightCap == 0 ? requested : min(requested, mode.heightCap)
    }
    static func options(_ source: [String], mode: Mode) -> [String] {
        guard mode != .original else { return source }
        let caps: [String: Double] = ["textureQuality": 0, "shadowQuality": -1, "reflectionQuality": 0, "grassQuality": 0, "particleQuality": 0,
            "lodScale": mode == .balanced ? 0.15 : 0, "cityDensity": mode == .balanced ? 0.2 : 0,
            "pedLodBias": 0, "vehicleLodBias": 0, "pedVariety": 0.2, "vehicleVariety": 0.2]
        return source.map { option in
            let parts = option.dropFirst().split(separator: "=", maxSplits: 1).map(String.init)
            guard parts.count == 2, let cap = caps[parts[0]], let value = Double(parts[1]) else { return option }
            let result = min(value, cap)
            return "-\(parts[0])=\(result.rounded() == result ? String(Int(result)) : String(result))"
        }
    }
}
