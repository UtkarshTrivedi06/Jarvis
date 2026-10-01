# 📐 SOP: J.A.R.V.I.S. Full-Screen Holographic HUD

## Purpose
Defines the window lifecycle, full-screen holographic rendering, giant Arc Reactor animations, audio chimes, and zero text-box voice-driven interface.

## Architecture & Layout
1. **Window Specifications:**
   - Full-Screen (`showFullScreen()`)
   - Frameless (`Qt.WindowType.FramelessWindowHint`)
   - Always-on-top (`Qt.WindowType.WindowStaysOnTopHint`)
   - Transparent canvas (`Qt.WidgetAttribute.WA_TranslucentBackground`)
   - Background canvas: `#030508` at 0.92 opacity.

2. **Visual Hierarchy:**
   - **Top Header:** Stark Industries Holographic Header + `[ESC] TO DISMISS` hint.
   - **Center:** Giant Multi-Ring Animated Arc Reactor (360x360px `QPainter` vector graphics).
     - Concentric rotating segmented tracks (16 segments).
     - 16 radial dynamic audio-reactive waveform bars scaling in real-time with mic input.
     - Central high-intensity energy bloom and core disc.
     - Orbiting quantum particle streams.
   - **Bottom Subtitle Stream:** Glowing sci-fi status badge + typewriter subtitle stream.

3. **Audio Cues & Transitions:**
   - **Wake (`Win + J`):** Plays `wake.wav`, triggers HUD full-screen expansion.
   - **Listening:** Stark Cyan (`#00F0FF`) & Electric Blue (`#3B82F6`).
   - **Processing:** Amber Gold (`#F59E0B`), Arc Reactor accelerates to 90 RPM.
   - **Speaking:** Emerald Green (`#10B981`), SAPI voice output plays while subtitles type character-by-character.
   - **Dismiss (`Esc`):** Plays `dismiss.wav` and fades back to desktop.
