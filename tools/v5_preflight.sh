#!/bin/bash
# Run independent checks together, report every failure before an expensive IPA build.
set -uo pipefail
scratch="${1:?temporary output folder required}"
failed=0
check() {
  if "$@"; then return 0; fi
  failed=$((failed+1))
  return 0
}
sdk="$(xcrun --sdk iphonesimulator --show-sdk-path)"
check xcrun swiftc -typecheck -target arm64-apple-ios16.0-simulator -sdk "$sdk" app/App/Theme.swift app/App/HomeView.swift app/Tests/V5HomeTypecheckStubs.swift
if clang -fobjc-arc -framework Foundation app/Source/VisualEffects.m app/Tests/visual_effects.m -o "$scratch/v5-visual"; then
  (cd app && "$scratch/v5-visual") || failed=$((failed+1))
else
  failed=$((failed+1))
fi
check python3 tools/test_v5_stock_audio.py
check python3 tools/test_v5_presets.py
check python3 tools/test_v5_msr.py
if clang++ -std=c++17 -Wall -Wextra -I app/Source app/Tests/v5_frame_metrics.cpp -o "$scratch/v5-metrics"; then
  check "$scratch/v5-metrics"
else
  failed=$((failed+1))
fi
if clang -std=c11 -pthread app/Tests/sound_runtime.c -o "$scratch/v5-sound"; then
  check "$scratch/v5-sound"
else
  failed=$((failed+1))
fi
check xcrun swiftc -frontend -parse -target arm64-apple-ios16.0-simulator -sdk "$sdk" app/App/HomeView.swift app/App/Theme.swift app/App/SettingsViewController.swift app/App/MSRSettings.swift app/App/GraphicsOptions.swift
printf 'V5 independent preflight failures: %s\n' "$failed"
test "$failed" = 0
