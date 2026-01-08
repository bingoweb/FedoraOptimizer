## 2025-05-18 - Press Any Key
**Learning:** In TUI apps, replacing "Press Enter to continue" with "Press any key" significantly reduces friction for repetitive tasks.
**Action:** Use `wait_for_key` with a polling loop and `KeyListener` instead of `Prompt.ask` for non-decision pauses.
