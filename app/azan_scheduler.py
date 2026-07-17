"""Background azan scheduler: recomputes today's prayer times, and at each
of the 5 salah plays the user's chosen azan recording + shows a tray
notification. Runs on a QTimer so it keeps working as long as the app is
alive (including minimized to tray) -- no OS-level alarm needed since,
unlike the Android app, this desktop app can just stay resident.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from app import azan_voices, prayer_times
from app.i18n import translator
from app.location import current_location
from app.settings import settings

CHECK_INTERVAL_MS = 15_000
SALAH_KEYS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]


class AzanScheduler(QObject):
    prayer_fired = Signal(str, bool)    # prayer_key, sound_played
    times_recomputed = Signal(object)   # prayer_times.PrayerTimes

    def __init__(self, tray_icon=None, parent=None) -> None:
        super().__init__(parent)
        self._tray_icon = tray_icon
        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)

        self._today: date | None = None
        self._times: prayer_times.PrayerTimes | None = None
        self._fired_today: set[str] = set()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(CHECK_INTERVAL_MS)

        self.recompute()

    def set_tray_icon(self, tray_icon) -> None:
        self._tray_icon = tray_icon

    def _calc_for(self, d: date) -> prayer_times.PrayerTimes:
        loc = current_location()
        raw = prayer_times.calculate(
            d, loc.lat, loc.lon, loc.tz_offset,
            method_id=settings.calc_method, madhab=settings.madhab,
        )
        offsets = {k: settings.prayer_offset(k) for k in prayer_times.PRAYER_KEYS}
        return prayer_times.apply_manual_offsets(raw, offsets)

    def recompute(self) -> prayer_times.PrayerTimes:
        today = date.today()
        self._times = self._calc_for(today)
        self._today = today
        self._fired_today = set()
        self.times_recomputed.emit(self._times)
        return self._times

    @property
    def times(self) -> prayer_times.PrayerTimes | None:
        return self._times

    def current_and_next(self) -> tuple[str | None, str | None, datetime | None]:
        """(current_key, next_key, next_time) -- rolls over to tomorrow's fajr."""
        if self._times is None:
            return None, None, None
        now = datetime.now()
        current, nxt = prayer_times.next_and_current_prayer(self._times, now)
        if nxt is None:
            tomorrow_times = self._calc_for(date.today() + timedelta(days=1))
            return current, "fajr", tomorrow_times.fajr
        return current, nxt, self._times.as_dict()[nxt]

    def preview_voice_id(self, voice_id: str, is_fajr: bool = False) -> None:
        self._play_path(azan_voices.resolve_path(voice_id, is_fajr))
        if self._tray_icon is not None:
            self._tray_icon.showMessage(translator.t("app_title"), translator.t("preview"))

    def _play_path(self, path: str) -> None:
        self._audio_out.setVolume(max(0, min(100, settings.azan_volume)) / 100.0)
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()

    def _tick(self) -> None:
        if self._times is None or self._today != date.today():
            self.recompute()
            if self._times is None:
                return

        now = datetime.now()
        times_map = self._times.as_dict()
        for key in SALAH_KEYS:
            t = times_map[key]
            if key in self._fired_today:
                continue
            # fire once we've reached the minute of the prayer time
            if now >= t and now - t < timedelta(minutes=2):
                self._fired_today.add(key)
                self._fire(key)

    def _fire(self, key: str) -> None:
        if not settings.azan_enabled_for(key):
            self._notify(key, sound=False)
            self.prayer_fired.emit(key, False)
            return
        is_fajr = key == "fajr"
        voice_id = settings.fajr_azan_voice_id if is_fajr else settings.azan_voice_id
        self._play_path(azan_voices.resolve_path(voice_id, is_fajr))
        self._notify(key, sound=True)
        self.prayer_fired.emit(key, True)

    def _notify(self, key: str, sound: bool) -> None:
        if self._tray_icon is None:
            return
        prayer_label = translator.t(f"prayer_{key}")
        title = translator.t("azan_notif_title", prayer=prayer_label)
        self._tray_icon.showMessage(translator.t("app_title"), title)
