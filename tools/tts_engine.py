"""
J.A.R.V.I.S. Local Text-to-Speech Engine
Uses Windows SAPI with British/US male voice persona running on a background worker thread.
"""

import threading
import pythoncom
import win32com.client
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class TTSWorker(QThread):
    speech_started = pyqtSignal()
    speech_finished = pyqtSignal()

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        try:
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Prefer British English voice for authentic J.A.R.V.I.S. persona
            voices = speaker.GetVoices()
            for i in range(voices.Count):
                desc = voices.Item(i).GetDescription()
                if "Great Britain" in desc or "Hazel" in desc:
                    speaker.Voice = voices.Item(i)
                    break
            
            # Slightly faster, articulate speaking rate (+1)
            speaker.Rate = 1
            speaker.Volume = 100
            
            self.speech_started.emit()
            speaker.Speak(self.text)
            self.speech_finished.emit()
        except Exception as e:
            print(f"[TTSWorker] Error during speech output: {e}")
            self.speech_finished.emit()
        finally:
            pythoncom.CoUninitialize()


class TTSEngine(QObject):
    speech_started = pyqtSignal()
    speech_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

    def speak(self, text: str):
        """Asynchronously speaks text without blocking the GUI thread."""
        if not text:
            return
        # Clean text of markdown formatting for speech
        clean_text = text.replace("#", "").replace("*", "").replace("`", "").replace(">", "").replace("[", "").replace("]", "")
        
        self.worker = TTSWorker(clean_text)
        self.worker.speech_started.connect(self.speech_started.emit)
        self.worker.speech_finished.connect(self.speech_finished.emit)
        self.worker.start()
