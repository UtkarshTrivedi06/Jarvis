"""
Jarvis App & File Launcher
Provides non-blocking Windows app execution, terminal spawning, and file opening.
"""

import os
import subprocess
from typing import Optional

class AppLauncher:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    def launch_cmd(self, working_dir: Optional[str] = None) -> bool:
        """Launches Windows Command Prompt."""
        cwd = working_dir or self.workspace_root
        try:
            subprocess.Popen(["cmd.exe"], cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
        except Exception as e:
            print(f"[AppLauncher] Error launching CMD: {e}")
            return False

    def launch_vscode(self, target_path: Optional[str] = None) -> bool:
        """Launches Visual Studio Code opening target file or workspace."""
        path = target_path or self.workspace_root
        try:
            subprocess.Popen(["code", path], shell=True)
            return True
        except Exception as e:
            print(f"[AppLauncher] Error launching VS Code: {e}")
            return False

    def launch_explorer(self, target_path: Optional[str] = None) -> bool:
        """Opens Windows File Explorer at target path."""
        path = target_path or self.workspace_root
        try:
            subprocess.Popen(["explorer.exe", path])
            return True
        except Exception as e:
            print(f"[AppLauncher] Error opening Explorer: {e}")
            return False

    def open_file(self, file_path: str) -> bool:
        """Opens a file with its default Windows associated program."""
        if not os.path.exists(file_path):
            return False
        try:
            os.startfile(file_path)
            return True
        except Exception as e:
            print(f"[AppLauncher] Error opening file: {e}")
            return False
