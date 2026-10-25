# R005 — drive-by input and texture recovery

Base: R004 3c912e7; rollback R004 and main remain unchanged.

Confirmed code defects:
- Native swipe rejected L1 bit 2 as a weapon wheel, although L1 also means vehicle aim. Wheel suppression now stays with actual UIKit gesture roles.
- Vehicle aim-only button was absent from the aiming predicate and lacked a fireLook drag role. Both corrected. Assisted targeting modes use controller swipe; explicit free aim remains free aim.

Texture investigation:
- A16 log: no Metal texture create/decode failures, thousands of streaming clamps, rapidly rising resource unload counts. This supports streaming starvation/churn, not proof that geometry is missing.
- Existing code documents that address-space fast nudges misclassify near-equal process/engine limits and evict textures much faster. Require 512 MiB spare before using that fast branch; ordinary reclamation, 384 MiB reserve, 256/64 MiB bands, heap ceiling, renderer, shaders and texture quality stay unchanged.
- This addresses a concrete classification weakness. It does NOT prove all grey materials are cured; base data/mod dependencies and actual iPhone recovery must be checked. Do not claim measured FPS improvements without device results.

Validation: production C swipe exercised across all 65536 button combinations, production Swift aiming/mode selection, production guard boundary tests, full previous importer/skin/audio/resource regression suite. Native iOS Release build follows only after validation passes. Host tests cannot establish rendered appearance, target acquisition or phone frame times.
