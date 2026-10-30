#!/bin/bash
set -euo pipefail
repo="$PWD"
probe="$RUNNER_TEMP/engine-cache-probe"
mkdir -p "$probe/Generated"
export PG_REAL_CLANG="$(xcrun --sdk iphoneos --find clang)"
export CCACHE_DIR="$probe/cache"
export CCACHE_LOGFILE="$probe/cache.log"
chmod +x "$repo/tools/ccache_engine.sh"
printf 'int engine_probe(int x){return x*3+1;}\n' > "$probe/Generated/game_probe.c"
cat > "$probe/project.yml" <<'YAML'
name: EngineCacheProbe
options:
  deploymentTarget:
    iOS: '16.0'
targets:
  EngineCacheProbe:
    type: library.static
    platform: iOS
    sources:
      - path: Generated
        compilerFlags: -w -fno-modules
YAML
(cd "$probe" && xcodegen generate)
for pass in 1 2; do
 # Touch changes Xcode's input date, not the content used by ccache.
 touch "$probe/Generated/game_probe.c"
 xcodebuild -project "$probe/EngineCacheProbe.xcodeproj" -scheme EngineCacheProbe -sdk iphoneos -configuration Release -derivedDataPath "$probe/Derived" "CC=$repo/tools/ccache_engine.sh" COMPILER_INDEX_STORE_ENABLE=NO CODE_SIGNING_ALLOWED=NO GCC_OPTIMIZATION_LEVEL=2 build > "$probe/xcode-$pass.log" 2>&1 || { tail -30 "$probe/xcode-$pass.log";exit 1; }
done
ccache --show-stats --verbose
if ! grep -Eq 'Result: (direct_cache_hit|preprocessed_cache_hit)' "$CCACHE_LOGFILE"; then
 echo 'ERROR: cache did not reuse the identical engine probe; stopping before expensive build.'
 cat "$CCACHE_LOGFILE";tail -20 "$probe/xcode-2.log";exit 1
fi
echo 'PASS: actual repeated Xcode generated-C compile cached with unchanged iPhone compiler'

