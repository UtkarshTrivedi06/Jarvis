"""
Global Hotkey Daemon Service (OS-Wide Win + J Listener)
Uses native Win32 RegisterHotKey with keyboard hook fallback to guarantee
instant overlay activation from any window across the entire operating system.
"""

import ctypes
import ctypes.wintypes
import threading
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

user32 = ctypes.windll.user32

MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
VK_J = 0x4A
HOTKEY_ID = 1001
WM_HOTKEY = 0x0312

class HotkeyDaemon(QObject):
    triggered = pyqtSignal()

    def __init__(self, hotkey: str = "windows+j", on_trigger=None, parent=None):
        super().__init__(parent)
        self.hotkey = hotkey
        self.on_trigger = on_trigger
        self._running = False
        self._thread = None
        self._win32_registered = False

        if on_trigger:
            self.triggered.connect(on_trigger)

    def _listen_win32(self):
        """Native Windows RegisterHotKey message loop for system-wide Win + J."""
        try:
            # Register OS-wide hotkey
            success = user32.RegisterHotKey(None, HOTKEY_ID, MOD_WIN | MOD_NOREPEAT, VK_J)
            if success:
                self._win32_registered = True
                print("[HotkeyDaemon] OS-wide Win32 'Win + J' registered successfully.")
            else:
                # Try without MOD_NOREPEAT if older subsystem
                success = user32.RegisterHotKey(None, HOTKEY_ID, MOD_WIN, VK_J)
                if success:
                    self._win32_registered = True
                    print("[HotkeyDaemon] OS-wide Win32 'Win + J' registered.")
                else:
                    print("[HotkeyDaemon] RegisterHotKey unavailable, using keyboard hook fallback.")
        except Exception as e:
            print(f"[HotkeyDaemon] Win32 registration error: {e}")

        if self._win32_registered:
            msg = ctypes.wintypes.MSG()
            while self._running:
                # Pump Windows messages
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.triggered.emit()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            user32.UnregisterHotKey(None, HOTKEY_ID)
        else:
            # Fallback to keyboard hook
            try:
                keyboard.add_hotkey(self.hotkey, self._handle_trigger, suppress=False)
                keyboard.wait()
            except Exception as e:
                print(f"[HotkeyDaemon] Keyboard fallback error: {e}")

    def _handle_trigger(self):
        self.triggered.emit()

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._listen_win32, daemon=True)
            self._thread.start()
            print(f"[HotkeyDaemon] Active and listening for '{self.hotkey}' across all windows.")

    def stop(self):
        self._running = False
        if self._win32_registered:
            try:
                user32.PostThreadMessageW(self._thread.ident, 0x0012, 0, 0) # WM_QUIT
            except Exception:
                pass
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
