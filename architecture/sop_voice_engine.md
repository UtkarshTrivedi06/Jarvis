# 🎙️ SOP: Direct Voice & Audio Stream Engine

## Purpose
Specifies the real-time microphone capture, RMS amplitude calculation, voice activity detection (VAD), and background `faster-whisper` transcription pipeline.

## Audio Processing Flow
1. **Direct Stream Initialization:**
   - Uses `sounddevice.InputStream` configured with 16kHz sampling rate, mono channel, float32 format.
   - Operates in a non-blocking stream callback.

2. **RMS Amplitude & Reactive Waves:**
   - In each audio callback (block size: 1024 or 2048 samples), calculates Root Mean Square (RMS):
     `rms = np.sqrt(np.mean(np.square(indata)))`
   - Emits amplitude value (0.0 to 1.0 scale) via Qt signal `amplitude_changed(float)` to drive Arc Reactor visualizer bars at ~30-60 FPS.

3. **Voice Activity Detection (VAD) & Silence Detection:**
   - Tracks speech energy. When amplitude exceeds threshold (> 0.015), speech active state begins.
   - When amplitude remains below threshold for > 800ms after speech, auto-stops recording and passes buffer to transcription.

4. **Quantized Local Transcription (`faster-whisper`):**
   - Transcribes audio buffer using `faster-whisper` model (`tiny.en` / `base.en` with INT8 quantization on CPU/GPU).
   - Runs in a background `QThread` or worker thread to ensure the GUI remains buttery smooth at 60 FPS.
   - Emits `transcription_completed(str)` signal back to HUD.
