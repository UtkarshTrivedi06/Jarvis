# ⚡ SOP: System Shortcuts & Application Launcher

## Purpose
Defines deterministic execution of system commands, opening native Windows applications, and launching files.

## Actions & Mappings
1. **Quick Tools:**
   - **CMD:** Opens Windows Command Prompt (`cmd.exe`).
   - **VS Code:** Launches `code <workspace_path>`.
   - **Second Brain (SB):** Opens default Second Brain directory or specific Markdown notes.
   - **Explorer:** Opens Windows File Explorer at active project folder.
2. **Deterministic Invocation:**
   - Uses `subprocess.Popen` or `os.startfile` with non-blocking execution to keep HUD responsive.
   - Captures launch status and reports back via `CommandExecutionResult`.
