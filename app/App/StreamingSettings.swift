import Foundation

/// Boot-only preferences. Automatic preserves the regeneration baseline.
enum StreamingSettings {
    static let distanceValues = ["0", "0.2", "0.4", "0.6", "0.8", "1"]
    static let textureValues = [384, 512, 640, 768, 1024, 1280]
    static var distanceScale: String? {
        get {
            guard let value = UserDefaults.standard.string(forKey: "RegenerationExtendedDistance"),
                  distanceValues.contains(value) else { return nil }
            return value
        }
        set {
            UserDefaults.standard.set(newValue.flatMap { distanceValues.contains($0) ? $0 : nil }, forKey: "RegenerationExtendedDistance")
        }
    }
    static var textureBudgetMB: Int {
        get {
            let value = UserDefaults.standard.integer(forKey: "RegenerationTextureBudget")
            return textureValues.contains(value) ? value : 0
        }
        set { UserDefaults.standard.set(textureValues.contains(newValue) ? newValue : 0, forKey: "RegenerationTextureBudget") }
    }
    static func applyTextureBudget() {
        setenv("PG_DISTANCE_STREAMING", GameSettings.shared.distanceStreaming ? "1" : "0", 1)
        if textureBudgetMB == 0 { unsetenv("PG_VIDEO_MEMORY_MB") }
        else { setenv("PG_VIDEO_MEMORY_MB", String(textureBudgetMB), 1) }
    }
}
