"""
J.A.R.V.I.S. B.L.A.S.T. Data Models (Hermes + Honcho Integration)
Strictly conforming to task-spec.md and gemini.md schemas.
"""

from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class CapturedCommand(BaseModel):
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 timestamp when command was submitted"
    )
    transcribed_text: str = Field(
        ...,
        description="Transcribed spoken user command"
    )
    honcho_user_id: str = Field(
        default="stark_01",
        description="Honcho user representation ID"
    )
    honcho_context: Optional[str] = Field(
        default=None,
        description="Dynamic user memory context retrieved from Honcho"
    )
    agent_model: str = Field(
        default="hermes3",
        description="Agent reasoning model"
    )

class CommandExecutionResult(BaseModel):
    action_type: Literal["agent_execution", "tts_response", "execute_system_command", "search_vault"] = "agent_execution"
    spoken_response: str
    executed_tools: List[str] = Field(
        default_factory=list,
        description="List of tools executed during agent resolution"
    )
    memory_updated: bool = Field(
        default=True,
        description="Whether memory was updated in Honcho"
    )
    status: Literal["success", "error"] = "success"
