"""Watches the configured alarms and fires a signal when one is due.

Separate from AzanScheduler (prayer times) -- this is a general-purpose
alarm clock (e.g. "wake me at 6am" or "shut the PC down at midnight").
"""
from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import QObject, QTimer, Signal

from app.alarms import Alarm, load_alarms, save_alarms

CHECK_INTERVAL_MS = 10_000


class AlarmManager(QObject):
    alarm_fired = Signal(object)  # Alarm

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.alarms: list[Alarm] = load_alarms()
        self._last_fired_date: dict[str, date] = {}

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(CHECK_INTERVAL_MS)

    def reload(self) -> None:
        self.alarms = load_alarms()

    def save(self) -> None:
        save_alarms(self.alarms)

    def add_or_update(self, alarm: Alarm) -> None:
        for i, a in enumerate(self.alarms):
            if a.id == alarm.id:
                self.alarms[i] = alarm
                break
        else:
            self.alarms.append(alarm)
        self.save()

    def delete(self, alarm_id: str) -> None:
        self.alarms = [a for a in self.alarms if a.id != alarm_id]
        self.save()

    def _tick(self) -> None:
        now = datetime.now()
        hhmm = now.strftime("%H:%M")
        today = now.date()
        for alarm in self.alarms:
            if not alarm.enabled or alarm.time != hhmm:
                continue
            if not alarm.repeats_today(now.weekday()):
                continue
            if self._last_fired_date.get(alarm.id) == today:
                continue
            self._last_fired_date[alarm.id] = today
            self.alarm_fired.emit(alarm)
