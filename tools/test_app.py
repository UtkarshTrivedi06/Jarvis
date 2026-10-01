"""
Automated Comprehensive Test Suite for Jarvis Desktop Assistant
Validates Models, Second Brain Engine, Telemetry, HUD Overlay, and Orchestrator.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from tools.models import CapturedCommand, CommandExecutionResult, SystemTelemetryPayload
from tools.second_brain import SecondBrainEngine
from tools.system_telemetry import TelemetryMonitor
from tools.app_launcher import AppLauncher
from tools.hud_overlay import JarvisHUDOverlay, ArcReactorWidget
from main import JarvisOrchestrator

class TestJarvisAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_01_models_validation(self):
        """Test Pydantic input and output payload models."""
        cmd = CapturedCommand(
            trigger_source="win+j",
            raw_text="Search note for SAMAY challenge",
            clipboard_context="https://example.com",
            target_scope="second_brain"
        )
        self.assertEqual(cmd.trigger_source, "win+j")
        self.assertEqual(cmd.target_scope, "second_brain")

        res = CommandExecutionResult(
            command_id="test-123",
            action_type="read_note",
            status="success",
            response_text="Found note",
            file_path_accessed="d:/_Second Brain/note.md"
        )
        self.assertEqual(res.status, "success")
        self.assertEqual(res.action_type, "read_note")

    def test_02_second_brain_search(self):
        """Test markdown note searching."""
        sb = SecondBrainEngine()
        results = sb.search_notes("project", limit=3)
        self.assertIsInstance(results, list)
        print(f"  [Test] Second Brain search for 'project' returned {len(results)} matches.")

    def test_03_telemetry_polling(self):
        """Test psutil metrics calculation."""
        monitor = TelemetryMonitor()
        received_payload = []
        monitor.telemetry_updated.connect(lambda p: received_payload.append(p))
        monitor.poll_stats()
        
        self.assertEqual(len(received_payload), 1)
        p = received_payload[0]
        self.assertGreaterEqual(p.cpu_percent, 0.0)
        self.assertGreater(p.ram_total_gb, 0.0)
        print(f"  [Test] Telemetry: CPU={p.cpu_percent}%, RAM={p.ram_used_gb}/{p.ram_total_gb}GB")

    def test_04_hud_widgets_and_reactor(self):
        """Test HUD components and Arc Reactor states."""
        hud = JarvisHUDOverlay()
        self.assertIsNotNone(hud.arc_reactor)
        
        # Test states
        hud.set_hud_state("listening", "Listening test")
        self.assertEqual(hud.arc_reactor.state, "listening")
        
        hud.set_hud_state("processing", "Thinking test")
        self.assertEqual(hud.arc_reactor.state, "processing")
        
        hud.set_hud_state("success", "Success test")
        self.assertEqual(hud.arc_reactor.state, "success")
        
        # Test audio amplitude setting
        hud.set_amplitude(0.75)
        self.assertEqual(hud.arc_reactor.target_amplitude, 0.75)
        print("  [Test] HUD & Arc Reactor animations validated.")

    def test_05_orchestrator_routing(self):
        """Test Layer 2 orchestrator command handling."""
        orchestrator = JarvisOrchestrator()
        
        # Test Second Brain command
        cmd_sb = CapturedCommand(
            trigger_source="manual",
            raw_text="Search note for SAMAY",
            target_scope="second_brain"
        )
        res_sb = orchestrator.handle_command(cmd_sb)
        self.assertEqual(res_sb.status, "success")
        self.assertIn(res_sb.action_type, ["read_note", "text_response"])
        print(f"  [Test] Orchestrator executed Second Brain query: {res_sb.response_text[:60]}...")

        # Test Telemetry command
        cmd_tel = CapturedCommand(
            trigger_source="manual",
            raw_text="Show system cpu and ram",
            target_scope="system_telemetry"
        )
        res_tel = orchestrator.handle_command(cmd_tel)
        self.assertEqual(res_tel.status, "success")
        self.assertEqual(res_tel.action_type, "telemetry")
        print(f"  [Test] Orchestrator executed Telemetry query: {res_tel.response_text[:60]}...")


if __name__ == "__main__":
    unittest.main()
