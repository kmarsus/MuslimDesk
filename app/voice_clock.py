"""Announces the current time out loud at a user-chosen interval (15/30/60
minutes), via Windows' built-in SAPI5 text-to-speech (pyttsx3). Speech is
synchronous/blocking in pyttsx3, so each announcement runs on its own
short-lived background thread to avoid freezing the UI.
"""
from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtCore import QObject, QTimer

from app.settings import settings

CHECK_INTERVAL_MS = 15_000
VALID_INTERVALS = (15, 30, 60)


def _speak(text: str) -> None:
    def _run() -> None:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass  # TTS engine unavailable -- fail silently, non-critical feature.

    threading.Thread(target=_run, daemon=True).start()


def _phrase_for(now: datetime) -> str:
    hour12 = now.hour % 12
    if hour12 == 0:
        hour12 = 12
    period = "AM" if now.hour < 12 else "PM"
    if now.minute == 0:
        return f"It's now {hour12} {period}."
    return f"It's now {hour12}:{now.minute:02d} {period}."


class VoiceClock(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._last_announced: tuple[int, int] | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(CHECK_INTERVAL_MS)

    def _tick(self) -> None:
        if not settings.voice_clock_enabled:
            return
        interval = settings.voice_clock_interval_min
        if interval not in VALID_INTERVALS:
            interval = 30
        now = datetime.now()
        if now.minute % interval != 0:
            return
        key = (now.hour, now.minute)
        if self._last_announced == key:
            return
        self._last_announced = key
        _speak(_phrase_for(now))

    def announce_now(self) -> None:
        """Manual "preview" trigger, e.g. a Test button in Settings."""
        _speak(_phrase_for(datetime.now()))
