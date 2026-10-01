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
    trigger_source: Literal["win+j", "voice_vad", "manual", "shortcut"] = Field(
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
    target_scope: Literal["second_brain", "app_launcher", "system_telemetry", "general_query"] = Field(
        default="general_query",
        description="Target routing scope for the command"
    )

class CommandExecutionResult(BaseModel):
    command_id: str
    action_type: Literal["read_note", "create_note", "search_notes", "launch_app", "telemetry", "text_response"] = "text_response"
    status: Literal["success", "executing", "failed", "cancelled"]
    response_text: str
    file_path_accessed: Optional[str] = None
    error: Optional[str] = None

class SystemTelemetryPayload(BaseModel):
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    net_sent_kbps: float
    net_recv_kbps: float
