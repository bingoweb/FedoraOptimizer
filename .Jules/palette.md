# Palette's Journal

## 2025-05-19 - Press Any Key
**Learning:** In a `rich`-based TUI, `Prompt.ask` forces a line-buffered input (Enter key), which interrupts the flow of quick interactions. Users prefer single-key acknowledgement ("Press any key") for informational pauses.
**Action:** Use `tty.setcbreak` (via `KeyListener`) with `sys.stdin.read(1)` for blocking single-key waits, instead of `Prompt.ask`. Ensure the user is prompted with "Press any key" instead of "Press Enter".
