## 2024-05-23 - Improving TUI Continuation Prompts
**Learning:** In TUI applications, requiring "Enter" to continue breaks the flow of keyboard-driven interfaces. Users expect "Press any key" behavior similar to `less` or `more` pagers.
**Action:** Replace `Prompt.ask("Press Enter...")` with non-blocking key listeners that accept any input. This reduces friction and feels more native to the terminal environment.
## 2025-05-18 - Press Any Key
**Learning:** In TUI apps, replacing "Press Enter to continue" with "Press any key" significantly reduces friction for repetitive tasks.
**Action:** Use `wait_for_key` with a polling loop and `KeyListener` instead of `Prompt.ask` for non-decision pauses.
## 2025-01-09 - [Fluid Navigation: Press Any Key]
**Learning:** Users prefer fluid navigation ("Press any key") over rigid interactions ("Press Enter") in TUI applications, especially for simple acknowledgments like continuing after a task.
**Action:** Implement `wait_for_key` utility using `KeyListener` or `tty/termios` for non-critical confirmations, replacing `Prompt.ask` where appropriate.
# Palette's UX Journal

## 2024-05-22 - Initial Setup
**Learning:** This journal tracks critical UX/accessibility learnings.
**Action:** Consult this file before making changes.

## 2025-01-12 - Duplicate TUI Methods & Prompt UX
**Learning:** In Rich TUI apps, `Text` objects with `blink` styles provide much better visibility for "Press any key" prompts than static strings. Also, duplicate method definitions in Python classes silently overwrite each other, leading to confusing API behavior.
**Action:** Use `rich.text.Text` for interactive prompts and ensure method uniqueness during refactoring.

## 2025-01-14 - Structured Data Presentation
**Learning:** Presenting structured data (like transaction logs) in a `rich.table.Table` with headers vastly improves scannability compared to simple text lists. It aligns the UI with the "Deep Scan" results and reinforces the "professional tool" feel.
**Action:** Always prefer `rich.table.Table` over formatted strings for multi-attribute lists.
