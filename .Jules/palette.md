## 2025-01-06 - Reducing Friction in TUI Flow
**Learning:** In text-based interfaces, "Press Enter to continue" often creates unnecessary friction. Users intuitively expect "Press any key" behavior when pausing for readability.
**Action:** When implementing pause/continue flows in TUIs, favor single-character raw input reading (any key) over line-buffered input (Enter only) to create a more fluid interaction model.
