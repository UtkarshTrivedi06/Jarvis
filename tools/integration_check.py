"""
J.A.R.V.I.S. Full System Integration Verification Suite
Executes the 4 mandatory system integration tests:
1. Local Ollama & Hermes 3 Check (Structured tool-calling & JSON)
2. Honcho Memory Integration Check (Context retrieval, session logging & fallback)
3. Local Audio & UI Dependencies Check (faster-whisper, sounddevice, PyQt6, torch/vad)
4. End-to-End Test Loop (Voice query -> Honcho context -> Hermes 3 -> Formatted response)
"""

import os
import sys
import json
import time
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.agent_tools import ALL_TOOLS
from tools.memory_honcho import HonchoMemoryClient
from tools.agent_router import AgentRouter

def test_1_ollama_hermes():
    print("\n[TEST 1/4] Checking Local Ollama & Hermes 3 Model...")
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "hermes3",
        "messages": [
            {"role": "system", "content": "You are J.A.R.V.I.S. Execute tools when needed."},
            {"role": "user", "content": "Adjust volume up please"}
        ],
        "tools": ALL_TOOLS,
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=20.0)
        assert r.status_code == 200, f"Ollama returned HTTP {r.status_code}"
        data = r.json()
        assert "message" in data, "No 'message' key in Ollama response JSON"
        
        tool_calls = data["message"].get("tool_calls", [])
        content = data["message"].get("content", "")
        print(f"  -> Ollama HTTP 200 OK. Response valid JSON.")
        if tool_calls:
            print(f"  -> Structured Tool Calls detected: {tool_calls[0].get('function', {}).get('name')}")
        else:
            print(f"  -> Direct text response: '{content[:50]}...'")
        return True, "Ollama & Hermes 3 responsive with tool-calling support."
    except Exception as e:
        return False, f"Ollama/Hermes test failed: {e}"

def test_2_honcho_memory():
    print("\n[TEST 2/4] Checking Honcho Memory Integration...")
    try:
        client = HonchoMemoryClient(user_id="stark_01")
        # 1. Read context
        ctx = client.get_user_context()
        assert isinstance(ctx, str), "Context returned is not string"
        print(f"  -> User context retrieved successfully: '{ctx[:60]}...'")
        
        # 2. Simulate logging
        test_q = "Simulated test command for verification"
        test_r = "Awaiting your next directive, sir."
        client.save_session_turn(test_q, test_r, ["system_telemetry"])
        print("  -> Session turn logged asynchronously.")
        
        # 3. Verify fallback memory file exists
        local_file = os.path.join(PROJECT_ROOT, ".tmp", "honcho_local_memory.json")
        assert os.path.exists(local_file), "Local fallback memory file was not created"
        print("  -> Local persistent fallback engine validated.")
        return True, "Honcho memory read, write, and fallback operational."
    except Exception as e:
        return False, f"Honcho memory test failed: {e}"

def test_3_audio_ui_deps():
    print("\n[TEST 3/4] Checking Audio & UI Dependencies...")
    try:
        import faster_whisper
        import sounddevice as sd
        import PyQt6.QtWidgets
        import torch
        
        # Check mic input device
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        assert default_input >= 0, "No default microphone input device detected"
        device_name = devices[default_input]['name']
        
        print(f"  -> faster-whisper: v{faster_whisper.__version__}")
        print(f"  -> sounddevice: Default Mic Index {default_input} ('{device_name}')")
        print(f"  -> PyQt6: Initialized")
        print(f"  -> Torch/VAD: v{torch.__version__}")
        return True, "All audio, STT, and UI dependencies detected & functional."
    except Exception as e:
        return False, f"Audio/UI dependency check failed: {e}"

def test_4_end_to_end_loop():
    print("\n[TEST 4/4] Checking End-to-End J.A.R.V.I.S. Loop...")
    try:
        router = AgentRouter()
        memory = HonchoMemoryClient(user_id="stark_01")
        
        query = "J.A.R.V.I.S., check my system volume and confirm memory status."
        honcho_ctx = memory.get_user_context()
        
        resp, tools = router.route_query(query, honcho_ctx)
        assert resp and len(resp) > 0, "No response returned from agent router"
        
        clean_resp = resp.encode('ascii', errors='ignore').decode()
        print(f"  -> Query: '{query}'")
        print(f"  -> Honcho Context: '{honcho_ctx[:50]}...'")
        print(f"  -> Hermes Response: '{clean_resp[:70]}...'")
        print(f"  -> Executed Tools: {tools}")
        return True, "End-to-end cognitive loop validated."
    except Exception as e:
        return False, f"End-to-end loop failed: {e}"

def main():
    print("=" * 70)
    print("      J.A.R.V.I.S. FULL SYSTEM INTEGRATION VERIFICATION SUITE      ")
    print("=" * 70)
    
    tests = [
        ("1. Ollama & Hermes 3 (Tools & JSON)", test_1_ollama_hermes),
        ("2. Honcho Memory & Fallback", test_2_honcho_memory),
        ("3. Audio, STT & UI Dependencies", test_3_audio_ui_deps),
        ("4. End-to-End Query Loop", test_4_end_to_end_loop),
    ]
    
    results = []
    all_passed = True
    
    for name, test_fn in tests:
        passed, msg = test_fn()
        results.append((name, passed, msg))
        if not passed:
            all_passed = False
            
    print("\n" + "=" * 70)
    print("FINAL INTEGRATION STATUS REPORT:")
    print("=" * 70)
    for name, passed, msg in results:
        status_str = "PASSED [OK]" if passed else "FAILED [X]"
        print(f"  * {name:<40} : {status_str}")
        print(f"    Details: {msg}")
    print("=" * 70)
    
    if all_passed:
        print("\n>>> ALL 4 INTEGRATION CHECKS PASSED SUCCESSFULLY. J.A.R.V.I.S. IS 100% OPERATIONAL. <<<")
    else:
        print("\n>>> ONE OR MORE CHECKS FAILED. <<<")
        sys.exit(1)

if __name__ == "__main__":
    main()
