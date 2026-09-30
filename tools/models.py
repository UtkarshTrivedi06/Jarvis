"""
Jarvis B.L.A.S.T. Data Models
Strictly adhering to gemini.md Project Constitution schemas.
"""

from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, Field

class CapturedCommand(BaseModel):
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 timestamp when command was submitted"
    )
    trigger_source: Literal["win+j", "manual", "cli"] = Field(
        default="win+j",
        description="Source that triggered the input window"
    )
    raw_text: str = Field(
        ...,
        description="Captured speech or typed query"
    )
    clipboard_context: Optional[str] = Field(
        default=None,
        description="Optional system clipboard text captured at trigger time"
    )

class CommandExecutionResult(BaseModel):
    command_id: str
    status: Literal["success", "executing", "failed", "cancelled"]
    action_taken: Optional[str] = None
    response_text: str
    error: Optional[str] = None
