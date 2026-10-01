"""
J.A.R.V.I.S. Autonomous Desktop Assistant — Layer 2 Orchestration
Connects Full-Screen Holographic HUD, Direct Voice Engine, Honcho Adaptive Memory,
Hermes 3 Agent Tool Router, and Local SAPI TTS Voice Output.
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
from tools.tts_engine import TTSEngine
from tools.memory_honcho import HonchoMemoryClient
from tools.hermes_agent import HermesAgent
from tools.hotkey_daemon import HotkeyDaemon

TMP_DIR = os.path.join(PROJECT_ROOT, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(TMP_DIR, "captured_commands.jsonl")


class JarvisOrchestrator(QObject):
    def __init__(self):
        super().__init__()
        print("[J.A.R.V.I.S.] Booting Stark Industries Cognitive Core (Hermes + Honcho)...")
        
        # 1. Initialize Subsystems (Layer 3 Tools)
        self.hud = JarvisHUDOverlay(on_submit=self.handle_command)
        self.voice = VoiceEngine()
        self.tts = TTSEngine()
        self.memory = HonchoMemoryClient(user_id="stark_01")
        self.agent = HermesAgent()
        
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
            self.hud.set_hud_state("processing", "Hermes agent reasoning & tool execution...")
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
        """Processes user voice transcription with Honcho memory context."""
        clean_text = text.strip()
        if not clean_text:
            self.hud.set_hud_state("listening", "I didn't quite catch that, sir. Standing by.")
            return

        print(f"[J.A.R.V.I.S.] User Spoke: '{clean_text}'")
        
        # Pull adaptive user memory context from Honcho
        honcho_ctx = self.memory.get_user_context()

        cmd = CapturedCommand(
            trigger_source="win+j_voice",
            transcribed_text=clean_text,
            honcho_user_id="stark_01",
            honcho_context=honcho_ctx,
            agent_model="hermes3"
        )
        self.handle_command(cmd)

    def handle_command(self, cmd: CapturedCommand) -> CommandExecutionResult:
        """Hermes Agent Cognitive Routing & Tool Execution."""
        print(f"\n[J.A.R.V.I.S.] Routing to Hermes: '{cmd.transcribed_text}'")
        self.hud.set_hud_state("processing", f"Hermes processing: \"{cmd.transcribed_text}\"...")

        # Process turn through Hermes agent
        spoken_response, executed_tools = self.agent.process_query(
            user_query=cmd.transcribed_text,
            honcho_context=cmd.honcho_context or ""
        )

        # Asynchronously update Honcho memory
        self.memory.save_session_turn(
            user_query=cmd.transcribed_text,
            agent_response=spoken_response,
            executed_tools=executed_tools
        )

        result = CommandExecutionResult(
            action_type="agent_execution",
            spoken_response=spoken_response,
            executed_tools=executed_tools,
            memory_updated=True,
            status="success"
        )

        # Log payload to .tmp/
        log_entry = {
            "timestamp": cmd.timestamp,
            "transcribed_text": cmd.transcribed_text,
            "spoken_response": spoken_response,
            "executed_tools": executed_tools
        }
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Update HUD state and stream voice output
        self.hud.set_hud_state("speaking", spoken_response)
        self.tts.speak(spoken_response)
        return result

    def _on_speech_finished(self):
        """Called when TTS voice finishes speaking."""
        QTimer.singleShot(2500, self._auto_close_overlay)

    def _auto_close_overlay(self):
        if self.hud.is_visible_state:
            self.hud.hide_overlay()

    def start(self):
        print("[J.A.R.V.I.S.] Starting Global Hotkey Daemon ('Win + J')...")
        self.hotkey_daemon.start()
        print("\n========================================================")
        print("  J.A.R.V.I.S. (HERMES + HONCHO MEMORY) IS ONLINE       ")
        print("  - Global Trigger: Press 'Win + J' anywhere in Windows ")
        print("  - Adaptive Long-Term Memory via Honcho                ")
        print("  - Nous Hermes 3 Tool Execution Agent Loop             ")
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
