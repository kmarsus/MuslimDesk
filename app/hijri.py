"""Hijri calendar, Islamic events, and yearly fasting reminders.

Mirrors lib/features/hijri_calendar/controllers/hijri_controller.dart:
arithmetic Hijri calendar (via `hijridate`) plus a manual day-offset the
user can dial in to match local moon-sighting announcements, a bundled
islamic_events.json, and a few fixed yearly fasting reminders that aren't
part of that file (Muharram, Arafah, Ayyam al-Bidh).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from hijridate import Hijri, Gregorian

from app.paths import data_path

MONTH_NAMES_EN = [
    "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani", "Jumada al-Awwal",
    "Jumada al-Thani", "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qi'dah",
    "Dhu al-Hijjah",
]
MONTH_NAMES_BN = [
    "মুহররম", "সফর", "রবিউল আউয়াল", "রবিউস সানি", "জমাদিউল আউয়াল", "জমাদিউস সানি",
    "রজব", "শাবান", "রমজান", "শাওয়াল", "জিলকদ", "জিলহজ",
]


def month_name(month: int, english: bool) -> str:
    return (MONTH_NAMES_EN if english else MONTH_NAMES_BN)[month - 1]


@dataclass(frozen=True)
class IslamicEvent:
    hijri_month: int
    hijri_day: int
    name_bn: str
    name_en: str = ""
    duration_days: int = 1

    def name(self, english: bool) -> str:
        return (self.name_en or self.name_bn) if english else self.name_bn


@dataclass(frozen=True)
class UpcomingEvent:
    event: IslamicEvent
    gregorian_date: date
    days_remaining: int


_YEARLY_FASTING_REMINDERS = [
    IslamicEvent(1, 9, "মুহাররমের রোজা (৯, ১০, ১১ থেকে যেকোনো ২ দিন)",
                 "Muharram fasting (any 2 of the 9th, 10th, 11th)", duration_days=3),
    IslamicEvent(12, 9, "আরাফার রোজা", "Day of Arafah fasting", duration_days=1),
]
_AYYAM_AL_BIDH_START = 13
_AYYAM_AL_BIDH_DURATION = 3
_AYYAM_AL_BIDH_NAME_BN = "আইয়্যামে বীযের রোজা (১৩, ১৪, ১৫)"
_AYYAM_AL_BIDH_NAME_EN = "Ayyam al-Bidh fasting (13th-15th)"


def _load_bundled_events() -> list[IslamicEvent]:
    raw = json.loads(Path(data_path("islamic_events.json")).read_text(encoding="utf-8"))
    return [
        IslamicEvent(
            hijri_month=e["hijriMonth"],
            hijri_day=e["hijriDay"],
            name_bn=e["nameBn"],
            duration_days=e.get("durationDays", 1),
        )
        for e in raw
    ]


class HijriCalendarService:
    def __init__(self) -> None:
        self.events: list[IslamicEvent] = _load_bundled_events()

    def today(self, offset_days: int = 0) -> Hijri:
        return Gregorian.fromdate(date.today() + timedelta(days=offset_days)).to_hijri()

    def from_gregorian(self, d: date, offset_days: int = 0) -> Hijri:
        return Gregorian.fromdate(d + timedelta(days=offset_days)).to_hijri()

    def to_gregorian(self, hijri_year: int, hijri_month: int, hijri_day: int, offset_days: int = 0) -> date:
        g = Hijri(hijri_year, hijri_month, hijri_day).to_gregorian()
        return date(g.year, g.month, g.day) - timedelta(days=offset_days)

    def days_in_month(self, year: int, month: int) -> int:
        return Hijri(year, month, 1).month_length()

    def weekday_of_first_day(self, year: int, month: int, offset_days: int = 0) -> int:
        """0=Sunday .. 6=Saturday, matching a typical calendar grid."""
        first = self.to_gregorian(year, month, 1, offset_days)
        # Python's date.weekday(): 0=Monday..6=Sunday -> convert to 0=Sunday..6=Saturday
        return (first.weekday() + 1) % 7

    def events_on(self, month: int, day: int) -> list[IslamicEvent]:
        from_events = [e for e in self.events if e.hijri_month == month and e.hijri_day == day]
        from_reminders = [
            e for e in _YEARLY_FASTING_REMINDERS
            if e.hijri_month == month and day >= e.hijri_day and day < e.hijri_day + e.duration_days
        ]
        ayyam = []
        if _AYYAM_AL_BIDH_START <= day < _AYYAM_AL_BIDH_START + _AYYAM_AL_BIDH_DURATION:
            ayyam = [IslamicEvent(month, day, _AYYAM_AL_BIDH_NAME_BN, _AYYAM_AL_BIDH_NAME_EN)]
        return from_events + from_reminders + ayyam

    def upcoming_events(self, offset_days: int = 0, limit: int = 10) -> list[UpcomingEvent]:
        now_hijri = self.today(offset_days)
        today_date = date.today()

        def upcoming_for(e: IslamicEvent) -> UpcomingEvent:
            within = (now_hijri.month == e.hijri_month and now_hijri.day >= e.hijri_day
                      and now_hijri.day < e.hijri_day + e.duration_days)
            year = now_hijri.year
            day = e.hijri_day
            if within:
                day = now_hijri.day
            else:
                passed = (e.hijri_month < now_hijri.month) or \
                         (e.hijri_month == now_hijri.month and e.hijri_day < now_hijri.day)
                if passed:
                    year += 1
            g = self.to_gregorian(year, e.hijri_month, day, offset_days)
            return UpcomingEvent(e, g, (g - today_date).days)

        def ayyam_upcoming() -> UpcomingEvent:
            within = _AYYAM_AL_BIDH_START <= now_hijri.day < _AYYAM_AL_BIDH_START + _AYYAM_AL_BIDH_DURATION
            month, year, day = now_hijri.month, now_hijri.year, _AYYAM_AL_BIDH_START
            if within:
                day = now_hijri.day
            elif now_hijri.day >= _AYYAM_AL_BIDH_START + _AYYAM_AL_BIDH_DURATION:
                month += 1
                if month > 12:
                    month, year = 1, year + 1
            e = IslamicEvent(month, day, _AYYAM_AL_BIDH_NAME_BN, _AYYAM_AL_BIDH_NAME_EN, _AYYAM_AL_BIDH_DURATION)
            g = self.to_gregorian(year, month, day, offset_days)
            return UpcomingEvent(e, g, (g - today_date).days)

        results = [upcoming_for(e) for e in self.events]
        results += [upcoming_for(e) for e in _YEARLY_FASTING_REMINDERS]
        results.append(ayyam_upcoming())
        results.sort(key=lambda u: u.days_remaining)
        return results[:limit]
