"""
Global Hotkey Daemon Service
Runs hotkey listener on a background thread and notifies UI thread safely.
"""

import threading
import keyboard

class HotkeyDaemon:
    def __init__(self, hotkey: str = "windows+j", on_trigger=None):
        self.hotkey = hotkey
        self.on_trigger = on_trigger
        self._running = False
        self._thread = None

    def _listen(self):
        try:
            keyboard.add_hotkey(self.hotkey, self._handle_trigger, suppress=True)
            keyboard.wait()
        except Exception as e:
            print(f"[HotkeyDaemon] Keyboard hook notice: {e}")

    def _handle_trigger(self):
        if self.on_trigger:
            self.on_trigger()

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
            print(f"[HotkeyDaemon] Active and listening for '{self.hotkey}'")

    def stop(self):
        self._running = False
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
