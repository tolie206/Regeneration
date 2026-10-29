# V5R1 build host recovery
GitHub run40912867216 failed before checkout: no hosted macOS ARM64 runner acquired, with explicit capacity annotations. Switching macOS15 to26 did not resolve the ARM pool shortage.

Use standard macos-26-intel, still Xcode26.2 build17C52 and iOSSDK26.2. iOS target remains ARM64, Release/O2, native Metal; IPA verification checks Mach-O CPU explicitly. No gameplay/streaming/memory-policy changes in this repair.

Only host tools change: WABT1.0.42 is built from checksum-pinned source for x86_64, then its unchanged patched writer generates the iOS engine C. libarchive3.8.9 is built for host importer tests (ZIP/deflate, RAR/RAR5, BZip2; optional codecs disabled in this test-only build). The committed iPhone archive library and native Opus/Blink ARM64 cross-build flags stay unchanged.

The original shader translator is ARM-only. Intel reuses exact device metallib/reflection bytes from locally retained R007 build1016, built with the same Xcode17C52, shader index and unchanged translator/reflection ABI. Archive/file/source SHA256 checks and all4808 shader IDs are required; mismatch fails closed. V5 MSR helper shaders still compile from current source. Simulator is rejected for this pinned device-only route. This adds a compressed38MB build input, not an extra IPA resource copy.

Host tests do not prove iPhone gameplay, sound audibility, image quality or FPS. Real device checks remain necessary.

On macos-26-intel, LLDB in job123618347858 stopped in libsystem_pthread __pthread_init.cold.2 before test code. An isolated sanitized setjmp/longjmp executable also exited132; the unsanitized full lazy test passed. Move host to macos-15-intel with the same Xcode26.2 rather than disable sanitizers or change game code.

macos-15-intel was also unavailable in the subsequent queue. Final route keeps the iPhone compiler/SDK at26.2, and uses Xcode26.6 only for isolated host sanitizer executables. Before regression tests, a minimal pthread/setjmp program must succeed and deliberate heap/signed-overflow controls must produce ASan/UBSan reports. Failed startup or missing detection fails CI; sanitizer checks are not skipped.
