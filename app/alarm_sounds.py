"""Catalog of bundled Alarm Clock sounds -- deliberately separate from
azan_voices.py. Alarms use simple beep tones by default, not reciter
voices; azan playback is never affected by anything in this module."""
from __future__ import annotations

from dataclasses import dataclass

from app.paths import audio_path


@dataclass(frozen=True)
class AlarmSound:
    id: str
    file_name: str
    label_en: str
    label_bn: str

    @property
    def path(self) -> str:
        return str(audio_path("alarm_sounds", self.file_name))


CLASSIC = AlarmSound("beep_classic", "beep_classic.wav", "Classic Beep", "ক্লাসিক বিপ")
DIGITAL = AlarmSound("beep_digital", "beep_digital.wav", "Digital Alarm", "ডিজিটাল অ্যালার্ম")
GENTLE = AlarmSound("beep_gentle", "beep_gentle.wav", "Gentle Beep", "নরম বিপ")
URGENT = AlarmSound("beep_urgent", "beep_urgent.wav", "Urgent Beep", "জরুরি বিপ")

ALL: list[AlarmSound] = [CLASSIC, DIGITAL, GENTLE, URGENT]
DEFAULT = CLASSIC


def by_id(sound_id: str) -> AlarmSound:
    for s in ALL:
        if s.id == sound_id:
            return s
    return DEFAULT


def resolve_path(sound_id: str) -> str:
    """Resolves a sound id (bundled or "custom:<id>") to a playable file path."""
    if sound_id and sound_id.startswith("custom:"):
        from app.custom_sounds import find_custom_sound
        custom = find_custom_sound(sound_id)
        if custom is not None:
            return custom.path
    return by_id(sound_id).path
