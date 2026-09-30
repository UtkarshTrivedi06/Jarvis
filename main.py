"""
Jarvis Desktop Assistant — Layer 2 Navigation / Orchestration
Connects Hotkey Daemon, CustomTkinter Overlay UI, and Command Execution Pipeline.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import uuid
from datetime import datetime, timezone
from tools.models import CapturedCommand, CommandExecutionResult
from tools.overlay_window import JarvisOverlay
from tools.hotkey_daemon import HotkeyDaemon

TMP_DIR = os.path.join(os.path.dirname(__file__), ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(TMP_DIR, "captured_commands.jsonl")

class JarvisOrchestrator:
    def __init__(self):
        print("[Jarvis] Initializing Core Orchestration Layer...")
        self.ui = JarvisOverlay(on_submit=self.handle_command)
        
        # Hotkey daemon triggers UI show via thread-safe root.after
        self.hotkey_daemon = HotkeyDaemon(
            hotkey="windows+j",
            on_trigger=self._on_hotkey_pressed
        )

    def _on_hotkey_pressed(self):
        """Dispatched from background listener thread to Tkinter main thread."""
        self.ui.after(0, self.ui.toggle)

    def handle_command(self, cmd: CapturedCommand) -> CommandExecutionResult:
        """Processes submitted user command and produces CommandExecutionResult."""
        cmd_id = str(uuid.uuid4())
        print(f"\n[Jarvis] Captured Command [{cmd_id}]: '{cmd.raw_text}'")
        if cmd.clipboard_context:
            print(f"         Context: {cmd.clipboard_context[:60]}...")
            
        # Log to local history in .tmp/
        log_entry = {
            "id": cmd_id,
            "timestamp": cmd.timestamp,
            "trigger_source": cmd.trigger_source,
            "raw_text": cmd.raw_text,
            "clipboard_context": cmd.clipboard_context
        }
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Deterministic result generation conforming to gemini.md schema
        result = CommandExecutionResult(
            command_id=cmd_id,
            status="success",
            action_taken="Command logged and routed to processing pipeline",
            response_text=f"Processed query: {cmd.raw_text}"
        )
        return result

    def start(self):
        print("[Jarvis] Starting Global Hotkey Daemon ('Win + J')...")
        self.hotkey_daemon.start()
        print("[Jarvis] Jarvis Desktop Assistant is READY and running in background.")
        print("         Press Win + J anywhere to invoke overlay.")
        print("         Press Esc to dismiss.")
        
        try:
            self.ui.mainloop()
        finally:
            self.hotkey_daemon.stop()
            print("[Jarvis] Daemon stopped cleanly.")

def main():
    app = JarvisOrchestrator()
    app.start()

if __name__ == "__main__":
    main()
