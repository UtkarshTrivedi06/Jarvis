"""
Jarvis System Telemetry Provider
Gathers real-time CPU, RAM, and Network stats using psutil.
"""

import time
import psutil
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from tools.models import SystemTelemetryPayload

class TelemetryMonitor(QObject):
    telemetry_updated = pyqtSignal(object) # SystemTelemetryPayload

    def __init__(self, update_interval_ms: int = 1500, parent=None):
        super().__init__(parent)
        self.interval_ms = update_interval_ms
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_stats)

    def start(self):
        self.poll_stats()
        self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()

    def poll_stats(self):
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            
            # Net rate calculation
            now = time.time()
            dt = max(now - self._last_time, 0.001)
            net_now = psutil.net_io_counters()
            
            bytes_sent_sec = (net_now.bytes_sent - self._last_net.bytes_sent) / dt
            bytes_recv_sec = (net_now.bytes_recv - self._last_net.bytes_recv) / dt
            
            self._last_net = net_now
            self._last_time = now
            
            payload = SystemTelemetryPayload(
                cpu_percent=round(cpu_pct, 1),
                ram_percent=round(mem.percent, 1),
                ram_used_gb=round(mem.used / (1024**3), 1),
                ram_total_gb=round(mem.total / (1024**3), 1),
                net_sent_kbps=round(bytes_sent_sec / 1024.0, 1),
                net_recv_kbps=round(bytes_recv_sec / 1024.0, 1)
            )
            self.telemetry_updated.emit(payload)
        except Exception as e:
            print(f"[Telemetry] Error reading stats: {e}")
