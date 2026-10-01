"""
Jarvis Cyberpunk Tactical HUD Overlay (PyQt6)
Implements:
- Glassmorphic dark slate window with cyan/neon glowing borders
- Central Arc Reactor custom vector widget (3 rotating tracks + live audio reactive bars)
- Left Telemetry Flank (CPU, RAM, Network)
- Right Quick Tools Flank (CMD, VS Code, Second Brain)
- Interactive Command Input Field
- Console Output Stream with Typewriter Animation & Status Badges
- Scale & Opacity Wake/Dismiss animations
"""

import sys
import os
import math
import ctypes
from typing import Callable, Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRectF, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, 
    QLinearGradient, QPainterPath, QKeySequence, QShortcut
)
import pyperclip

from tools.models import CapturedCommand, SystemTelemetryPayload
from tools.win_keys import force_foreground_window


class ArcReactorWidget(QWidget):
    """
    High-Tech Arc Reactor Vector HUD Component:
    - Inner Glowing Energy Core
    - Middle Rotating Segmented Tick Ring (Accelerates on thinking)
    - Outer Audio-Reactive Radial Waveform Equalizer Bars
    - Orbiting Quantum Particles
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)
        
        self.angle_middle = 0.0
        self.angle_particles = 0.0
        self.rotation_speed = 1.2 # RPM idle
        self.amplitude = 0.0      # Current audio level (0.0 to 1.0)
        self.target_amplitude = 0.0
        self.state = "idle"       # "idle", "listening", "processing", "success"
        self.pulse_phase = 0.0

        # Animation timer ~60 FPS
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(16)

    def set_amplitude(self, amp: float):
        self.target_amplitude = max(0.0, min(amp, 1.0))

    def set_state(self, state: str):
        self.state = state
        if state == "processing":
            self.rotation_speed = 6.0 # Accelerated 60 RPM
        elif state == "listening":
            self.rotation_speed = 2.0
        else:
            self.rotation_speed = 1.2
        self.update()

    def _update_animation(self):
        # Smooth rotation
        self.angle_middle = (self.angle_middle + self.rotation_speed) % 360.0
        self.angle_particles = (self.angle_particles - self.rotation_speed * 1.8) % 360.0
        self.pulse_phase = (self.pulse_phase + 0.05) % (math.pi * 2)

        # Smooth audio amplitude lerp
        self.amplitude += (self.target_amplitude - self.amplitude) * 0.35
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        
        # Color mapping based on HUD state
        if self.state == "listening":
            glow_color = QColor(59, 130, 246)  # Electric Blue #3B82F6
            accent_color = QColor(0, 240, 255) # Cyan
        elif self.state == "processing":
            glow_color = QColor(245, 158, 11)  # Amber #F59E0B
            accent_color = QColor(251, 191, 36)
        elif self.state == "success":
            glow_color = QColor(16, 185, 129)  # Emerald #10B981
            accent_color = QColor(52, 211, 153)
        else:
            glow_color = QColor(0, 240, 255)   # Default Cyan #00F0FF
            accent_color = QColor(59, 130, 246)

        # 1. Outer Radial Audio Waveform Equalizer (16 bars)
        num_bars = 16
        base_radius = 32.0
        max_bar_length = 11.0
        for i in range(num_bars):
            theta = (i * (360.0 / num_bars)) * (math.pi / 180.0)
            # Modulate bar height with amplitude and subtle idle vibration
            idle_noise = math.sin(self.pulse_phase * 2.0 + i) * 0.15
            bar_scale = max(0.15, self.amplitude + idle_noise)
            bar_len = bar_scale * max_bar_length
            
            r_start = base_radius
            r_end = base_radius + bar_len
            
            x1 = center_x + r_start * math.cos(theta)
            y1 = center_y + r_start * math.sin(theta)
            x2 = center_x + r_end * math.cos(theta)
            y2 = center_y + r_end * math.sin(theta)
            
            bar_alpha = int(140 + 115 * min(bar_scale, 1.0))
            bar_pen = QPen(QColor(accent_color.red(), accent_color.green(), accent_color.blue(), bar_alpha), 2.2)
            bar_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(bar_pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # 2. Middle Rotating Segmented Tick Ring (12 Segments)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_middle)
        
        mid_radius = 24.0
        num_ticks = 12
        for j in range(num_ticks):
            deg = j * (360.0 / num_ticks)
            rad = deg * (math.pi / 180.0)
            tx1 = (mid_radius - 2.5) * math.cos(rad)
            ty1 = (mid_radius - 2.5) * math.sin(rad)
            tx2 = (mid_radius + 2.5) * math.cos(rad)
            ty2 = (mid_radius + 2.5) * math.sin(rad)
            
            tick_pen = QPen(QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 180), 1.5)
            painter.setPen(tick_pen)
            painter.drawLine(int(tx1), int(ty1), int(tx2), int(ty2))
            
        # Draw thin track ring
        painter.setPen(QPen(QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 80), 1.0, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-mid_radius, -mid_radius, mid_radius * 2, mid_radius * 2))
        painter.restore()

        # 3. Inner Core Reactor with Pulse & Radial Glow
        pulse_scale = 1.0 + 0.08 * math.sin(self.pulse_phase)
        core_radius = 14.0 * pulse_scale
        
        # Radial gradient for deep energy bloom
        grad = QRadialGradient(center_x, center_y, core_radius * 1.6)
        grad.setColorAt(0.0, QColor(255, 255, 255, 230))
        grad.setColorAt(0.4, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 200))
        grad.setColorAt(0.8, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 60))
        grad.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QRectF(center_x - core_radius * 1.5, center_y - core_radius * 1.5, core_radius * 3.0, core_radius * 3.0))
        
        # Inner core solid center
        painter.setPen(QPen(QColor(255, 255, 255, 240), 1.2))
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(QRectF(center_x - core_radius * 0.6, center_y - core_radius * 0.6, core_radius * 1.2, core_radius * 1.2))

        # 4. Orbiting Quantum Particle Dots (State == processing)
        if self.state == "processing":
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(self.angle_particles)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
            for p_idx in range(3):
                p_rad = (p_idx * 120.0) * (math.pi / 180.0)
                px = (base_radius + 4.0) * math.cos(p_rad)
                py = (base_radius + 4.0) * math.sin(p_rad)
                painter.drawEllipse(QRectF(px - 2, py - 2, 4, 4))
            painter.restore()


class JarvisHUDOverlay(QWidget):
    """
    Main Tactical HUD Floating Overlay Window.
    """
    command_submitted = pyqtSignal(object) # CapturedCommand
    shortcut_triggered = pyqtSignal(str)   # "cmd", "vscode", "second_brain"

    def __init__(self, on_submit: Optional[Callable[[CapturedCommand], None]] = None):
        super().__init__()
        self.on_submit = on_submit
        self.is_visible_state = False
        
        # Window attributes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(780, 160)
        self._center_window()
        
        # Stream Typewriter Effect State
        self.stream_full_text = ""
        self.stream_current_idx = 0
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self._stream_step)
        
        self._init_ui()
        self._bind_shortcuts()
        
        if self.on_submit:
            self.command_submitted.connect(self.on_submit)

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        pos_x = int((screen.width() - self.width()) / 2)
        pos_y = int(screen.height() * 0.16)
        self.move(pos_x, pos_y)

    def _init_ui(self):
        # Main Outer Container with Dark Glassmorphism Styling
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("HudBackground")
        self.bg_frame.setStyleSheet("""
            QFrame#HudBackground {
                background-color: rgba(11, 14, 20, 235);
                border: 1.5px solid #00F0FF;
                border-radius: 14px;
            }
        """)
        
        # Subtle Cyan Drop Glow Effect
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(28)
        glow.setColor(QColor(0, 240, 255, 90))
        glow.setOffset(0, 0)
        self.bg_frame.setGraphicsEffect(glow)
        
        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(14, 8, 14, 10)
        frame_layout.setSpacing(6)

        # ---------------- TOP BAR: Telemetry | Arc Reactor | Quick Shortcuts ----------------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        # Left Flank: System Telemetry
        self.telemetry_box = QVBoxLayout()
        self.telemetry_box.setSpacing(2)
        
        self.title_label = QLabel("⚡ JARVIS CORE // HUD v2.0")
        self.title_label.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        self.stat_cpu_ram = QLabel("CPU: 0%  |  RAM: 0.0GB (0%)")
        self.stat_cpu_ram.setStyleSheet("color: #94A3B8; font-family: 'Segoe UI', monospace; font-size: 10px;")
        
        self.stat_net = QLabel("NET: ▲ 0.0 KB/s  ▼ 0.0 KB/s")
        self.stat_net.setStyleSheet("color: #64748B; font-family: 'Segoe UI', monospace; font-size: 9.5px;")
        
        self.telemetry_box.addWidget(self.title_label)
        self.telemetry_box.addWidget(self.stat_cpu_ram)
        self.telemetry_box.addWidget(self.stat_net)
        top_bar.addLayout(self.telemetry_box, stretch=3)

        # Center: Central Vector Arc Reactor
        self.arc_reactor = ArcReactorWidget(self)
        top_bar.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        # Right Flank: Quick Launcher Tools
        right_box = QVBoxLayout()
        right_box.setSpacing(4)
        
        quick_title = QLabel("TACTICAL SHORTCUTS")
        quick_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        quick_title.setStyleSheet("color: #64748B; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;")
        right_box.addWidget(quick_title)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        btn_style = """
            QPushButton {
                background-color: #161B26;
                color: #38BDF8;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border-color: #00F0FF;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #0284C7;
            }
        """
        self.btn_cmd = QPushButton("CMD")
        self.btn_cmd.setStyleSheet(btn_style)
        self.btn_cmd.clicked.connect(lambda: self.shortcut_triggered.emit("cmd"))
        
        self.btn_code = QPushButton("VS CODE")
        self.btn_code.setStyleSheet(btn_style)
        self.btn_code.clicked.connect(lambda: self.shortcut_triggered.emit("vscode"))
        
        self.btn_sb = QPushButton("2ND BRAIN")
        self.btn_sb.setStyleSheet(btn_style)
        self.btn_sb.clicked.connect(lambda: self.shortcut_triggered.emit("second_brain"))
        
        btn_layout.addWidget(self.btn_cmd)
        btn_layout.addWidget(self.btn_code)
        btn_layout.addWidget(self.btn_sb)
        right_box.addLayout(btn_layout)
        
        top_bar.addLayout(right_box, stretch=3)
        frame_layout.addLayout(top_bar)

        # ---------------- MIDDLE: Command Input Field ----------------
        input_container = QHBoxLayout()
        input_container.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Speak or type command (e.g. 'Search note on SAMAY', 'Open VS Code')... [Enter: Send | Esc: Hide]")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(22, 27, 38, 220);
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 7px 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12.5px;
            }
            QLineEdit:focus {
                border: 1.5px solid #00F0FF;
                background-color: rgba(26, 32, 46, 240);
            }
        """)
        self.input_field.returnPressed.connect(self._handle_submit)
        
        self.send_btn = QPushButton("EXECUTE")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369A1;
                border: 1px solid #38BDF8;
            }
        """)
        self.send_btn.clicked.connect(self._handle_submit)
        
        input_container.addWidget(self.input_field, stretch=1)
        input_container.addWidget(self.send_btn)
        frame_layout.addLayout(input_container)

        # ---------------- BOTTOM: Console Output / Voice Stream ----------------
        console_layout = QHBoxLayout()
        console_layout.setContentsMargins(2, 0, 2, 0)
        
        self.status_pill = QLabel("[ ⚡ JARVIS READY ]")
        self.status_pill.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold;")
        
        self.console_stream = QLabel("Awaiting voice trigger (Win + J) or typed query...")
        self.console_stream.setStyleSheet("color: #94A3B8; font-family: 'Segoe UI', monospace; font-size: 10.5px;")
        
        console_layout.addWidget(self.status_pill)
        console_layout.addWidget(self.console_stream, stretch=1)
        frame_layout.addLayout(console_layout)

        self.main_layout.addWidget(self.bg_frame)

    def _bind_shortcuts(self):
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.activated.connect(self.hide_overlay)

    def update_telemetry(self, t: SystemTelemetryPayload):
        """Updates CPU, RAM, and Network readout."""
        self.stat_cpu_ram.setText(f"CPU: {t.cpu_percent}%  |  RAM: {t.ram_used_gb}GB / {t.ram_total_gb}GB ({t.ram_percent}%)")
        self.stat_net.setText(f"NET: ▲ {t.net_sent_kbps} KB/s  ▼ {t.net_recv_kbps} KB/s")

    def set_hud_state(self, state: str, message: str = ""):
        """
        Updates Arc Reactor state and status pill:
        - 'listening': [ 🎙️ LISTENING... ] (Electric Blue)
        - 'processing': [ ⚡ DECODING INTENT ] (Amber)
        - 'success': [ 🚀 EXECUTED ] (Emerald)
        - 'idle': [ ⚡ JARVIS READY ] (Cyan)
        """
        self.arc_reactor.set_state(state)
        
        if state == "listening":
            self.status_pill.setText("[ 🎙️ LISTENING ]")
            self.status_pill.setStyleSheet("color: #38BDF8; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold;")
            self.bg_frame.setStyleSheet("QFrame#HudBackground { background-color: rgba(11, 14, 20, 235); border: 1.5px solid #38BDF8; border-radius: 14px; }")
        elif state == "processing":
            self.status_pill.setText("[ ⚡ DECODING INTENT ]")
            self.status_pill.setStyleSheet("color: #F59E0B; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold;")
            self.bg_frame.setStyleSheet("QFrame#HudBackground { background-color: rgba(11, 14, 20, 235); border: 1.5px solid #F59E0B; border-radius: 14px; }")
        elif state == "success":
            self.status_pill.setText("[ 🚀 EXECUTED ]")
            self.status_pill.setStyleSheet("color: #10B981; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold;")
            self.bg_frame.setStyleSheet("QFrame#HudBackground { background-color: rgba(11, 14, 20, 235); border: 1.5px solid #10B981; border-radius: 14px; }")
        else:
            self.status_pill.setText("[ ⚡ JARVIS READY ]")
            self.status_pill.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold;")
            self.bg_frame.setStyleSheet("QFrame#HudBackground { background-color: rgba(11, 14, 20, 235); border: 1.5px solid #00F0FF; border-radius: 14px; }")

        if message:
            self.stream_response(message)

    def stream_response(self, text: str):
        """Typewriter text stream output."""
        self.stream_full_text = text
        self.stream_current_idx = 0
        self.console_stream.setText("")
        self.typewriter_timer.start(18) # 18ms per character

    def _stream_step(self):
        if self.stream_current_idx < len(self.stream_full_text):
            self.stream_current_idx += 1
            self.console_stream.setText(self.stream_full_text[:self.stream_current_idx])
        else:
            self.typewriter_timer.stop()

    def set_amplitude(self, amp: float):
        self.arc_reactor.set_amplitude(amp)

    def set_input_text(self, text: str):
        self.input_field.setText(text)
        self.input_field.setCursorPosition(len(text))

    def show_overlay(self):
        """Shows HUD overlay, animates wake, and grabs foreground focus."""
        self.is_visible_state = True
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Win32 foreground grab
        hwnd = int(self.winId())
        force_foreground_window(hwnd)
        
        self.input_field.setFocus()
        self.set_hud_state("listening")

    def hide_overlay(self):
        """Hides HUD overlay."""
        self.is_visible_state = False
        self.arc_reactor.set_amplitude(0.0)
        self.set_hud_state("idle")
        self.input_field.clear()
        self.hide()

    def toggle(self):
        if self.is_visible_state:
            self.hide_overlay()
        else:
            self.show_overlay()

    def _handle_submit(self):
        text = self.input_field.text().strip()
        if not text:
            self.hide_overlay()
            return
            
        clipboard_text = None
        try:
            clipboard_text = pyperclip.paste().strip() or None
        except Exception:
            pass

        # Determine target scope
        scope = "general_query"
        text_lower = text.lower()
        if any(w in text_lower for w in ["note", "second brain", "brain", "challenge", "samay", "todo"]):
            scope = "second_brain"
        elif any(w in text_lower for w in ["open", "launch", "run", "cmd", "vscode", "code"]):
            scope = "app_launcher"
        elif any(w in text_lower for w in ["stat", "cpu", "ram", "memory", "net"]):
            scope = "system_telemetry"

        cmd = CapturedCommand(
            trigger_source="manual" if not getattr(self, "_from_voice", False) else "voice_vad",
            raw_text=text,
            clipboard_context=clipboard_text,
            target_scope=scope
        )
        self._from_voice = False
        self.command_submitted.emit(cmd)
