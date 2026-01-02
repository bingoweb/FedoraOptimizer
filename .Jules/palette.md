## 2025-05-23 - Improve "Continue" Prompt Interaction
**Learning:** In TUI applications, requiring specific keys (like 'Enter') for navigation flow breaks the fluid experience. Users expect "any key" to continue unless confirmation is explicitly needed.
**Action:** Replace `Prompt.ask("Press Enter...")` with a non-blocking `wait_for_key` mechanism that accepts any input, making the interaction feel snappier.
