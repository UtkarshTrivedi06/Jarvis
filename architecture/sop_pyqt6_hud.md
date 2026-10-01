# 📐 SOP: PyQt6 Cyberpunk Tactical HUD Overlay

## Purpose
Defines the window lifecycle, rendering pipeline, micro-animations, and input handling for the Jarvis Desktop Assistant HUD.

## Architecture & Layout
1. **Window Specifications:**
   - Frameless (`Qt.WindowType.FramelessWindowHint`)
   - Always-on-top (`Qt.WindowType.WindowStaysOnTopHint`)
   - Transparent background attribute (`Qt.WidgetAttribute.WA_TranslucentBackground`)
   - Default dimensions: `760x170px`, auto-centered at top 18% of screen.
   - Expanded telemetry mode: `840x480px`.

2. **Visual Hierarchy:**
   - **Header Bar:**
     - Left Flank: Real-time CPU, RAM, and Network I/O metrics.
     - Center: Dynamic Vector Arc Reactor Core (custom QWidget with QPainter).
     - Right Flank: Quick Launcher buttons (CMD, VS Code, Second Brain).
   - **Input Section:** Glowing glassmorphic input box with keyboard and voice capture.
   - **Console Output Section:** Typewriter text stream with colored status pills (`[ 🎙️ LISTENING ]`, `[ ⚡ THINKING ]`, `[ 🚀 EXECUTED ]`).

3. **Arc Reactor Core:**
   - Ring 1 (Inner): Core reactor glowing circle with pulse.
   - Ring 2 (Middle): 12-segment rotating tick ring (counter-clockwise 12 RPM, accelerating to 60 RPM during processing).
   - Ring 3 (Outer): 8-16 radial audio reactive waveform bars scaling dynamically with microphone RMS volume.

4. **Lifecycle & Focus:**
   - Triggered by global `Win + J`.
   - Wakes, raises, and claims OS focus using Win32 API (`SetForegroundWindow`).
   - Dismisses immediately on `Esc` key or blur timeout.
