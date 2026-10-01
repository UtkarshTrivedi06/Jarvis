"""
Automated Comprehensive Test Suite for J.A.R.V.I.S. (Hermes + Honcho Integration)
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from tools.models import CapturedCommand, CommandExecutionResult
from tools.memory_honcho import HonchoMemoryClient
from tools.hermes_agent import HermesAgent
from tools.agent_tools import ALL_TOOLS, TOOL_DISPATCH
from tools.audio_sfx import generate_sci_fi_chimes, WAKE_WAV, DISMISS_WAV
from tools.hud_overlay import JarvisHUDOverlay
from main import JarvisOrchestrator

class TestJarvisAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_01_models_validation(self):
        """Test Pydantic input and output payload models for Hermes and Honcho."""
        cmd = CapturedCommand(
            trigger_source="win+j_voice",
            transcribed_text="Search note for SAMAY",
            honcho_user_id="stark_01",
            honcho_context="User prefers concise responses",
            agent_model="hermes3"
        )
        self.assertEqual(cmd.honcho_user_id, "stark_01")
        self.assertEqual(cmd.agent_model, "hermes3")

        res = CommandExecutionResult(
            action_type="agent_execution",
            spoken_response="At your service, sir.",
            executed_tools=["search_vault"],
            memory_updated=True,
            status="success"
        )
        self.assertEqual(res.status, "success")
        self.assertIn("search_vault", res.executed_tools)

    def test_02_honcho_memory_client(self):
        """Test Honcho memory client retrieval and async saving."""
        memory = HonchoMemoryClient(user_id="test_user")
        ctx = memory.get_user_context()
        self.assertIsInstance(ctx, str)
        memory.save_session_turn("Test query", "Test response", ["search_vault"])
        print(f"  [Test] Honcho memory context retrieved: {ctx[:60]}...")

    def test_03_agent_tools_registry(self):
        """Test agent tools execution."""
        self.assertGreaterEqual(len(ALL_TOOLS), 4)
        
        # Test vault tool
        res_vault = TOOL_DISPATCH["search_vault"](query="project")
        self.assertIsInstance(res_vault, str)
        
        # Test volume tool
        res_vol = TOOL_DISPATCH["adjust_volume"](direction="up")
        self.assertIn("audio volume", res_vol)
        print(f"  [Test] Agent tools validated. Volume: {res_vol}")

    def test_04_hermes_agent_reasoning(self):
        """Test Hermes agent reasoning and tool resolution."""
        agent = HermesAgent()
        response, tools = agent.process_query("Search note for SAMAY", "User prefers fast results")
        self.assertIsInstance(response, str)
        self.assertIn("search_vault", tools)
        print(f"  [Test] Hermes executed tools: {tools}")

    def test_05_orchestrator_routing(self):
        """Test full orchestrator turn."""
        orchestrator = JarvisOrchestrator()
        cmd = CapturedCommand(
            trigger_source="win+j_voice",
            transcribed_text="Search note for SAMAY",
            honcho_user_id="stark_01"
        )
        res = orchestrator.handle_command(cmd)
        self.assertEqual(res.status, "success")
        self.assertTrue(res.memory_updated)
        clean_spoken = res.spoken_response.encode('ascii', errors='ignore').decode()
        print(f"  [Test] Full turn completed with response: '{clean_spoken[:70]}...'")


if __name__ == "__main__":
    unittest.main()
