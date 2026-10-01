"""
Jarvis Voice Engine
Low-latency direct microphone streaming via sounddevice + RMS amplitude calculation
and background faster-whisper transcription.
"""

import os
import time
import queue
import threading
import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Global lazy whisper model loader
_whisper_model = None
_model_lock = threading.Lock()

def get_whisper_model():
    global _whisper_model
    with _model_lock:
        if _whisper_model is None:
            from faster_whisper import WhisperModel
            # Load tiny.en quantized model for sub-200ms CPU inference
            print("[VoiceEngine] Loading faster-whisper (tiny.en INT8)...")
            _whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            print("[VoiceEngine] Whisper model loaded successfully.")
    return _whisper_model


class TranscriptionWorker(QThread):
    finished_transcription = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_data: np.ndarray, sample_rate: int = 16000):
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate

    def run(self):
        try:
            if len(self.audio_data) == 0:
                self.finished_transcription.emit("")
                return
                
            model = get_whisper_model()
            # Convert float32 numpy array to faster-whisper format
            segments, info = model.transcribe(
                self.audio_data,
                beam_size=1,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            text_segments = [seg.text.strip() for seg in segments]
            full_text = " ".join(text_segments).strip()
            self.finished_transcription.emit(full_text)
        except Exception as e:
            self.error_occurred.emit(str(e))


class VoiceEngine(QObject):
    amplitude_changed = pyqtSignal(float) # 0.0 - 1.0
    status_changed = pyqtSignal(str)     # "idle", "listening", "processing"
    transcription_ready = pyqtSignal(str)

    def __init__(self, sample_rate: int = 16000, parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.is_recording = False
        self._stream = None
        self._audio_buffer = []
        self._buffer_lock = threading.Lock()
        
        # VAD parameters
        self.silence_threshold = 0.015
        self.silence_limit_sec = 0.8
        self.speech_detected = False
        self.last_speech_time = 0.0
        self.worker = None

    def start_listening(self):
        """Starts real-time microphone capture buffer and amplitude stream."""
        if self.is_recording:
            return

        with self._buffer_lock:
            self._audio_buffer.clear()
        
        self.speech_detected = False
        self.last_speech_time = time.time()
        self.is_recording = True
        self.status_changed.emit("listening")

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=1024,
                callback=self._audio_callback
            )
            self._stream.start()
            print("[VoiceEngine] Microphone stream active (16kHz mono).")
        except Exception as e:
            print(f"[VoiceEngine] Failed to open microphone stream: {e}")
            self.is_recording = False
            self.status_changed.emit("idle")

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return

        # Compute RMS audio amplitude
        rms = float(np.sqrt(np.mean(np.square(indata))))
        normalized_amp = min(rms * 12.0, 1.0) # boost for visualization
        self.amplitude_changed.emit(normalized_amp)

        # Buffer data for transcription
        with self._buffer_lock:
            self._audio_buffer.append(indata.copy())

        # VAD & Silence tracking
        now = time.time()
        if rms > self.silence_threshold:
            self.speech_detected = True
            self.last_speech_time = now
        elif self.speech_detected and (now - self.last_speech_time > self.silence_limit_sec):
            # Auto-stop on silence cutoff
            self.stop_listening(auto_trigger=True)

    def stop_listening(self, auto_trigger: bool = False):
        """Stops microphone stream and triggers transcription."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.amplitude_changed.emit(0.0)
        
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        with self._buffer_lock:
            if self._audio_buffer:
                full_audio = np.concatenate(self._audio_buffer, axis=0).flatten()
            else:
                full_audio = np.array([], dtype=np.float32)

        if len(full_audio) > self.sample_rate * 0.3: # At least 300ms of audio
            self.status_changed.emit("processing")
            self._dispatch_transcription(full_audio)
        else:
            self.status_changed.emit("idle")

    def _dispatch_transcription(self, audio_data: np.ndarray):
        self.worker = TranscriptionWorker(audio_data, self.sample_rate)
        self.worker.finished_transcription.connect(self._on_transcription_finished)
        self.worker.error_occurred.connect(self._on_transcription_error)
        self.worker.start()

    def _on_transcription_finished(self, text: str):
        self.status_changed.emit("idle")
        self.transcription_ready.emit(text)

    def _on_transcription_error(self, err: str):
        print(f"[VoiceEngine] Transcription error: {err}")
        self.status_changed.emit("idle")
