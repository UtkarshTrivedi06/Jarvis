"""
Jarvis Desktop Assistant — Layer 2 Navigation / Orchestration
Connects PyQt6 Tactical HUD Overlay, Live Voice Engine, Telemetry Monitor,
Second Brain Engine, App Launcher, and Global Hotkey Daemon into a unified system.
"""

import os
import sys
import uuid
import json
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot, QTimer

from tools.models import CapturedCommand, CommandExecutionResult
from tools.hud_overlay import JarvisHUDOverlay
from tools.voice_engine import VoiceEngine
from tools.system_telemetry import TelemetryMonitor
from tools.second_brain import SecondBrainEngine
from tools.app_launcher import AppLauncher
from tools.hotkey_daemon import HotkeyDaemon

TMP_DIR = os.path.join(PROJECT_ROOT, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(TMP_DIR, "captured_commands.jsonl")


class JarvisOrchestrator(QObject):
    def __init__(self):
        super().__init__()
        print("[Jarvis] Initializing Layer 2 Orchestrator...")
        
        # 1. Initialize Subsystems (Layer 3 Tools)
        self.hud = JarvisHUDOverlay(on_submit=self.handle_command)
        self.voice = VoiceEngine()
        self.telemetry = TelemetryMonitor(update_interval_ms=1500)
        self.second_brain = SecondBrainEngine()
        self.launcher = AppLauncher()
        
        # 2. Wire Signal Pipelines
        self._wire_signals()
        
        # 3. Initialize Global Hotkey Daemon ('Win + J')
        self.hotkey_daemon = HotkeyDaemon(
            hotkey="windows+j",
            on_trigger=self._on_hotkey_triggered
        )

    def _wire_signals(self):
        # Audio amplitude -> Arc Reactor waveform visualizer
        self.voice.amplitude_changed.connect(self.hud.set_amplitude)
        
        # Voice status changes -> HUD state pills & colors
        self.voice.status_changed.connect(lambda s: self.hud.set_hud_state(s))
        
        # Voice transcription completed -> Route to command handler
        self.voice.transcription_ready.connect(self._on_voice_transcription)
        
        # Telemetry updates -> HUD left flank
        self.telemetry.telemetry_updated.connect(self.hud.update_telemetry)
        
        # HUD quick buttons -> App launcher
        self.hud.shortcut_triggered.connect(self.handle_shortcut)

    def _on_hotkey_triggered(self):
        """Dispatched when global Win + J is pressed."""
        print("[Jarvis] Global Hotkey (Win + J) pressed.")
        if self.hud.is_visible_state:
            self.voice.stop_listening()
            self.hud.hide_overlay()
        else:
            self.hud.show_overlay()
            self.hud.stream_response("Listening for your command...")
            self.voice.start_listening()

    def _on_voice_transcription(self, text: str):
        """Called when speech transcription finishes."""
        if not text:
            self.hud.stream_response("No speech detected. Ready for input.")
            return

        print(f"[Jarvis] Transcribed Speech: '{text}'")
        self.hud.set_input_text(text)
        self.hud._from_voice = True
        # Auto-submit transcribed command
        self.hud._handle_submit()

    def handle_shortcut(self, shortcut_name: str):
        """Handles clicks on HUD quick tool buttons."""
        if shortcut_name == "cmd":
            self.launcher.launch_cmd()
            self.hud.set_hud_state("success", "Launched Command Prompt terminal.")
        elif shortcut_name == "vscode":
            self.launcher.launch_vscode()
            self.hud.set_hud_state("success", "Launched Visual Studio Code.")
        elif shortcut_name == "second_brain":
            notes = self.second_brain.search_notes("project", limit=1)
            target = notes[0]["file_path"] if notes else self.second_brain.root_dir
            self.launcher.launch_vscode(target)
            self.hud.set_hud_state("success", f"Opened Second Brain in VS Code: {os.path.basename(target)}")

    def handle_command(self, cmd: CapturedCommand) -> CommandExecutionResult:
        """Main cognitive routing engine for user queries."""
        cmd_id = str(uuid.uuid4())
        print(f"\n[Jarvis] Executing Command [{cmd_id}] ({cmd.target_scope}): '{cmd.raw_text}'")
        self.hud.set_hud_state("processing", f"Decoding: '{cmd.raw_text}'...")

        # Log payload to .tmp/
        log_entry = {
            "id": cmd_id,
            "timestamp": cmd.timestamp,
            "trigger_source": cmd.trigger_source,
            "raw_text": cmd.raw_text,
            "clipboard_context": cmd.clipboard_context,
            "target_scope": cmd.target_scope
        }
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        raw_lower = cmd.raw_text.lower()
        action_type = "text_response"
        file_path_accessed = None
        response_msg = ""

        # Scope 1: Second Brain Search & Notes
        if cmd.target_scope == "second_brain" or any(k in raw_lower for k in ["note", "second brain", "brain", "challenge", "samay"]):
            # Extract search keyword
            clean_query = raw_lower.replace("open", "").replace("search", "").replace("my", "").replace("note", "").replace("second brain", "").replace("on", "").replace("for", "").strip()
            if not clean_query:
                clean_query = "project"
                
            matches = self.second_brain.search_notes(clean_query, limit=3)
            if matches:
                top = matches[0]
                action_type = "read_note"
                file_path_accessed = top["file_path"]
                
                # If command requested to open/launch
                if "open" in raw_lower or "launch" in raw_lower:
                    self.launcher.open_file(top["file_path"])
                    response_msg = f"Opened note '{top['file_name']}' in editor. Snippet: {top['snippet']}"
                else:
                    response_msg = f"Found note '{top['file_name']}': \"{top['snippet']}\" ({top['rel_path']})"
            else:
                response_msg = f"No markdown notes found matching '{clean_query}' in Second Brain."

        # Scope 2: App Launcher & System Execution
        elif cmd.target_scope == "app_launcher" or any(k in raw_lower for k in ["open", "launch", "run"]):
            action_type = "launch_app"
            if "cmd" in raw_lower or "terminal" in raw_lower or "command prompt" in raw_lower:
                self.launcher.launch_cmd()
                response_msg = "Spawned Windows Command Prompt."
            elif "code" in raw_lower or "vs code" in raw_lower:
                self.launcher.launch_vscode()
                response_msg = "Launched Visual Studio Code workspace."
            elif "explorer" in raw_lower or "folder" in raw_lower:
                self.launcher.launch_explorer()
                response_msg = "Opened Windows File Explorer."
            else:
                response_msg = f"Executed launch directive for '{cmd.raw_text}'."

        # Scope 3: Telemetry Query
        elif cmd.target_scope == "system_telemetry" or any(k in raw_lower for k in ["cpu", "ram", "stat", "performance"]):
            action_type = "telemetry"
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            response_msg = f"System Telemetry: CPU is at {cpu}%, RAM usage is {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)."

        # Scope 4: General Query Fallback
        else:
            action_type = "text_response"
            response_msg = f"Jarvis Acknowledged: '{cmd.raw_text}'. Context recorded."

        result = CommandExecutionResult(
            command_id=cmd_id,
            action_type=action_type,
            status="success",
            response_text=response_msg,
            file_path_accessed=file_path_accessed
        )

        # Update HUD to success state with typewriter animation
        self.hud.set_hud_state("success", response_msg)
        return result

    def start(self):
        print("[Jarvis] Starting Telemetry polling & Global Hotkey Daemon...")
        self.telemetry.start()
        self.hotkey_daemon.start()
        print("\n========================================================")
        print("  JARVIS DESKTOP ASSISTANT v2.0 IS ONLINE AND READY     ")
        print("  - Global Hotkey: Press 'Win + J' to summon HUD       ")
        print("  - Dismiss: Press 'Esc'                               ")
        print("  - Real-time Micro-Animated Arc Reactor Core Active    ")
        print("========================================================\n")


def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    orchestrator = JarvisOrchestrator()
    orchestrator.start()
    
    # Run Qt Event Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
