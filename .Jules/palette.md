## 2024-05-23 - Improving TUI Continuation Prompts
**Learning:** In TUI applications, requiring "Enter" to continue breaks the flow of keyboard-driven interfaces. Users expect "Press any key" behavior similar to `less` or `more` pagers.
**Action:** Replace `Prompt.ask("Press Enter...")` with non-blocking key listeners that accept any input. This reduces friction and feels more native to the terminal environment.
