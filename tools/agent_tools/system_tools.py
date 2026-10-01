"""
System Automation Agent Tools for Hermes
"""

import psutil
from tools.system_controls import SystemControlEngine

_sys_control = SystemControlEngine()

def adjust_volume(direction: str) -> str:
    """Adjusts volume up, down, or mute."""
    d = direction.lower()
    if "up" in d:
        return _sys_control.volume_up(5)
    elif "down" in d:
        return _sys_control.volume_down(5)
    elif "mute" in d:
        return _sys_control.volume_mute()
    return _sys_control.volume_up(3)

def launch_application(app_name: str) -> str:
    """Launches target application."""
    return _sys_control.launch_app(app_name)

def get_system_telemetry() -> str:
    """Returns CPU, RAM, and memory stats."""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return f"CPU usage is at {cpu}%, RAM utilization is {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)."
