"""One-off: synthesizes simple beep-tone WAV files for the Alarm Sound
catalog (app/alarm_sounds.py) -- pure sine-wave generation via the stdlib
wave module, no external audio assets needed. Each clip is designed to
sound natural when looped infinitely by QMediaPlayer (a beep pattern
followed by a pause, repeating)."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "audio" / "alarm_sounds"
FRAMERATE = 22050
AMPLITUDE = 0.5  # fraction of full scale, keeps headroom to avoid clipping/distortion


def _tone(freq_hz: float, duration_s: float, fade_ms: float = 8.0) -> list[int]:
    n = int(FRAMERATE * duration_s)
    fade_samples = max(1, int(FRAMERATE * fade_ms / 1000))
    samples = []
    for i in range(n):
        t = i / FRAMERATE
        val = math.sin(2 * math.pi * freq_hz * t)
        # Short fade in/out on each tone to avoid audible clicks at the edges.
        if i < fade_samples:
            val *= i / fade_samples
        elif i > n - fade_samples:
            val *= (n - i) / fade_samples
        samples.append(int(val * AMPLITUDE * 32767))
    return samples


def _silence(duration_s: float) -> list[int]:
    return [0] * int(FRAMERATE * duration_s)


def _write(name: str, samples: list[int]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FRAMERATE)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    print(f"wrote {path} ({len(samples)/FRAMERATE:.2f}s)")


def build_classic_beep() -> None:
    """A single steady beep, repeated three times -- the traditional
    "beep... beep... beep" digital alarm clock sound."""
    samples: list[int] = []
    for _ in range(3):
        samples += _tone(800, 0.18)
        samples += _silence(0.18)
    samples += _silence(0.3)
    _write("beep_classic.wav", samples)


def build_digital_beep() -> None:
    """Two alternating tones, faster-paced -- like a digital wristwatch alarm."""
    samples: list[int] = []
    for _ in range(4):
        samples += _tone(1000, 0.09)
        samples += _tone(1300, 0.09)
    samples += _silence(0.35)
    _write("beep_digital.wav", samples)


def build_gentle_beep() -> None:
    """A softer, less jarring single tone with more space between beeps."""
    samples: list[int] = []
    for _ in range(2):
        samples += _tone(600, 0.25)
        samples += _silence(0.35)
    samples += _silence(0.3)
    _write("beep_gentle.wav", samples)


def build_urgent_beep() -> None:
    """A fast triple-beep burst -- more attention-grabbing."""
    samples: list[int] = []
    for _ in range(6):
        samples += _tone(900, 0.08)
        samples += _silence(0.06)
    samples += _silence(0.3)
    _write("beep_urgent.wav", samples)


if __name__ == "__main__":
    build_classic_beep()
    build_digital_beep()
    build_gentle_beep()
    build_urgent_beep()
