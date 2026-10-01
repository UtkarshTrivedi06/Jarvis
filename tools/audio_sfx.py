"""
Procedural Sci-Fi Sound FX Generator & Player for J.A.R.V.I.S.
Generates and plays crisp, futuristic wake and dismiss chimes using native winsound.
"""

import os
import wave
import struct
import math
import winsound
import numpy as np

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
os.makedirs(ASSETS_DIR, exist_ok=True)

WAKE_WAV = os.path.join(ASSETS_DIR, "wake.wav")
DISMISS_WAV = os.path.join(ASSETS_DIR, "dismiss.wav")

def generate_sci_fi_chimes():
    """Generates futuristic harmonic chimes if they don't already exist."""
    sample_rate = 44100
    
    # 1. Wake Sound: Rising high-tech dual-harmonic pulse
    if not os.path.exists(WAKE_WAV):
        duration = 0.28
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Rising frequency chirp (580Hz -> 1160Hz) with harmonic sheen (1740Hz)
        freq = np.linspace(587.33, 1174.66, n_samples) # D5 to D6
        envelope = np.sin(np.pi * np.power(t / duration, 0.6))
        
        wave_data = 0.5 * np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 1.5 * t) + 0.2 * np.sin(2 * np.pi * freq * 2.0 * t)
        wave_data = (wave_data * envelope * 32767 * 0.8).astype(np.int16)
        
        with wave.open(WAKE_WAV, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(wave_data.tobytes())

    # 2. Dismiss Sound: Soft descending power-down pulse
    if not os.path.exists(DISMISS_WAV):
        duration = 0.22
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Descending frequency (880Hz -> 320Hz)
        freq = np.linspace(880.0, 329.63, n_samples)
        envelope = np.exp(-t * 12.0)
        
        wave_data = 0.6 * np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 0.5 * t)
        wave_data = (wave_data * envelope * 32767 * 0.7).astype(np.int16)
        
        with wave.open(DISMISS_WAV, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(wave_data.tobytes())

def play_wake_sound():
    """Plays sci-fi wake chime asynchronously without blocking."""
    try:
        generate_sci_fi_chimes()
        winsound.PlaySound(WAKE_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"[AudioSFX] Notice: {e}")

def play_dismiss_sound():
    """Plays sci-fi power-down chime asynchronously without blocking."""
    try:
        generate_sci_fi_chimes()
        winsound.PlaySound(DISMISS_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"[AudioSFX] Notice: {e}")

if __name__ == "__main__":
    generate_sci_fi_chimes()
    print("Synthesized sci-fi chimes in:", ASSETS_DIR)
    play_wake_sound()
