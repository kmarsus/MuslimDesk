"""Catalog of bundled azan (call to prayer) audio choices.

Ported from lib/core/constants/azan_voices.dart -- same 7 bundled
recordings, same id/label pairing, same Fajr-gets-an-extra-choice rule
(the dedicated Fajr recording includes the "as-salatu khayrun min an-nawm"
line, so it's offered alongside the regular voices for Fajr specifically).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.paths import audio_path


@dataclass(frozen=True)
class AzanVoice:
    id: str
    file_name: str
    label_en: str
    label_bn: str

    def label(self, english: bool) -> str:
        return self.label_en if english else self.label_bn

    @property
    def path(self) -> str:
        return str(audio_path(self.file_name))


MAKKAH = AzanVoice("makkah", "azan_makkah.mp3", "Makkah (Masjid al-Haram)", "মক্কা (মসজিদুল হারাম)")
ALAFASI = AzanVoice("alafasi", "azan_alafasi.mp3", "Mishary Rashid Alafasi", "মিশারী রাশেদ আলাফাসি")
ALMENSHAWY = AzanVoice("almenshawy", "azan_almenshawy.mp3", "Mohammad Al-Menshawy", "মুহাম্মদ আল-মিনশাবি")
ALQATAMI = AzanVoice("alqatami", "azan_alqatami.mp3", "Nasser Alqatami", "নাসের আল-কাতামি")
ABDULBASIT = AzanVoice("abdulbasit", "azan_abdulbasit.mp3", "Abdul Basit", "আব্দুল বাসিত")
RIFAAT = AzanVoice("rifaat", "azan_rifaat.mp3", "Mohammad Rifaat", "মুহাম্মদ রিফাত")
FAJR = AzanVoice("fajr", "azan_fajr.mp3", "Fajr Azan (Malek Chebae)", "ফজরের আজান (মালেক চেবা)")

REGULAR: list[AzanVoice] = [MAKKAH, ALAFASI, ALMENSHAWY, ALQATAMI, ABDULBASIT, RIFAAT]
FOR_FAJR: list[AzanVoice] = [FAJR, MAKKAH, ALAFASI, ALMENSHAWY, ALQATAMI, ABDULBASIT, RIFAAT]

DEFAULT_REGULAR = MAKKAH
DEFAULT_FAJR = FAJR


def by_id(voice_id: str, is_fajr: bool) -> AzanVoice:
    choices = FOR_FAJR if is_fajr else REGULAR
    for v in choices:
        if v.id == voice_id:
            return v
    return DEFAULT_FAJR if is_fajr else DEFAULT_REGULAR


def resolve_path(voice_id: str, is_fajr: bool = False) -> str:
    """Resolves a voice id (bundled or "custom:<id>") to a playable file path."""
    if voice_id and voice_id.startswith("custom:"):
        from app.custom_sounds import find_custom_sound
        custom = find_custom_sound(voice_id)
        if custom is not None:
            return custom.path
    return by_id(voice_id, is_fajr=is_fajr).path
