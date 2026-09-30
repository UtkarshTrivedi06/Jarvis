"""
Win32 Keystroke & OS Focus Simulation Layer
Provides ultra-low latency, deterministic keystrokes using ctypes user32 API.
"""

import ctypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_LWIN = 0x5B
VK_H = 0x48
KEYEVENTF_KEYUP = 0x0002

def force_foreground_window(hwnd: int) -> bool:
    """Brings the specified window handle to the absolute OS foreground."""
    try:
        current_foreground = user32.GetForegroundWindow()
        current_thread = kernel32.GetCurrentThreadId()
        fg_thread = user32.GetWindowThreadProcessId(current_foreground, None)
        
        if fg_thread != current_thread:
            user32.AttachThreadInput(fg_thread, current_thread, True)
            user32.AllowSetForegroundWindow(-1)
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
            user32.AttachThreadInput(fg_thread, current_thread, False)
        else:
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
        return True
    except Exception as e:
        print(f"[win_keys] Error focusing window: {e}")
        return False

def simulate_win_h():
    """Deterministic simulation of Win + H to trigger Windows Speech Dictation."""
    try:
        # Press Win
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        time.sleep(0.02)
        # Press H
        user32.keybd_event(VK_H, 0, 0, 0)
        time.sleep(0.05)
        # Release H
        user32.keybd_event(VK_H, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        # Release Win
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        print(f"[win_keys] Error simulating Win+H: {e}")
        return False
