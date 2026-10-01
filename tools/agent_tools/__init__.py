"""
J.A.R.V.I.S. Agent Tools Registry
Exports tool schemas and dispatch handlers for Hermes reasoning.
"""

from tools.agent_tools.vault_tools import search_vault, open_note, read_note
from tools.agent_tools.system_tools import adjust_volume, launch_application, get_system_telemetry

ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_vault",
            "description": "Searches the user's Second Brain markdown notes for queries or projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search term or project keyword to find in Second Brain"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_note",
            "description": "Opens a specific Second Brain markdown note in Visual Studio Code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "The title or filename of the note to open"}
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_volume",
            "description": "Adjusts system audio volume (up, down, or mute).",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["up", "down", "mute"], "description": "Volume action to perform"}
                },
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "launch_application",
            "description": "Launches a Windows application (VS Code, terminal/cmd, browser, explorer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to launch (e.g. 'code', 'cmd', 'chrome', 'explorer')"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_telemetry",
            "description": "Retrieves real-time CPU, RAM, and system performance metrics.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

TOOL_DISPATCH = {
    "search_vault": search_vault,
    "open_note": open_note,
    "read_note": read_note,
    "adjust_volume": adjust_volume,
    "launch_application": launch_application,
    "get_system_telemetry": get_system_telemetry
}
