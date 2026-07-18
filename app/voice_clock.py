"""Announces the current time out loud at a user-chosen interval (15/30/60
minutes).

Two voices:
- English: Windows' built-in SAPI5 text-to-speech (pyttsx3). Speech is
  synchronous/blocking in pyttsx3, so each announcement runs on its own
  short-lived background thread to avoid freezing the UI.
- Bangla: Windows has no installed Bangla TTS voice, so instead this
  concatenates real recorded word clips (hour numbers, time-of-day words,
  minute values) bundled under assets/audio/voice_clock/, in the pattern
  "এখন সময় সকাল একটা, ত্রিশ মিনিট" -- silently skipping the minute clip
  when the time is exactly on the hour (e.g. "এখন সময় রাত বারোটা").
"""
from __future__ import annotations

import threading
import wave
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from app.paths import audio_path, user_data_dir
from app.settings import settings

CHECK_INTERVAL_MS = 15_000
VALID_INTERVALS = (15, 30, 60)
KNOWN_MINUTE_CLIPS = (15, 30, 45)


# ── English (SAPI5 TTS) ──────────────────────────────────────────────────
def _speak_english(text: str) -> None:
    def _run() -> None:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass  # TTS engine unavailable -- fail silently, non-critical feature.

    threading.Thread(target=_run, daemon=True).start()


def _english_phrase(now: datetime) -> str:
    hour12 = now.hour % 12
    if hour12 == 0:
        hour12 = 12
    period = "AM" if now.hour < 12 else "PM"
    if now.minute == 0:
        return f"It's now {hour12} {period}."
    return f"It's now {hour12}:{now.minute:02d} {period}."


# ── Bangla (recorded clip concatenation) ─────────────────────────────────
def _bn_period_and_hour(now: datetime) -> tuple[str, int]:
    hour24 = now.hour
    hour12 = hour24 % 12 or 12
    if hour24 >= 21 or hour24 < 4:
        period = "night"
    elif hour24 < 6:
        period = "dawn"
    elif hour24 < 12:
        period = "morning"
    elif hour24 < 15:
        period = "noon"
    elif hour24 < 18:
        period = "afternoon"
    else:
        period = "evening"
    return period, hour12


def _bn_clip_names(now: datetime) -> list[str]:
    period, hour12 = _bn_period_and_hour(now)
    names = ["now_time", f"period_{period}", f"hour_{hour12}"]
    if now.minute != 0:
        nearest = min(KNOWN_MINUTE_CLIPS, key=lambda m: abs(m - now.minute))
        names.append(f"min_{nearest}")
    return names


def _u8_to_s16le(raw: bytes) -> bytes:
    """Converts 8-bit unsigned PCM (silence=128) to 16-bit signed little-endian
    PCM. Some Windows media backends don't reliably decode past the first
    chunk of 8-bit WAV audio, cutting playback short; 16-bit PCM is
    universally supported."""
    out = bytearray(len(raw) * 2)
    for i, b in enumerate(raw):
        s = (b - 128) * 256
        out[2 * i] = s & 0xFF
        out[2 * i + 1] = (s >> 8) & 0xFF
    return bytes(out)


def _concat_clips(names: list[str], gap_ms: int = 260) -> str | None:
    """Concatenates bundled WAV word clips (with a short silence gap between
    hour and minute, standing in for the comma pause) into one temp file."""
    frames: list[bytes] = []
    params = None
    try:
        for i, name in enumerate(names):
            path = audio_path("voice_clock", f"{name}.wav")
            with wave.open(str(path), "rb") as w:
                if params is None:
                    params = w.getparams()
                    silence = b"\x80" * int(params.framerate * gap_ms / 1000) * params.sampwidth
                elif i > 0:
                    frames.append(silence)
                frames.append(w.readframes(w.getnframes()))
        if params is None:
            return None
        raw = b"".join(frames)
        sampwidth = params.sampwidth
        if sampwidth == 1:
            raw = _u8_to_s16le(raw)
            sampwidth = 2
        out_path = user_data_dir() / "voice_clock_tmp.wav"
        with wave.open(str(out_path), "wb") as out:
            out.setnchannels(params.nchannels)
            out.setsampwidth(sampwidth)
            out.setframerate(params.framerate)
            out.writeframes(raw)
        return str(out_path)
    except OSError:
        return None


class VoiceClock(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._last_announced: tuple[int, int] | None = None
        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(CHECK_INTERVAL_MS)

    def _announce(self, now: datetime) -> None:
        if settings.voice_clock_language == "bn":
            path = _concat_clips(_bn_clip_names(now))
            if path is not None:
                self._player.setSource(QUrl.fromLocalFile(path))
                self._player.play()
        else:
            _speak_english(_english_phrase(now))

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
        self._announce(now)

    def announce_now(self) -> None:
        """Manual "preview" trigger, e.g. a Test button in Settings."""
        self._announce(datetime.now())
