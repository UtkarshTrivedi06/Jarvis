"""
J.A.R.V.I.S. System Control Engine
Executes Windows OS automation: Volume, Mute, Apps, File Search, and Browser.
"""

import os
import subprocess
import ctypes

user32 = ctypes.windll.user32

# Virtual key codes for volume
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_KEYUP = 0x0002

class SystemControlEngine:
    def __init__(self, second_brain_path: str = "d:/_Second Brain"):
        self.sb_path = os.path.abspath(second_brain_path)

    def volume_up(self, steps: int = 5) -> str:
        for _ in range(steps):
            user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
        return "Increasing audio volume, sir."

    def volume_down(self, steps: int = 5) -> str:
        for _ in range(steps):
            user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
        return "Lowering audio volume, sir."

    def volume_mute(self) -> str:
        user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
        return "Toggling audio mute, sir."

    def launch_app(self, app_name: str) -> str:
        app_lower = app_name.lower()
        try:
            if "code" in app_lower or "vs code" in app_lower:
                subprocess.Popen(["code", self.sb_path], shell=True)
                return "Launching Visual Studio Code with your Second Brain workspace, sir."
            elif "cmd" in app_lower or "terminal" in app_lower:
                subprocess.Popen(["cmd.exe"], cwd=self.sb_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return "Opening system terminal, sir."
            elif "explorer" in app_lower or "folder" in app_lower:
                subprocess.Popen(["explorer.exe", self.sb_path])
                return "Opening Second Brain vault in File Explorer, sir."
            elif "browser" in app_lower or "chrome" in app_lower:
                subprocess.Popen(["start", "https://google.com"], shell=True)
                return "Opening web browser, sir."
            else:
                # Attempt general execution
                subprocess.Popen([app_name], shell=True)
                return f"Launching {app_name}, sir."
        except Exception as e:
            return f"I encountered a slight anomaly launching {app_name}: {e}"
