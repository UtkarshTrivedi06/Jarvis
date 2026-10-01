"""
J.A.R.V.I.S. Adaptive Memory Client (Honcho Integration)
Connects to Honcho SDK / API for long-term user representation and session memory,
with automatic local persistent fallback.
"""

import os
import json
import threading
from typing import Optional, Dict, Any, List

TMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".tmp"))
os.makedirs(TMP_DIR, exist_ok=True)
LOCAL_MEMORY_FILE = os.path.join(TMP_DIR, "honcho_local_memory.json")

class HonchoMemoryClient:
    def __init__(self, user_id: str = "stark_01"):
        self.user_id = user_id
        self.api_key = os.environ.get("HONCHO_API_KEY", None)
        self.app_id = os.environ.get("HONCHO_APP_ID", "jarvis-desktop")
        self._honcho_sdk = None
        self._init_sdk()

    def _init_sdk(self):
        if self.api_key:
            try:
                import honcho
                self._honcho_sdk = honcho.Honcho(api_key=self.api_key)
                print(f"[Honcho] Initialized cloud client for user '{self.user_id}'.")
            except Exception as e:
                print(f"[Honcho] SDK notice: {e}. Utilizing persistent local memory engine.")
        else:
            print(f"[Honcho] No HONCHO_API_KEY detected. Utilizing persistent local memory engine.")

    def get_user_context(self) -> str:
        """Retrieves adaptive memory context for user query augmentation."""
        if self._honcho_sdk:
            try:
                # Query Honcho memory context
                user = self._honcho_sdk.users.get(self.user_id)
                representation = user.representation()
                if representation:
                    return str(representation)
            except Exception as e:
                print(f"[Honcho] Cloud context fetch fallback: {e}")

        # Local Persistent Memory Fallback
        return self._get_local_context()

    def save_session_turn(self, user_query: str, agent_response: str, executed_tools: Optional[List[str]] = None):
        """Asynchronously updates memory with the latest interaction."""
        threading.Thread(
            target=self._async_save,
            args=(user_query, agent_response, executed_tools or []),
            daemon=True
        ).start()

    def _async_save(self, user_query: str, agent_response: str, executed_tools: List[str]):
        # 1. Update cloud Honcho if available
        if self._honcho_sdk:
            try:
                session = self._honcho_sdk.sessions.get_or_create(session_id=f"{self.user_id}_session")
                session.messages.create(
                    messages=[
                        {"role": "user", "content": user_query},
                        {"role": "assistant", "content": agent_response}
                    ]
                )
            except Exception as e:
                print(f"[Honcho] Cloud save notice: {e}")

        # 2. Update local memory store
        try:
            data = self._load_local_data()
            if "history" not in data:
                data["history"] = []
            
            data["history"].append({
                "query": user_query,
                "response": agent_response,
                "tools": executed_tools
            })
            # Keep latest 30 turns
            data["history"] = data["history"][-30:]
            
            # Simple preference extraction heuristics
            if "prefer" in user_query.lower() or "always" in user_query.lower():
                if "preferences" not in data:
                    data["preferences"] = []
                data["preferences"].append(user_query)

            with open(LOCAL_MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Honcho] Local save error: {e}")

    def _load_local_data(self) -> Dict[str, Any]:
        if os.path.exists(LOCAL_MEMORY_FILE):
            try:
                with open(LOCAL_MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "user_id": self.user_id,
            "preferences": ["User prefers concise, sophisticated answers and direct tool execution."],
            "history": []
        }

    def _get_local_context(self) -> str:
        data = self._load_local_data()
        prefs = "; ".join(data.get("preferences", []))
        recent_history = data.get("history", [])[-3:]
        recent_queries = [f"'{h.get('query')}'" for h in recent_history if "query" in h]
        
        context_parts = []
        if prefs:
            context_parts.append(f"User Preferences: {prefs}")
        if recent_queries:
            context_parts.append(f"Recent Topics: {', '.join(recent_queries)}")
            
        return " | ".join(context_parts) if context_parts else "User working on Jarvis desktop assistant project."
