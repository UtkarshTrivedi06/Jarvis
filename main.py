"""
J.A.R.V.I.S. Autonomous Desktop Assistant — Layer 2 Orchestration
Connects Full-Screen Holographic HUD, Direct Voice Engine, Local TTS Voice Output,
Second Brain Vault Engine, System Controls, and Global Hotkey Daemon into a unified assistant.
"""

import os
import sys
import uuid
import json
import re
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot, QTimer

from tools.models import CapturedCommand, CommandExecutionResult
from tools.hud_overlay import JarvisHUDOverlay
from tools.voice_engine import VoiceEngine
from tools.tts_engine import TTSEngine
from tools.second_brain import SecondBrainEngine
from tools.system_controls import SystemControlEngine
from tools.hotkey_daemon import HotkeyDaemon

TMP_DIR = os.path.join(PROJECT_ROOT, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(TMP_DIR, "captured_commands.jsonl")


class JarvisOrchestrator(QObject):
    def __init__(self):
        super().__init__()
        print("[J.A.R.V.I.S.] Booting Stark Industries Cognitive Core...")
        
        # 1. Initialize Subsystems (Layer 3 Tools)
        self.hud = JarvisHUDOverlay(on_submit=self.handle_command)
        self.voice = VoiceEngine()
        self.tts = TTSEngine()
        self.second_brain = SecondBrainEngine()
        self.sys_control = SystemControlEngine()
        
        # 2. Wire Signal Pipelines
        self._wire_signals()
        
        # 3. Global Hotkey Daemon ('Win + J')
        self.hotkey_daemon = HotkeyDaemon(
            hotkey="windows+j",
            on_trigger=self._on_hotkey_triggered
        )

    def _wire_signals(self):
        # Audio amplitude -> Arc Reactor waveform visualizer
        self.voice.amplitude_changed.connect(self.hud.set_amplitude)
        
        # Voice status changes -> HUD state pills & colors
        self.voice.status_changed.connect(self._on_voice_status_changed)
        
        # Voice transcription completed -> Route to command handler
        self.voice.transcription_ready.connect(self._on_voice_transcription)
        
        # TTS speaking states
        self.tts.speech_started.connect(lambda: self.hud.set_hud_state("speaking"))
        self.tts.speech_finished.connect(self._on_speech_finished)

    def _on_voice_status_changed(self, status: str):
        if status == "listening":
            self.hud.set_hud_state("listening", "Listening to your voice, sir...")
        elif status == "processing":
            self.hud.set_hud_state("processing", "Analyzing command and computing...")
        elif status == "idle" and not self.hud.is_visible_state:
            self.hud.set_hud_state("idle")

    def _on_hotkey_triggered(self):
        """Global Win + J trigger handler."""
        print("[J.A.R.V.I.S.] Global Hotkey (Win + J) engaged.")
        if self.hud.is_visible_state:
            self.voice.stop_listening()
            self.hud.hide_overlay()
        else:
            self.hud.show_overlay()
            self.voice.start_listening()

    def _on_voice_transcription(self, text: str):
        """Processes user voice transcription."""
        clean_text = text.strip()
        if not clean_text:
            self.hud.set_hud_state("listening", "I didn't quite catch that, sir. Standing by.")
            return

        print(f"[J.A.R.V.I.S.] User Spoke: '{clean_text}'")
        
        # Classify scope
        raw_lower = clean_text.lower()
        if any(w in raw_lower for w in ["note", "second brain", "vault", "challenge", "samay", "project"]):
            scope = "second_brain"
        elif any(w in raw_lower for w in ["volume", "mute", "unmute", "open", "launch", "run", "spotify", "chrome", "browser"]):
            scope = "system_control"
        else:
            scope = "general_query"

        cmd = CapturedCommand(
            trigger_source="win+j_voice",
            transcribed_text=clean_text,
            vad_confidence=0.99,
            target_scope=scope
        )
        self.handle_command(cmd)

    def handle_command(self, cmd: CapturedCommand) -> CommandExecutionResult:
        """Cognitive Intent Decision Matrix with J.A.R.V.I.S. Persona."""
        print(f"\n[J.A.R.V.I.S.] Processing Query ({cmd.target_scope}): '{cmd.transcribed_text}'")
        self.hud.set_hud_state("processing", f"Deciphering intent: \"{cmd.transcribed_text}\"...")

        raw = cmd.transcribed_text.lower()
        spoken_response = ""
        action_type = "tts_response"
        executed_command = None

        # ---------------- 1. System Controls & App Launching ----------------
        if cmd.target_scope == "system_control" or any(k in raw for k in ["volume", "mute", "open", "launch"]):
            if "volume up" in raw or "increase volume" in raw or "louder" in raw:
                spoken_response = self.sys_control.volume_up(5)
                action_type = "execute_system_command"
                executed_command = "volume_up"
            elif "volume down" in raw or "decrease volume" in raw or "lower volume" in raw or "quieter" in raw:
                spoken_response = self.sys_control.volume_down(5)
                action_type = "execute_system_command"
                executed_command = "volume_down"
            elif "mute" in raw or "unmute" in raw:
                spoken_response = self.sys_control.volume_mute()
                action_type = "execute_system_command"
                executed_command = "volume_mute"
            elif "vs code" in raw or "vscode" in raw or "code" in raw:
                spoken_response = self.sys_control.launch_app("code")
                action_type = "execute_system_command"
                executed_command = "launch_vscode"
            elif "terminal" in raw or "cmd" in raw or "command prompt" in raw:
                spoken_response = self.sys_control.launch_app("cmd")
                action_type = "execute_system_command"
                executed_command = "launch_cmd"
            elif "browser" in raw or "chrome" in raw or "google" in raw:
                spoken_response = self.sys_control.launch_app("chrome")
                action_type = "execute_system_command"
                executed_command = "launch_browser"
            elif "explorer" in raw or "files" in raw or "vault folder" in raw:
                spoken_response = self.sys_control.launch_app("explorer")
                action_type = "execute_system_command"
                executed_command = "launch_explorer"
            elif "open" in raw or "launch" in raw:
                app_target = raw.replace("open", "").replace("launch", "").replace("please", "").strip()
                spoken_response = self.sys_control.launch_app(app_target)
                action_type = "execute_system_command"
                executed_command = f"launch_{app_target}"

        # ---------------- 2. Second Brain Vault Interrogation ----------------
        elif cmd.target_scope == "second_brain" or any(k in raw for k in ["note", "second brain", "vault", "challenge", "samay"]):
            action_type = "search_vault"
            clean_query = raw.replace("search", "").replace("read", "").replace("find", "").replace("note", "").replace("second brain", "").replace("vault", "").replace("on", "").replace("about", "").replace("for", "").strip()
            if not clean_query:
                clean_query = "project"

            matches = self.second_brain.search_notes(clean_query, limit=3)
            if matches:
                top = matches[0]
                executed_command = f"read_note:{top['file_path']}"
                if "open" in raw:
                    self.sys_control.launch_app(f"code \"{top['file_path']}\"")
                    spoken_response = f"I have opened your note on '{top['title']}' in Visual Studio Code, sir."
                else:
                    snippet = top['snippet'].replace("#", "").strip()
                    spoken_response = f"I found '{top['title']}' in your vault, sir. Summary: {snippet}"
            else:
                spoken_response = f"I searched your Second Brain vault for '{clean_query}', but found no matching records, sir."

        # ---------------- 3. Conversational Persona & General Queries ----------------
        else:
            action_type = "tts_response"
            if any(g in raw for g in ["hello", "hi", "hey", "jarvis", "morning"]):
                spoken_response = "Good day, sir. All holographic and neural systems are operating at peak efficiency."
            elif any(s in raw for s in ["status", "system", "health", "diagnostics"]):
                spoken_response = "All subsystems online, sir. CPU telemetry normal, memory buffers cleared, and ready for your next directive."
            elif "who are you" in raw:
                spoken_response = "I am J.A.R.V.I.S., your autonomous desktop intelligence system. Always at your service, sir."
            else:
                spoken_response = f"Right away, sir. I have logged and acknowledged your query: '{cmd.transcribed_text}'."

        result = CommandExecutionResult(
            action_type=action_type,
            spoken_response=spoken_response,
            executed_command=executed_command,
            status="success"
        )

        # Log to .tmp/
        log_entry = {
            "timestamp": cmd.timestamp,
            "transcribed_text": cmd.transcribed_text,
            "spoken_response": spoken_response,
            "action_type": action_type
        }
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Update HUD to speaking / success state and stream voice output
        self.hud.set_hud_state("speaking", spoken_response)
        self.tts.speak(spoken_response)
        return result

    def _on_speech_finished(self):
        """Called when TTS voice finish speaking."""
        # Auto-dismiss overlay or return to listening after 2.5 seconds
        QTimer.singleShot(2500, self._auto_close_overlay)

    def _auto_close_overlay(self):
        if self.hud.is_visible_state:
            self.hud.hide_overlay()

    def start(self):
        print("[J.A.R.V.I.S.] Starting Global Hotkey Daemon ('Win + J')...")
        self.hotkey_daemon.start()
        print("\n========================================================")
        print("  J.A.R.V.I.S. FULL-SCREEN HOLOGRAPHIC HUD READY        ")
        print("  - Global Trigger: Press 'Win + J' anywhere in Windows ")
        print("  - Pure Voice-Driven UI with Sci-Fi Chimes & TTS       ")
        print("  - Dismiss: Press 'Esc'                                ")
        print("========================================================\n")


def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    orchestrator = JarvisOrchestrator()
    orchestrator.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
