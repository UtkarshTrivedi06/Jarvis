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
    print("[Link Test 1/8] Checking PyQt6...")
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    print("  -> PyQt6 initialized successfully.")
    return True

def test_audio():
    print("[Link Test 2/8] Checking sounddevice & microphone...")
    import sounddevice as sd
    devices = sd.query_devices()
    default_input = sd.default.device[0]
    print(f"  -> Default input device index: {default_input}")
    print(f"  -> Total audio devices found: {len(devices)}")
    return True

def test_telemetry():
    print("[Link Test 3/8] Checking psutil telemetry...")
    import psutil
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    print(f"  -> CPU: {cpu}% | RAM: {ram.percent}% ({ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB)")
    return True

def test_whisper():
    print("[Link Test 4/8] Checking faster-whisper...")
    import faster_whisper
    print(f"  -> faster-whisper version: {faster_whisper.__version__}")
    return True

def test_second_brain():
    print("[Link Test 5/8] Checking Second Brain local path...")
    from tools.second_brain import SecondBrainEngine
    sb = SecondBrainEngine()
    notes = sb.search_notes("project", limit=3)
    print(f"  -> Second Brain search operational. Found {len(notes)} project matches.")
    return True

def test_sapi_tts():
    print("[Link Test 6/8] Checking Windows SAPI TTS...")
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    voices = speaker.GetVoices()
    voice_names = [voices.Item(i).GetDescription() for i in range(voices.Count)]
    print(f"  -> Found {len(voice_names)} SAPI voices: {', '.join(voice_names[:2])}")
    return True

def test_honcho_memory():
    print("[Link Test 7/8] Checking Honcho memory client...")
    from tools.memory_honcho import HonchoMemoryClient
    memory = HonchoMemoryClient(user_id="test_probe")
    ctx = memory.get_user_context()
    print(f"  -> Honcho Memory ready. Context: {ctx[:60]}...")
    return True

def test_hermes_agent():
    print("[Link Test 8/8] Checking Hermes 3 agent loop...")
    from tools.hermes_agent import HermesAgent
    agent = HermesAgent()
    resp, tools = agent.process_query("What is the system status?")
    print(f"  -> Hermes Agent responsive: '{resp[:60]}...' (Tools: {tools})")
    return True

def main():
    print("=" * 65)
    print("      J.A.R.V.I.S. SYSTEM VERIFICATION & DIAGNOSTIC SPIKE      ")
    print("=" * 65)
    
    results = [
        ("PyQt6 GUI Subsystem", test_pyqt6()),
        ("SoundDevice Input Stream", test_audio()),
        ("Psutil System Telemetry", test_telemetry()),
        ("Faster-Whisper STT Engine", test_whisper()),
        ("Second Brain Vault Search", test_second_brain()),
        ("Windows SAPI TTS Engine", test_sapi_tts()),
        ("Honcho Memory Layer", test_honcho_memory()),
        ("Hermes Agent Router", test_hermes_agent()),
    ]
    
    print("\n" + "=" * 65)
    print("DIAGNOSTIC SUMMARY:")
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  - {name:<30}: {status}")
        if not passed:
            all_passed = False
    print("=" * 65)
    
    if all_passed:
        print("[Diagnostic Spike] All 8 subsystems verified and fully operational.")
    else:
        print("[Diagnostic Spike] Subsystem anomalies detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
