"""
Non-interactive / Spike Test for Jarvis Overlay and Pipeline
Validates payload generation, data validation, and JSON logging.
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
from tools.models import CapturedCommand, CommandExecutionResult
from main import JarvisOrchestrator, HISTORY_FILE

def test_pipeline():
    print("[-] Testing Command Pipeline with synthetic input...")
    # Clean test artifact
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        
    orchestrator = JarvisOrchestrator()
    
    test_cmd = CapturedCommand(
        trigger_source="win+j",
        raw_text="Summarize the latest meeting notes",
        clipboard_context="Meeting Notes: Discussed Q4 roadmap and deliverables."
    )
    
    result = orchestrator.handle_command(test_cmd)
    
    assert isinstance(result, CommandExecutionResult), "Result must be instance of CommandExecutionResult"
    assert result.status == "success", "Result status should be success"
    assert os.path.exists(HISTORY_FILE), "History file should be created"
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1, "Expected 1 logged command"
        logged_data = json.loads(lines[0])
        assert logged_data["raw_text"] == test_cmd.raw_text
        assert logged_data["clipboard_context"] == test_cmd.clipboard_context
        
    print(" [OK] Pipeline execution and payload logging verified.")
    print(">>> Phase 3: Architect Tests PASSED!")
    return 0

if __name__ == "__main__":
    sys.exit(test_pipeline())
