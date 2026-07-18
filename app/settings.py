"""Persisted user preferences, backed by an INI file in the user's local
app-data folder (portable, no registry writes -- works the same whether
running from source or from the packaged exe)."""
from __future__ import annotations

import json

from PySide6.QtCore import QSettings

from app.paths import user_data_dir

PRAYER_KEYS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
ALL_PRAYER_KEYS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]


class Settings:
    def __init__(self) -> None:
        ini_path = str(user_data_dir() / "settings.ini")
        self._qs = QSettings(ini_path, QSettings.Format.IniFormat)

    # ── generic helpers ──────────────────────────────────────────────
    def _get(self, key: str, default):
        val = self._qs.value(key, default)
        if isinstance(default, bool):
            return str(val).lower() in ("1", "true", "yes") if isinstance(val, str) else bool(val)
        if isinstance(default, int) and not isinstance(default, bool):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default
        if isinstance(default, float):
            try:
                return float(val)
            except (TypeError, ValueError):
                return default
        return val

    def _set(self, key: str, value) -> None:
        self._qs.setValue(key, value)
        self._qs.sync()

    # ── language / theme / font ──────────────────────────────────────
    @property
    def language(self) -> str:
        return self._get("language", "bn")

    @language.setter
    def language(self, v: str) -> None:
        self._set("language", v)

    @property
    def dark_mode(self) -> bool:
        return self._get("dark_mode", False)

    @dark_mode.setter
    def dark_mode(self, v: bool) -> None:
        self._set("dark_mode", v)

    @property
    def arabic_font(self) -> str:
        return self._get("arabic_font", "Amiri")

    @arabic_font.setter
    def arabic_font(self, v: str) -> None:
        self._set("arabic_font", v)

    @property
    def ui_font(self) -> str:
        """Font for the general interface text (menus, buttons, Bangla labels,
        etc.) -- separate from arabic_font, which only affects Quran/Azkar/Dua
        Arabic-script text."""
        return self._get("ui_font", "System Default")

    @ui_font.setter
    def ui_font(self, v: str) -> None:
        self._set("ui_font", v)

    # ── location ──────────────────────────────────────────────────────
    @property
    def location_mode(self) -> str:
        """'city' (pick from cities_bd.json) or 'manual' (lat/lon/tz entered)."""
        return self._get("location_mode", "city")

    @location_mode.setter
    def location_mode(self, v: str) -> None:
        self._set("location_mode", v)

    @property
    def country_code(self) -> str:
        return self._get("country_code", "BD")

    @country_code.setter
    def country_code(self, v: str) -> None:
        self._set("country_code", v)

    @property
    def city_key(self) -> str:
        return self._get("city_key", "Dhaka")

    @city_key.setter
    def city_key(self, v: str) -> None:
        self._set("city_key", v)

    @property
    def manual_lat(self) -> float:
        return self._get("manual_lat", 23.8103)

    @manual_lat.setter
    def manual_lat(self, v: float) -> None:
        self._set("manual_lat", v)

    @property
    def manual_lon(self) -> float:
        return self._get("manual_lon", 90.4125)

    @manual_lon.setter
    def manual_lon(self, v: float) -> None:
        self._set("manual_lon", v)

    @property
    def manual_tz_offset(self) -> float:
        return self._get("manual_tz_offset", 6.0)

    @manual_tz_offset.setter
    def manual_tz_offset(self, v: float) -> None:
        self._set("manual_tz_offset", v)

    @property
    def manual_label(self) -> str:
        return self._get("manual_label", "Custom location")

    @manual_label.setter
    def manual_label(self, v: str) -> None:
        self._set("manual_label", v)

    # ── prayer calculation ───────────────────────────────────────────
    @property
    def calc_method(self) -> str:
        return self._get("calc_method", "karachi")

    @calc_method.setter
    def calc_method(self, v: str) -> None:
        self._set("calc_method", v)

    @property
    def madhab(self) -> str:
        return self._get("madhab", "hanafi")

    @madhab.setter
    def madhab(self, v: str) -> None:
        self._set("madhab", v)

    # ── manual prayer-time adjustment (minutes, +/-) ─────────────────
    def prayer_offset(self, prayer_key: str) -> int:
        return self._get(f"prayer_offset_{prayer_key}", 0)

    def set_prayer_offset(self, prayer_key: str, minutes: int) -> None:
        self._set(f"prayer_offset_{prayer_key}", minutes)

    # ── azan ──────────────────────────────────────────────────────────
    @property
    def azan_master_enabled(self) -> bool:
        return self._get("azan_master_enabled", True)

    @azan_master_enabled.setter
    def azan_master_enabled(self, v: bool) -> None:
        self._set("azan_master_enabled", v)

    def azan_enabled_for(self, prayer_key: str) -> bool:
        raw = self._get(f"azan_enabled_{prayer_key}", None)
        if raw is None:
            return self.azan_master_enabled
        return str(raw).lower() in ("1", "true", "yes") if isinstance(raw, str) else bool(raw)

    def set_azan_enabled_for(self, prayer_key: str, enabled: bool) -> None:
        self._set(f"azan_enabled_{prayer_key}", enabled)

    @property
    def azan_voice_id(self) -> str:
        return self._get("azan_voice_id", "makkah")

    @azan_voice_id.setter
    def azan_voice_id(self, v: str) -> None:
        self._set("azan_voice_id", v)

    @property
    def fajr_azan_voice_id(self) -> str:
        return self._get("fajr_azan_voice_id", "fajr")

    @fajr_azan_voice_id.setter
    def fajr_azan_voice_id(self, v: str) -> None:
        self._set("fajr_azan_voice_id", v)

    @property
    def azan_volume(self) -> int:
        return self._get("azan_volume", 80)

    @azan_volume.setter
    def azan_volume(self, v: int) -> None:
        self._set("azan_volume", v)

    # ── misc ──────────────────────────────────────────────────────────
    @property
    def azan_custom_message(self) -> str:
        """Empty string means "use the default translated reminder text"."""
        return self._get("azan_custom_message", "")

    @azan_custom_message.setter
    def azan_custom_message(self, v: str) -> None:
        self._set("azan_custom_message", v)

    @property
    def close_browsers_on_azan(self) -> bool:
        return self._get("close_browsers_on_azan", False)

    @close_browsers_on_azan.setter
    def close_browsers_on_azan(self, v: bool) -> None:
        self._set("close_browsers_on_azan", v)

    @property
    def close_browsers_delay_sec(self) -> int:
        return self._get("close_browsers_delay_sec", 30)

    @close_browsers_delay_sec.setter
    def close_browsers_delay_sec(self, v: int) -> None:
        self._set("close_browsers_delay_sec", v)

    @property
    def hijri_offset(self) -> int:
        return self._get("hijri_offset", 0)

    @hijri_offset.setter
    def hijri_offset(self, v: int) -> None:
        self._set("hijri_offset", v)

    @property
    def voice_clock_enabled(self) -> bool:
        return self._get("voice_clock_enabled", True)

    @voice_clock_enabled.setter
    def voice_clock_enabled(self, v: bool) -> None:
        self._set("voice_clock_enabled", v)

    @property
    def voice_clock_interval_min(self) -> int:
        return self._get("voice_clock_interval_min", 30)

    @voice_clock_interval_min.setter
    def voice_clock_interval_min(self, v: int) -> None:
        self._set("voice_clock_interval_min", v)

    @property
    def voice_clock_language(self) -> str:
        """'bn' (recorded Bangla clips) or 'en' (SAPI5 text-to-speech)."""
        return self._get("voice_clock_language", "bn")

    @voice_clock_language.setter
    def voice_clock_language(self, v: str) -> None:
        self._set("voice_clock_language", v)

    @property
    def show_speed_tray(self) -> bool:
        return self._get("show_speed_tray", True)

    @show_speed_tray.setter
    def show_speed_tray(self, v: bool) -> None:
        self._set("show_speed_tray", v)

    @property
    def start_minimized(self) -> bool:
        return self._get("start_minimized", False)

    @start_minimized.setter
    def start_minimized(self, v: bool) -> None:
        self._set("start_minimized", v)

    @property
    def tasbih_target(self) -> int:
        return self._get("tasbih_target", 33)

    @tasbih_target.setter
    def tasbih_target(self, v: int) -> None:
        self._set("tasbih_target", v)

    @property
    def tasbih_count(self) -> int:
        return self._get("tasbih_count", 0)

    @tasbih_count.setter
    def tasbih_count(self, v: int) -> None:
        self._set("tasbih_count", v)

    @property
    def quran_show_arabic(self) -> bool:
        return self._get("quran_show_arabic", True)

    @quran_show_arabic.setter
    def quran_show_arabic(self, v: bool) -> None:
        self._set("quran_show_arabic", v)

    @property
    def quran_show_translation(self) -> bool:
        return self._get("quran_show_translation", True)

    @quran_show_translation.setter
    def quran_show_translation(self, v: bool) -> None:
        self._set("quran_show_translation", v)

    @property
    def quran_show_recitation(self) -> bool:
        return self._get("quran_show_recitation", False)

    @quran_show_recitation.setter
    def quran_show_recitation(self, v: bool) -> None:
        self._set("quran_show_recitation", v)

    @property
    def bookmark_surah(self) -> int:
        return self._get("bookmark_surah", 0)

    @bookmark_surah.setter
    def bookmark_surah(self, v: int) -> None:
        self._set("bookmark_surah", v)

    @property
    def last_read_surah(self) -> int:
        return self._get("last_read_surah", 1)

    @last_read_surah.setter
    def last_read_surah(self, v: int) -> None:
        self._set("last_read_surah", v)

    @property
    def last_read_ayah(self) -> int:
        return self._get("last_read_ayah", 1)

    @last_read_ayah.setter
    def last_read_ayah(self, v: int) -> None:
        self._set("last_read_ayah", v)


settings = Settings()
