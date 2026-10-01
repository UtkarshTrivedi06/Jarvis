"""
Second Brain Vault Agent Tools for Hermes
"""

import os
from tools.second_brain import SecondBrainEngine
from tools.system_controls import SystemControlEngine

_vault_engine = SecondBrainEngine()
_sys_control = SystemControlEngine()

def search_vault(query: str) -> str:
    """Searches markdown notes in Second Brain."""
    matches = _vault_engine.search_notes(query, limit=3)
    if matches:
        top = matches[0]
        snippet = top['snippet'].replace("#", "").strip()
        return f"Found note '{top['title']}' ({top['file_name']}). Summary: {snippet}"
    return f"No markdown notes found in Second Brain matching '{query}'."

def open_note(target: str) -> str:
    """Opens a markdown note in Visual Studio Code."""
    matches = _vault_engine.search_notes(target, limit=1)
    if matches:
        top = matches[0]
        _sys_control.launch_app(f"code \"{top['file_path']}\"")
        return f"Opened note '{top['title']}' in Visual Studio Code."
    return f"Unable to locate note matching '{target}' in vault."

def read_note(target: str) -> str:
    """Reads full content of a note."""
    content = _vault_engine.read_note(target)
    if content:
        return content[:400]
    return f"Note '{target}' not found."
