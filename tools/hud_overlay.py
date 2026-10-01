"""
J.A.R.V.I.S. Full-Screen Holographic HUD (PyQt6)
Implements:
- Full-Screen Dark HUD Canvas (#030508 with 0.92 glassmorphic opacity)
- Giant Centered Multi-Ring Arc Reactor Core with live 16-bar audio-reactive waveform
- Orbiting quantum energy particles and dynamic rotational acceleration (15 RPM -> 90 RPM)
- Stark Sci-Fi color palette (Cyan/Electric Blue -> Amber Gold -> Emerald Green)
- Sci-Fi Subtitle Stream with Typewriter Animation (Zero conventional text boxes)
- Audio cues (wake / dismiss chimes) and smooth holographic scale/fade transitions
"""

import sys
import os
import math
from typing import Callable, Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGraphicsDropShadowEffect, QFrame
)
from PyQt6.QtCore import (
    Qt, QTimer, QRectF, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, 
    QPainterPath, QKeySequence, QShortcut
)

from tools.models import CapturedCommand
from tools.win_keys import force_foreground_window
from tools.audio_sfx import play_wake_sound, play_dismiss_sound


class GiantArcReactorWidget(QWidget):
    """
    Giant Centered Arc Reactor Holographic Core:
    - Inner High-Intensity Energy Core & Radial Bloom
    - Middle Concentric Rotating Segmented Tick Tracks (Multi-Ring)
    - Outer 16-Bar Radial Audio-Reactive Waveform Equalizer
    - Orbiting Quantum Particle Streams
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(360, 360)
        
        self.angle_middle = 0.0
        self.angle_outer_track = 0.0
        self.angle_particles = 0.0
        self.rotation_speed = 1.2 # ~15 RPM idle
        self.amplitude = 0.0      # Current audio level (0.0 to 1.0)
        self.target_amplitude = 0.0
        self.state = "idle"       # "idle", "listening", "processing", "speaking", "success"
        self.pulse_phase = 0.0
        self.scale_factor = 1.0

        # High-refresh animation timer (~60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(16)

    def set_amplitude(self, amp: float):
        self.target_amplitude = max(0.0, min(amp, 1.0))

    def set_state(self, state: str):
        self.state = state
        if state == "processing":
            self.rotation_speed = 7.5 # Accelerated 90 RPM
        elif state == "listening":
            self.rotation_speed = 2.2
        elif state in ["speaking", "success"]:
            self.rotation_speed = 1.8
        else:
            self.rotation_speed = 1.2
        self.update()

    def _update_animation(self):
        # Continuous multi-track rotations
        self.angle_middle = (self.angle_middle + self.rotation_speed) % 360.0
        self.angle_outer_track = (self.angle_outer_track - self.rotation_speed * 0.7) % 360.0
        self.angle_particles = (self.angle_particles + self.rotation_speed * 2.0) % 360.0
        self.pulse_phase = (self.pulse_phase + 0.06) % (math.pi * 2)

        # Smooth audio amplitude interpolation (lerp)
        self.amplitude += (self.target_amplitude - self.amplitude) * 0.4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        
        # Determine color palette based on J.A.R.V.I.S. state
        if self.state == "listening":
            # Stark Cyan (#00F0FF) & Electric Blue (#3B82F6)
            primary_color = QColor(0, 240, 255)
            glow_color = QColor(59, 130, 246)
        elif self.state == "processing":
            # Amber Gold (#F59E0B)
            primary_color = QColor(245, 158, 11)
            glow_color = QColor(251, 191, 36)
        elif self.state in ["speaking", "success"]:
            # Emerald Green (#10B981)
            primary_color = QColor(16, 185, 129)
            glow_color = QColor(52, 211, 153)
        else:
            primary_color = QColor(0, 240, 255)
            glow_color = QColor(59, 130, 246)

        # ---------------- 1. Outer Holographic Perimeter Guide Ring ----------------
        outer_guide_r = 155.0
        painter.setPen(QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 45), 1.2, Qt.PenStyle.DashDotLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(center_x - outer_guide_r, center_y - outer_guide_r, outer_guide_r * 2, outer_guide_r * 2))

        # ---------------- 2. Outer Radial Audio Waveform Equalizer (16 Dynamic Bars) ----------------
        num_bars = 16
        base_radius = 110.0
        max_bar_len = 42.0
        
        for i in range(num_bars):
            theta = (i * (360.0 / num_bars)) * (math.pi / 180.0)
            
            # Modulate bar scaling with live mic amplitude + organic wave motion
            organic_wave = math.sin(self.pulse_phase * 2.5 + i * 0.8) * 0.12
            bar_scale = max(0.18, self.amplitude + organic_wave)
            bar_length = bar_scale * max_bar_len
            
            r_start = base_radius
            r_end = base_radius + bar_length
            
            x1 = center_x + r_start * math.cos(theta)
            y1 = center_y + r_start * math.sin(theta)
            x2 = center_x + r_end * math.cos(theta)
            y2 = center_y + r_end * math.sin(theta)
            
            alpha = int(140 + 115 * min(bar_scale, 1.0))
            bar_pen = QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), alpha), 4.0)
            bar_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(bar_pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # ---------------- 3. Middle Rotating Segmented Tick Ring (16 Segments) ----------------
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_middle)
        
        mid_radius = 85.0
        num_ticks = 16
        for j in range(num_ticks):
            deg = j * (360.0 / num_ticks)
            rad = deg * (math.pi / 180.0)
            tx1 = (mid_radius - 8.0) * math.cos(rad)
            ty1 = (mid_radius - 8.0) * math.sin(rad)
            tx2 = (mid_radius + 8.0) * math.cos(rad)
            ty2 = (mid_radius + 8.0) * math.sin(rad)
            
            tick_pen = QPen(QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 200), 2.5)
            tick_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(tick_pen)
            painter.drawLine(int(tx1), int(ty1), int(tx2), int(ty2))
            
        # Draw concentric track circle
        painter.setPen(QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 90), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-mid_radius, -mid_radius, mid_radius * 2, mid_radius * 2))
        painter.restore()

        # ---------------- 4. Inner Orbiting Quantum Particle Streams ----------------
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_particles)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
        
        num_particles = 4 if self.state == "processing" else 2
        for p_idx in range(num_particles):
            p_rad = (p_idx * (360.0 / num_particles)) * (math.pi / 180.0)
            px = 62.0 * math.cos(p_rad)
            py = 62.0 * math.sin(p_rad)
            painter.drawEllipse(QRectF(px - 3.5, py - 3.5, 7.0, 7.0))
        painter.restore()

        # ---------------- 5. Inner Core Reactor with Pulsing Radial Glow ----------------
        pulse_scale = 1.0 + 0.08 * math.sin(self.pulse_phase)
        core_radius = 48.0 * pulse_scale
        
        # Multi-stage radial energy bloom
        grad = QRadialGradient(center_x, center_y, core_radius * 2.0)
        grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        grad.setColorAt(0.3, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 220))
        grad.setColorAt(0.7, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 80))
        grad.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QRectF(center_x - core_radius * 1.8, center_y - core_radius * 1.8, core_radius * 3.6, core_radius * 3.6))
        
        # Central Core High-Intensity Disc
        painter.setPen(QPen(QColor(255, 255, 255, 250), 2.0))
        painter.setBrush(QBrush(primary_color))
        painter.drawEllipse(QRectF(center_x - core_radius * 0.55, center_y - core_radius * 0.55, core_radius * 1.1, core_radius * 1.1))


class JarvisHUDOverlay(QWidget):
    """
    Full-Screen Holographic J.A.R.V.I.S. HUD Window.
    Pure graphic overlay with zero conventional text boxes.
    """
    command_submitted = pyqtSignal(object) # CapturedCommand
    dismiss_requested = pyqtSignal()

    def __init__(self, on_submit: Optional[Callable[[CapturedCommand], None]] = None):
        super().__init__()
        self.on_submit = on_submit
        self.is_visible_state = False
        
        # Full-Screen Frameless Transparent Window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Typewriter Subtitle Stream State
        self.stream_full_text = ""
        self.stream_current_idx = 0
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self._stream_step)
        
        self._init_ui()
        self._bind_shortcuts()
        
        if self.on_submit:
            self.command_submitted.connect(self.on_submit)

    def _init_ui(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        # Main Root Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Full-Screen Dark Glass Backdrop (#030508 at 0.92 opacity)
        self.backdrop_frame = QFrame(self)
        self.backdrop_frame.setObjectName("HoloBackdrop")
        self.backdrop_frame.setStyleSheet("""
            QFrame#HoloBackdrop {
                background-color: rgba(3, 5, 8, 235);
            }
        """)

        backdrop_layout = QVBoxLayout(self.backdrop_frame)
        backdrop_layout.setContentsMargins(40, 40, 40, 40)

        # ---------------- TOP HEADER: System Telemetry Branding ----------------
        top_header = QHBoxLayout()
        self.header_title = QLabel("J.A.R.V.I.S. // STARK INDUSTRIES HOLOGRAPHIC INTERFACE")
        self.header_title.setStyleSheet("color: rgba(0, 240, 255, 180); font-family: 'Segoe UI', monospace; font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        
        self.esc_hint = QLabel("PRESS [ESC] TO DISMISS")
        self.esc_hint.setStyleSheet("color: rgba(148, 163, 184, 120); font-family: 'Segoe UI', monospace; font-size: 11px; letter-spacing: 1.5px;")
        
        top_header.addWidget(self.header_title)
        top_header.addStretch()
        top_header.addWidget(self.esc_hint)
        backdrop_layout.addLayout(top_header)

        backdrop_layout.addStretch(1)

        # ---------------- CENTER: Giant Arc Reactor Visualizer ----------------
        self.arc_reactor = GiantArcReactorWidget(self)
        backdrop_layout.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        backdrop_layout.addStretch(1)

        # ---------------- BOTTOM: Sci-Fi Subtitle Stream ----------------
        bottom_container = QVBoxLayout()
        bottom_container.setSpacing(10)
        
        self.status_badge = QLabel("[ J.A.R.V.I.S. IS LISTENING... ]")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        
        self.subtitle_label = QLabel("Speak your command, sir...")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("color: #F8FAFC; font-family: 'Segoe UI', sans-serif; font-size: 20px; font-weight: 500; letter-spacing: 0.5px;")
        
        bottom_container.addWidget(self.status_badge)
        bottom_container.addWidget(self.subtitle_label)
        backdrop_layout.addLayout(bottom_container)

        root_layout.addWidget(self.backdrop_frame)

    def _bind_shortcuts(self):
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.activated.connect(self.hide_overlay)

    def set_hud_state(self, state: str, message: str = ""):
        """
        Updates Arc Reactor state, colors, and status subtitle badge:
        - 'listening': [ J.A.R.V.I.S. IS LISTENING... ] (Stark Cyan)
        - 'processing': [ J.A.R.V.I.S. IS COMPUTING... ] (Amber Gold)
        - 'speaking': [ J.A.R.V.I.S. RESPONDING ] (Emerald Green)
        - 'success': [ ACTION COMPLETED ] (Emerald Green)
        - 'idle': [ J.A.R.V.I.S. STANDBY ] (Cyan)
        """
        self.arc_reactor.set_state(state)
        
        if state == "listening":
            self.status_badge.setText("[ J.A.R.V.I.S. IS LISTENING... ]")
            self.status_badge.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        elif state == "processing":
            self.status_badge.setText("[ J.A.R.V.I.S. IS COMPUTING... ]")
            self.status_badge.setStyleSheet("color: #F59E0B; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        elif state in ["speaking", "success"]:
            self.status_badge.setText("[ J.A.R.V.I.S. RESPONDING ]")
            self.status_badge.setStyleSheet("color: #10B981; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        else:
            self.status_badge.setText("[ J.A.R.V.I.S. STANDBY ]")
            self.status_badge.setStyleSheet("color: #00F0FF; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; letter-spacing: 2px;")

        if message:
            self.stream_response(message)

    def stream_response(self, text: str):
        """Typewriter character-by-character subtitle stream."""
        self.stream_full_text = text
        self.stream_current_idx = 0
        self.subtitle_label.setText("")
        self.typewriter_timer.start(20) # 20ms per character

    def _stream_step(self):
        if self.stream_current_idx < len(self.stream_full_text):
            self.stream_current_idx += 1
            self.subtitle_label.setText(self.stream_full_text[:self.stream_current_idx])
        else:
            self.typewriter_timer.stop()

    def set_amplitude(self, amp: float):
        self.arc_reactor.set_amplitude(amp)

    def show_overlay(self):
        """Shows full-screen holographic HUD, plays wake chime, and grabs foreground focus."""
        self.is_visible_state = True
        play_wake_sound()
        
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        
        # Grab Win32 OS foreground focus
        hwnd = int(self.winId())
        force_foreground_window(hwnd)
        
        self.set_hud_state("listening", "At your service, sir. I am listening...")

    def hide_overlay(self):
        """Plays dismiss chime and closes HUD overlay."""
        if self.is_visible_state:
            play_dismiss_sound()
        self.is_visible_state = False
        self.arc_reactor.set_amplitude(0.0)
        self.set_hud_state("idle")
        self.hide()
        self.dismiss_requested.emit()

    def toggle(self):
        if self.is_visible_state:
            self.hide_overlay()
        else:
            self.show_overlay()
