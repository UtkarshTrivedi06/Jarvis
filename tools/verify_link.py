"""
Jarvis Link Verification Spike
Tests and validates all hardware connections, external libraries, and data paths.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_pyqt6():
    print("[Link Test 1/5] Checking PyQt6...")
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    print("  -> PyQt6 initialized successfully.")
    return True

def test_audio():
    print("[Link Test 2/5] Checking sounddevice & microphone...")
    import sounddevice as sd
    devices = sd.query_devices()
    default_input = sd.default.device[0]
    print(f"  -> Default input device index: {default_input}")
    print(f"  -> Total audio devices found: {len(devices)}")
    return True

def test_telemetry():
    print("[Link Test 3/5] Checking psutil telemetry...")
    import psutil
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    print(f"  -> CPU: {cpu}% | RAM: {ram.percent}% ({ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB)")
    return True

def test_whisper():
    print("[Link Test 4/5] Checking faster-whisper...")
    import faster_whisper
    print(f"  -> faster-whisper version: {faster_whisper.__version__}")
    return True

def test_second_brain():
    print("[Link Test 5/5] Checking Second Brain local path...")
    sb_path = os.path.abspath(os.path.join(PROJECT_ROOT, "..", ".."))
    if os.path.exists(sb_path):
        md_count = 0
        for root, dirs, files in os.walk(sb_path):
            if ".git" in root or ".tmp" in root or "node_modules" in root:
                continue
            for f in files:
                if f.endswith(".md"):
                    md_count += 1
        print(f"  -> Second Brain path verified at '{sb_path}'. Found {md_count} markdown notes.")
        return True
    else:
        print(f"  -> Warning: Second Brain path '{sb_path}' not found directly.")
        return False

def main():
    print("=" * 60)
    print("      JARVIS DESKTOP ASSISTANT — LINK VERIFICATION SPIKE      ")
    print("=" * 60)
    
    results = [
        ("PyQt6 UI", test_pyqt6()),
        ("SoundDevice Audio", test_audio()),
        ("Psutil Telemetry", test_telemetry()),
        ("Faster-Whisper STT", test_whisper()),
        ("Second Brain Storage", test_second_brain()),
    ]
    
    print("\n" + "=" * 60)
    print("LINK VERIFICATION SUMMARY:")
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  - {name:<25}: {status}")
        if not passed:
            all_passed = False
    print("=" * 60)
    
    if all_passed:
        print("[Link Spike] All systems operational. Proceeding to Phase 3 Architect.")
    else:
        print("[Link Spike] Verification encountered issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
