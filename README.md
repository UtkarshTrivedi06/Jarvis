# ⚡ Jarvis Desktop Assistant (Cyberpunk Tactical HUD v2.0)

A high-performance, low-latency desktop assistant overlay for Windows built with **PyQt6**, **sounddevice**, **faster-whisper (INT8 quantized)**, and local **Second Brain** knowledge integration.

---

## ✨ Key Features

- **Global Activation (`Win + J`)**: Seamlessly invoke a sleek floating tactical HUD from anywhere in Windows with instant OS foreground focus.
- **Micro-Animated Arc Reactor Core**:
  - Custom vector-rendered 3-track rotating HUD core (`QPainter`).
  - Real-time audio-reactive radial waveform equalizer bars scaling dynamically with microphone RMS volume.
  - State acceleration (12 RPM idle ➔ 60 RPM on processing/thinking) with orbiting particle effects.
- **Direct Low-Latency Speech Engine**:
  - Streams microphone audio directly into memory via `sounddevice` (16kHz mono).
  - Sub-200ms local transcription using `faster-whisper` quantized models (`tiny.en` INT8).
  - Zero reliance on external Windows Dictation overlays (`Win + H`).
- **Local Second Brain Integration**:
  - Instant multi-token search across all Markdown notes in `d:/_Second Brain`.
  - Preview note titles, snippets, and open notes directly in VS Code / default editor.
- **Real-Time System Telemetry**:
  - Live CPU %, RAM GB usage, and Network upload/download bandwidth counters powered by `psutil`.
- **Quick Tactical Shortcuts**:
  - One-click launcher buttons for Command Prompt (`CMD`), Visual Studio Code (`VS CODE`), and Second Brain (`2ND BRAIN`).
- **Terminal Typewriter Stream**:
  - Smooth character-by-character response streaming with glowing cyber status badges (`[ 🎙️ LISTENING ]`, `[ ⚡ DECODING INTENT ]`, `[ 🚀 EXECUTED ]`).
- **Instant Dismissal (`Esc`)**:
  - Yields focus and hides overlay instantly.

---

## 🏗️ Architecture & File Structure (B.L.A.S.T.)

```
Jarvis/
├── main.py                     # Layer 2: Main Orchestrator & Qt Event Loop
├── architecture/               # Layer 1: Technical SOPs (The "How-To")
│   ├── sop_pyqt6_hud.md        # Window geometry, Arc Reactor, styling, focus
│   ├── sop_voice_engine.md     # sounddevice stream, RMS calculation, faster-whisper
│   ├── sop_second_brain.md     # Markdown indexing, ranking search engine
│   ├── sop_app_launcher.md     # Application & shortcut execution
│   └── sop_hotkey_daemon.md    # Background keyboard listener & signal dispatch
├── tools/                      # Layer 3: Deterministic Python Tools
│   ├── models.py               # Pydantic schemas (CapturedCommand, CommandExecutionResult)
│   ├── hud_overlay.py          # PyQt6 Tactical HUD & Arc Reactor vector widget
│   ├── voice_engine.py         # sounddevice stream + RMS audio waveform + faster-whisper worker
│   ├── second_brain.py         # Fast search & parser for Second Brain notes
│   ├── system_telemetry.py     # Live CPU, RAM, and Network polling
│   ├── app_launcher.py         # App and note launching engine
│   ├── hotkey_daemon.py        # Global Win + J listener
│   ├── win_keys.py             # Win32 foreground window management
│   ├── verify_link.py          # Link verification spike script
│   └── test_app.py             # Automated unit test suite (5/5 passed)
├── gemini.md                   # Project Constitution & Data Schemas
├── task_plan.md                # B.L.A.S.T. Master Phase Tracker
├── findings.md                 # Technical findings & architectural decisions
├── progress.md                 # Execution history & milestones
└── task-spec.md                # Core functional specification
```

---

## 🚀 Quick Start

### 1. Requirements & Dependencies

Ensure dependencies are installed:
```powershell
pip install PyQt6 sounddevice psutil faster-whisper numpy keyboard pyperclip pywin32
```

### 2. Verify Connectivity & Run Tests

```powershell
python tools/verify_link.py
python tools/test_app.py
```

### 3. Launch Jarvis

```powershell
python main.py
```

### 4. Interactive Controls

- `Win + J`: Summon / Dismiss Jarvis HUD
- **Speak naturally**: Audio level activates the glowing radial waveform bars and automatically transcribes intent on silence
- **Type command**: e.g., `"Search note for SAMAY"`, `"Open VS Code"`, `"System stats"`, then hit `Enter`
- `Esc`: Instantly dismiss overlay
