"""
Automated Comprehensive Test Suite for J.A.R.V.I.S. Desktop Assistant
Validates Models, Audio SFX, Second Brain, System Controls, Full-Screen HUD, and Orchestrator.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from tools.models import CapturedCommand, CommandExecutionResult
from tools.second_brain import SecondBrainEngine
from tools.system_controls import SystemControlEngine
from tools.audio_sfx import generate_sci_fi_chimes, WAKE_WAV, DISMISS_WAV
from tools.hud_overlay import JarvisHUDOverlay, GiantArcReactorWidget
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
            trigger_source="win+j_voice",
            transcribed_text="Search note for SAMAY",
            vad_confidence=0.99,
            target_scope="second_brain"
        )
        self.assertEqual(cmd.trigger_source, "win+j_voice")
        self.assertEqual(cmd.target_scope, "second_brain")

        res = CommandExecutionResult(
            action_type="tts_response",
            spoken_response="At your service, sir.",
            status="success"
        )
        self.assertEqual(res.status, "success")
        self.assertEqual(res.action_type, "tts_response")

    def test_02_audio_sfx_synthesis(self):
        """Test procedural sound chimes generation."""
        generate_sci_fi_chimes()
        self.assertTrue(os.path.exists(WAKE_WAV))
        self.assertTrue(os.path.exists(DISMISS_WAV))
        print("  [Test] Sci-Fi audio chimes generated and validated.")

    def test_03_system_controls(self):
        """Test system control routines."""
        sc = SystemControlEngine()
        msg_up = sc.volume_up(1)
        self.assertIn("audio volume", msg_up)
        print(f"  [Test] System control message: {msg_up}")

    def test_04_hud_widgets_and_giant_reactor(self):
        """Test full-screen HUD and Giant Arc Reactor state transitions."""
        hud = JarvisHUDOverlay()
        self.assertIsNotNone(hud.arc_reactor)
        
        # Test states
        hud.set_hud_state("listening", "Listening test")
        self.assertEqual(hud.arc_reactor.state, "listening")
        
        hud.set_hud_state("processing", "Computing test")
        self.assertEqual(hud.arc_reactor.state, "processing")
        
        hud.set_hud_state("speaking", "Speaking test")
        self.assertEqual(hud.arc_reactor.state, "speaking")
        
        # Test audio amplitude setting
        hud.set_amplitude(0.85)
        self.assertEqual(hud.arc_reactor.target_amplitude, 0.85)
        print("  [Test] Full-Screen HUD & Giant Arc Reactor animations validated.")

    def test_05_orchestrator_routing(self):
        """Test Layer 2 orchestrator command handling with J.A.R.V.I.S. persona."""
        orchestrator = JarvisOrchestrator()
        
        # Test Second Brain query
        cmd_sb = CapturedCommand(
            trigger_source="win+j_voice",
            transcribed_text="Search note for SAMAY",
            target_scope="second_brain"
        )
        res_sb = orchestrator.handle_command(cmd_sb)
        self.assertEqual(res_sb.status, "success")
        self.assertIn("sir", res_sb.spoken_response)
        clean_spoken = res_sb.spoken_response.encode('ascii', errors='ignore').decode()
        print(f"  [Test] Orchestrator executed query with J.A.R.V.I.S. persona: '{clean_spoken}'")


if __name__ == "__main__":
    unittest.main()
