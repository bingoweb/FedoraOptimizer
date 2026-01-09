## 2025-01-09 - [Fluid Navigation: Press Any Key]
**Learning:** Users prefer fluid navigation ("Press any key") over rigid interactions ("Press Enter") in TUI applications, especially for simple acknowledgments like continuing after a task.
**Action:** Implement `wait_for_key` utility using `KeyListener` or `tty/termios` for non-critical confirmations, replacing `Prompt.ask` where appropriate.
