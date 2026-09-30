# ⚡ Jarvis Desktop Assistant

A lightweight, zero-latency desktop overlay assistant for Windows built with Python, CustomTkinter, and native Windows Speech Dictation.

---

## ✨ Features

- **Global Activation (`Win + J`)**: Seamlessly invoke a sleek, floating dark-mode bar from anywhere in the OS without blocking background tasks.
- **Native Voice Dictation (`Win + H`)**: Automatically grabs foreground focus and triggers native Windows Speech Recognition directly into the input bar.
- **Clipboard Context Injection**: Automatically pairs clipboard text with voice queries (e.g. highlight code, press `Win + J`, say "Explain this").
- **Instant Dismissal (`Esc`)**: Drops window focus and hides instantly without lingering processes.
- **Deterministic B.L.A.S.T. Architecture**: Clean separation between Architecture SOPs, Layer 2 Navigation orchestrator, and Layer 3 execution tools.

---

## 🏗️ Architecture & File Structure

```
Jarvis/
├── main.py               # Layer 2: Main Orchestrator & lifecycle runner
├── architecture/         # Layer 1: Technical SOPs (The "How-To")
│   ├── sop_overlay_lifecycle.md
│   ├── sop_speech_dictation.md
│   └── sop_hotkey_daemon.md
├── tools/                # Layer 3: Deterministic Python Tools
│   ├── models.py         # Pydantic schemas (CapturedCommand, CommandExecutionResult)
│   ├── win_keys.py       # Win32 SendInput & focus elevation
│   ├── hotkey_daemon.py  # Thread-safe global hotkey listener
│   ├── overlay_window.py # Frameless CustomTkinter UI
│   ├── verify_link.py    # Connectivity spike tester
│   └── test_app.py       # Pipeline test suite
├── gemini.md             # Project Constitution & Data Schemas
├── task_plan.md          # B.L.A.S.T. Master Phase Tracker
├── findings.md           # Technical findings & constraints
└── progress.md           # Execution history
```

---

## 🚀 Quick Start

### 1. Requirements & Installation

```powershell
pip install customtkinter keyboard pywinauto pyperclip pynput pywin32 pydantic
```

### 2. Run Jarvis

```powershell
python main.py
```

### 3. Controls

- `Win + J`: Open / Toggle overlay
- Speak or type your command
- `Enter`: Submit command
- `Esc`: Dismiss overlay
