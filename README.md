# ⚡ J.A.R.V.I.S. (Stark Tech Full-Screen Holographic HUD)

A zero-friction, hands-free **J.A.R.V.I.S.** autonomous voice agent for Windows built with **PyQt6**, **sounddevice**, **faster-whisper (INT8 quantized)**, **Nous Hermes 3 Agent Loop**, **Honcho Adaptive Memory**, **Windows SAPI TTS**, and **Second Brain** knowledge vault integration.

---

## ✨ Features

- **Global Hotkey (`Win + J`)**: Summon J.A.R.V.I.S. from any application, game, or window across Windows.
- **Full-Screen Holographic HUD**:
  - Dark glassmorphic canvas (`#030508`, 0.92 opacity) covering the entire display.
  - **Zero Text-Box Invariant**: Pure graphical HUD without clunky text boxes. 100% voice-driven.
  - **Giant Animated Arc Reactor Core**: Multi-ring concentric rotating tracks, 16 radial audio-reactive waveform bars scaling in real-time with your microphone, and orbiting quantum energy particles.
- **Nous Hermes 3 Agent Router**:
  - Local Ollama endpoint (`hermes3`) with function calling across modular agent tools.
  - Sub-second deterministic fallback if offline.
- **Honcho Long-Term Adaptive Memory**:
  - Automatically enriches system context with user preferences and historical interactions.
  - Seamless offline local caching fallback.
- **Audio Chimes & Cues**:
  - Sci-fi startup chime (`wake.wav`) on `Win + J` activation.
  - Powering-down chime (`dismiss.wav`) on dismissal.
- **Dynamic State Transitions**:
  - **Listening State:** Stark Cyan (`#00F0FF`) & Electric Blue (`#3B82F6`) with live audio waveform bars.
  - **Hermes Reasoning / Tool Execution:** Amber Gold (`#F59E0B`), Arc Reactor accelerates from 15 RPM to 90 RPM with orbiting particles.
  - **Speaking / Action:** Emerald Green (`#10B981`), local voice response plays while minimalist subtitles stream across the screen.
- **Local Voice Output (TTS) & Iron Man Persona**:
  - Sophisticated, polite, and witty J.A.R.V.I.S. persona ("At your service, sir", "Right away, sir").
  - 100% local Windows SAPI speech synthesis with zero cloud latency.
- **Second Brain Vault Interrogation**:
  - Search notes, read summaries, and launch note files directly in VS Code by voice.
- **OS Automation Drivers**:
  - Voice-controlled volume adjustments (Up, Down, Mute) and application launching (VS Code, Terminal, Browser, Explorer).

---

## 🏗️ Architecture (B.L.A.S.T.)

```
Jarvis/
├── main.py                     # Layer 2: Main Cognitive Orchestrator
├── architecture/               # Layer 1: Technical SOPs
│   ├── sop_pyqt6_hud.md        # Full-Screen HUD & Arc Reactor specifications
│   ├── sop_voice_engine.md     # sounddevice stream, RMS waveform, faster-whisper
│   ├── sop_second_brain.md     # Markdown indexing & vault search engine
│   ├── sop_app_launcher.md     # System & app execution SOP
│   └── sop_hotkey_daemon.md    # OS-wide Win32 RegisterHotKey listener
├── tools/                      # Layer 3: Deterministic Tools
│   ├── agent_tools/            # Modular Hermes tool registry
│   │   ├── vault_tools.py      # Search, read, and open Second Brain notes
│   │   └── system_tools.py     # Volume control, mute, apps, telemetry
│   ├── memory_honcho.py        # Honcho adaptive memory client
│   ├── hermes_agent.py         # Nous Hermes 3 agent router & fallback
│   ├── hud_overlay.py          # Full-Screen Holographic HUD & Giant Arc Reactor
│   ├── voice_engine.py         # sounddevice buffer + RMS waveform + faster-whisper
│   ├── tts_engine.py           # Background Windows SAPI voice synthesizer
│   ├── audio_sfx.py            # Procedural sci-fi chimes generator & player
│   ├── system_controls.py      # Volume control, mute, and app launching
│   ├── second_brain.py         # Local Markdown note search and reader
│   ├── hotkey_daemon.py        # Global Win + J listener
│   ├── models.py               # Pydantic data schemas
│   ├── verify_link.py          # Connectivity tester
│   └── test_app.py             # Unit test suite (5/5 passed)
├── assets/sounds/              # Sci-fi sound chimes (wake.wav, dismiss.wav)
├── gemini.md                   # Project Constitution & Data Schemas
├── task_plan.md                # B.L.A.S.T. Phase Tracker
├── findings.md                 # Technical notes & discoveries
└── progress.md                 # Execution history
```

---

## 🚀 Quick Start

### 1. Launch J.A.R.V.I.S.

```powershell
python main.py
```

### 2. Voice Commands

- Press `Win + J` anywhere on Windows
- Say:
  - *"Search note for SAMAY"* ➔ Interrogates vault & speaks summary
  - *"Open note for SAMAY"* ➔ Launches note in VS Code
  - *"Increase volume"* / *"Mute"* ➔ Adjusts Windows audio
  - *"Launch terminal"* / *"Open VS Code"* ➔ Spawns applications
  - *"System diagnostics"* / *"Who are you?"* ➔ Conversational persona response
- Press `Esc` anytime to dismiss
