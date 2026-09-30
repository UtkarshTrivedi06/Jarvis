"""
CustomTkinter Floating Overlay UI for Jarvis
Implements sleek dark-theme frameless window with voice typing & clipboard integration.
"""

import customtkinter as ctk
import pyperclip
from typing import Callable, Optional
from tools.models import CapturedCommand
from tools.win_keys import force_foreground_window, simulate_win_h

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class JarvisOverlay(ctk.CTk):
    def __init__(self, on_submit: Optional[Callable[[CapturedCommand], None]] = None):
        super().__init__()
        self.on_submit = on_submit
        
        # Window attributes
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F1117") # Sleek deep slate
        
        # Dimensions & screen positioning
        self.window_width = 680
        self.window_height = 80
        self._position_window()
        
        # Build UI layout
        self._create_widgets()
        self._bind_events()
        
        # Hidden by default on boot
        self.withdraw()
        self.is_visible = False

    def _position_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = int((screen_width - self.window_width) / 2)
        pos_y = int(screen_height * 0.18) # Upper 18% of screen
        self.geometry(f"{self.window_width}x{self.window_height}+{pos_x}+{pos_y}")

    def _create_widgets(self):
        # Outer border frame with subtle glow
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#181A20",
            corner_radius=14,
            border_width=2,
            border_color="#3B82F6" # Blue accent
        )
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Top/Center layout container
        self.content_box = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_box.pack(fill="both", expand=True, padx=14, pady=12)
        
        # Left Icon / Voice Indicator
        self.mic_label = ctk.CTkLabel(
            self.content_box,
            text="⚡ JARVIS",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#60A5FA"
        )
        self.mic_label.pack(side="left", padx=(4, 12))
        
        # Central Input Entry
        self.entry = ctk.CTkEntry(
            self.content_box,
            placeholder_text="Speak or type a command... (Enter to submit, Esc to hide)",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#222630",
            border_width=1,
            border_color="#374151",
            text_color="#F3F4F6",
            placeholder_text_color="#9CA3AF",
            height=44,
            corner_radius=8
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Quick submit action button
        self.submit_btn = ctk.CTkButton(
            self.content_box,
            text="Send",
            width=65,
            height=40,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._handle_submit
        )
        self.submit_btn.pack(side="right")

    def _bind_events(self):
        self.entry.bind("<Return>", lambda e: self._handle_submit())
        self.bind("<Escape>", lambda e: self.hide())
        self.entry.bind("<Escape>", lambda e: self.hide())

    def show(self, trigger_source: str = "win+j"):
        """Displays overlay, grabs focus, and triggers Win+H speech dictation."""
        self.trigger_source = trigger_source
        self.is_visible = True
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        
        # Acquire Win32 foreground focus
        hwnd = self.winfo_id()
        force_foreground_window(hwnd)
        
        # Focus input widget
        self.entry.delete(0, "end")
        self.entry.focus_force()
        
        # Update voice status indicator
        self.mic_label.configure(text="🎙️ LISTENING", text_color="#EF4444")
        
        # Settle delay before triggering Win + H dictation
        self.after(120, self._trigger_dictation)

    def _trigger_dictation(self):
        """Simulates Win + H to open Windows Voice Typing directly into the entry box."""
        simulate_win_h()

    def hide(self):
        """Hides the overlay instantly and restores default status."""
        self.mic_label.configure(text="⚡ JARVIS", text_color="#60A5FA")
        self.entry.delete(0, "end")
        self.withdraw()
        self.is_visible = False

    def toggle(self):
        """Toggles the visibility state."""
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def _handle_submit(self):
        text = self.entry.get().strip()
        if not text:
            self.hide()
            return
            
        # Optional clipboard capture
        clipboard_data = None
        try:
            clipboard_data = pyperclip.paste().strip()
            if not clipboard_data:
                clipboard_data = None
        except Exception:
            pass
            
        payload = CapturedCommand(
            trigger_source=getattr(self, "trigger_source", "win+j"),
            raw_text=text,
            clipboard_context=clipboard_data
        )
        
        self.hide()
        
        if self.on_submit:
            self.on_submit(payload)
