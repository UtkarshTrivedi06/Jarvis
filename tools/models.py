"""
J.A.R.V.I.S. B.L.A.S.T. Data Models
Strictly conforming to task-spec.md and gemini.md schemas.
"""

from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, Field

class CapturedCommand(BaseModel):
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 timestamp when command was submitted"
    )
    trigger_source: str = Field(
        default="win+j_voice",
        description="Source that triggered the input window"
    )
    transcribed_text: str = Field(
        ...,
        description="Transcribed spoken user command"
    )
    vad_confidence: float = Field(
        default=0.99,
        description="VAD confidence score"
    )
    target_scope: Literal["second_brain", "system_control", "general_query"] = Field(
        default="general_query",
        description="Target routing scope for the command"
    )

class CommandExecutionResult(BaseModel):
    action_type: Literal["tts_response", "execute_system_command", "search_vault"] = "tts_response"
    spoken_response: str
    executed_command: Optional[str] = None
    status: Literal["success", "error"] = "success"
