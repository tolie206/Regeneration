# Optional lightweight color filter — research prototype

The supplied E:/43a79a-Filter/scripts/addins/Filter.lua calls GRAPHICS.DRAW_RECT(0.5,1,1,2,red,green,blue,alpha) every active tick. It is a transparent screen tint, not foliage grading; its Lua/menu dependency is not bundled.

New implementation is selective vibrance in the existing final Metal presentation pass, after existing scaling/FXAA. Three optional shader variants retain exactly the same texture sample counts, draw count, command encoder count, and existing targets. Only a16-byte uniform and color ALU are added when enabled. No LUT, extra full-screen surface, bloom, sharpening, weather/light/texture replacement or Lua runtime. Off selects the untouched original shader/pipeline and does not bind the filter uniform. Capture uses the original pipeline as before. Optional PSOs are compiled once at startup; unavailable variant falls back to original.

Settings category: Filter màu cảnh quan. Off (default), Tự nhiên, Cây cối tươi hơn, Rực rỡ nhẹ; live and persistent. Green-only preset preserves neutral, red-dominant skin and blue colors in the reference math; color selection also changes other green objects, not just trees. Final composition includes HUD, so colored HUD elements can shift. Camera/cutscene colors are also graded; native UIKit launcher/settings are not.

No promise of zero FPS impact: enabled filter executes additional ALU at output resolution. Device A/B comparison required with same location, weather, resolution, thermal state and camera. Measure frame time, low FPS and sustained heat with Off versus Natural/Green. UI should never label it free/no cost. No actual iPhone/GPU pixel test performed here.

New tests: unchanged-original shader SHA checks, no extra present pass/draw/texture lookups, numeric reference color bounds/skin/neutral/luma oracle, real MSL compile plus iPhone SDK renderer syntax, Swift typecheck. Numeric oracle does not replace rendering acceptance on iPhone.

FIX3 build already running is kept intact. Filter is isolated on a feature branch for targeted validation before a later IPA.
