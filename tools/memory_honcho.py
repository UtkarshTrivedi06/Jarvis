"""
J.A.R.V.I.S. Adaptive Memory Client (Honcho Integration)
Connects to Honcho SDK (honcho-ai v2.5+) for long-term user representation and session memory,
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
        self.workspace_id = os.environ.get("HONCHO_WORKSPACE_ID", "jarvis_workspace")
        self._honcho_sdk = None
        self._init_sdk()

    def _init_sdk(self):
        if self.api_key:
            try:
                from honcho import Honcho
                self._honcho_sdk = Honcho(
                    api_key=self.api_key,
                    workspace_id=self.workspace_id
                )
                print(f"[Honcho] Initialized cloud client for workspace '{self.workspace_id}' (User: '{self.user_id}').")
            except Exception as e:
                print(f"[Honcho] SDK notice: {e}. Utilizing persistent local memory engine.")
        else:
            print(f"[Honcho] No HONCHO_API_KEY detected. Utilizing persistent local memory engine.")

    def get_user_context(self) -> str:
        """Retrieves adaptive memory context for user query augmentation."""
        if self._honcho_sdk:
            try:
                # Query Honcho conclusions/context
                conclusions = self._honcho_sdk.conclusions.get(session_id=f"{self.user_id}_session")
                if conclusions:
                    return str(conclusions)
            except Exception as e:
                # Fallback to local
                pass

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
        # 1. Update cloud Honcho if SDK and API key are configured
        if self._honcho_sdk:
            try:
                session_id = f"{self.user_id}_session"
                self._honcho_sdk.sessions.get_or_create(session_id=session_id)
                # Record user query and assistant response messages
                self._honcho_sdk.messages.create(
                    session_id=session_id,
                    peer_id=self.user_id,
                    content=user_query
                )
                self._honcho_sdk.messages.create(
                    session_id=session_id,
                    peer_id="jarvis_assistant",
                    content=agent_response
                )
            except Exception as e:
                print(f"[Honcho] Cloud save notice: {e}")

        # 2. Update local persistent memory store
        try:
            data = self._load_local_data()
            if "history" not in data:
                data["history"] = []
            
            data["history"].append({
                "query": user_query,
                "response": agent_response,
                "tools": executed_tools
            })
            # Retain last 30 turns
            data["history"] = data["history"][-30:]
            
            # Simple adaptive preference extraction
            q_lower = user_query.lower()
            if "prefer" in q_lower or "always" in q_lower or "i like" in q_lower:
                if "preferences" not in data:
                    data["preferences"] = []
                if user_query not in data["preferences"]:
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
