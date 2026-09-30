"""
B.L.A.S.T. Phase 2: Link Verification Spike Script
Tests all underlying Windows OS capabilities, GUI engine, clipboard, and key hooks.
"""

import sys
import time
import ctypes

def test_imports():
    print("[-] Testing imports...")
    import customtkinter as ctk
    import keyboard
    import pyperclip
    import pywinauto
    print(" [OK] All core dependencies imported successfully.")

def test_clipboard():
    print("[-] Testing clipboard access...")
    import pyperclip
    original = pyperclip.paste()
    test_str = f"__jarvis_link_test_{int(time.time())}__"
    pyperclip.copy(test_str)
    read_back = pyperclip.paste()
    assert read_back == test_str, f"Clipboard mismatch: expected {test_str}, got {read_back}"
    pyperclip.copy(original) # restore
    print(" [OK] Clipboard read/write verified.")

def test_win32_key_capabilities():
    print("[-] Testing Win32 native SendInput capability...")
    # Check if user32.dll SendInput is callable
    user32 = ctypes.windll.user32
    assert hasattr(user32, 'SendInput'), "user32.SendInput not found"
    assert hasattr(user32, 'SetForegroundWindow'), "user32.SetForegroundWindow not found"
    print(" [OK] Win32 OS keystroke and focus APIs verified.")

def main():
    print("=== Jarvis Link Verification Spike ===")
    try:
        test_imports()
        test_clipboard()
        test_win32_key_capabilities()
        print("\n>>> Phase 2: Link Handshake PASSED! All subsystems ready.")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Link verification failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
