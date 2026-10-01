"""
J.A.R.V.I.S. Hermes 3 Agent Router
Runs the Nous Hermes reasoning loop via Ollama/OpenAI-compatible endpoints
with tool execution and instant deterministic fallback.
"""

import os
import json
import requests
from typing import Dict, Any, List, Tuple
from tools.agent_tools import ALL_TOOLS, TOOL_DISPATCH

OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434/api/chat")
HERMES_MODEL = os.environ.get("HERMES_MODEL", "hermes3")

SYSTEM_PROMPT_TEMPLATE = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the sophisticated, witty, and polite AI assistant from Iron Man.
Always address the user as 'sir' and maintain a calm, highly capable demeanor.

[ADAPTIVE USER MEMORY FROM HONCHO]:
{honcho_context}

Respond concisely and execute appropriate tools directly when requested.
"""

class HermesAgent:
    def __init__(self, endpoint: str = OLLAMA_ENDPOINT, model: str = HERMES_MODEL):
        self.endpoint = endpoint
        self.model = model

    def process_query(self, user_query: str, honcho_context: str = "") -> Tuple[str, List[str]]:
        """
        Executes Hermes reasoning turn:
        Returns (spoken_dialogue_response, list_of_executed_tools).
        """
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            honcho_context=honcho_context or "User is working on the J.A.R.V.I.S. system."
        )
        
        executed_tools = []
        
        # 1. Attempt Ollama Hermes Function Calling
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "tools": ALL_TOOLS,
                "stream": False
            }
            resp = requests.post(self.endpoint, json=payload, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("message", {})
                
                # Check for tool calls
                tool_calls = msg.get("tool_calls", [])
                if tool_calls:
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        fn_name = fn.get("name")
                        fn_args = fn.get("arguments", {})
                        if isinstance(fn_args, str):
                            try:
                                fn_args = json.loads(fn_args)
                            except Exception:
                                fn_args = {}
                                
                        if fn_name in TOOL_DISPATCH:
                            tool_res = TOOL_DISPATCH[fn_name](**fn_args)
                            executed_tools.append(fn_name)
                            return f"{tool_res}", executed_tools
                            
                content = msg.get("content", "").strip()
                if content:
                    return content, executed_tools
        except Exception as e:
            # Fallback seamlessly to local deterministic resolver
            pass

        # 2. Deterministic Tool Fallback (Zero-latency when Ollama is offline)
        return self._deterministic_fallback(user_query)

    def _deterministic_fallback(self, query: str) -> Tuple[str, List[str]]:
        """Handles intents deterministically if LLM server is unreachable."""
        q = query.lower()
        executed_tools = []

        # Vault search / notes
        if any(w in q for w in ["note", "second brain", "vault", "challenge", "samay", "project"]):
            if "open" in q:
                res = TOOL_DISPATCH["open_note"](target=q.replace("open", "").replace("note", "").strip())
                executed_tools.append("open_note")
                return f"{res}", executed_tools
            else:
                clean_term = q.replace("search", "").replace("find", "").replace("note", "").replace("vault", "").strip() or "project"
                res = TOOL_DISPATCH["search_vault"](query=clean_term)
                executed_tools.append("search_vault")
                return f"I found this in your vault, sir. {res}", executed_tools

        # System volume
        if "volume up" in q or "louder" in q or "increase volume" in q:
            res = TOOL_DISPATCH["adjust_volume"](direction="up")
            executed_tools.append("adjust_volume")
            return f"{res}", executed_tools
        elif "volume down" in q or "quieter" in q or "lower volume" in q:
            res = TOOL_DISPATCH["adjust_volume"](direction="down")
            executed_tools.append("adjust_volume")
            return f"{res}", executed_tools
        elif "mute" in q or "unmute" in q:
            res = TOOL_DISPATCH["adjust_volume"](direction="mute")
            executed_tools.append("adjust_volume")
            return f"{res}", executed_tools

        # App launcher
        if "vs code" in q or "vscode" in q or "code" in q:
            res = TOOL_DISPATCH["launch_application"](app_name="code")
            executed_tools.append("launch_application")
            return f"{res}", executed_tools
        elif "terminal" in q or "cmd" in q:
            res = TOOL_DISPATCH["launch_application"](app_name="cmd")
            executed_tools.append("launch_application")
            return f"{res}", executed_tools
        elif "browser" in q or "chrome" in q:
            res = TOOL_DISPATCH["launch_application"](app_name="chrome")
            executed_tools.append("launch_application")
            return f"{res}", executed_tools
        elif "explorer" in q or "folder" in q:
            res = TOOL_DISPATCH["launch_application"](app_name="explorer")
            executed_tools.append("launch_application")
            return f"{res}", executed_tools

        # Telemetry
        if any(w in q for w in ["stat", "cpu", "ram", "diagnostics", "health"]):
            res = TOOL_DISPATCH["get_system_telemetry"]()
            executed_tools.append("get_system_telemetry")
            return f"Telemetry diagnostic complete, sir. {res}", executed_tools

        # Conversational Persona
        if any(w in q for w in ["hello", "hi", "hey", "jarvis"]):
            return "Good day, sir. All holographic and neural systems are operating at peak efficiency.", []
        if "who are you" in q:
            return "I am J.A.R.V.I.S., your autonomous desktop intelligence system. Always at your service, sir.", []

        return f"Right away, sir. I have processed and logged your request: '{query}'.", []
