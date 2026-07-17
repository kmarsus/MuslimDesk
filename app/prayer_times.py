"""Offline astronomical prayer-time calculator.

Implements the same public-domain solar-position algorithm used by
praytimes.org and the batoulapps/Adhan libraries (the one the Android app's
`adhan` Dart package wraps): NOAA low-precision sun position, equation of
time, and the standard sun-angle / shadow-length formulas for each prayer.
Pure Python, no network access required at runtime.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


# ── angle helpers (all trig here works in degrees) ──────────────────────
def _dsin(d: float) -> float:
    return math.sin(math.radians(d))


def _dcos(d: float) -> float:
    return math.cos(math.radians(d))


def _dtan(d: float) -> float:
    return math.tan(math.radians(d))


def _darcsin(x: float) -> float:
    return math.degrees(math.asin(max(-1.0, min(1.0, x))))


def _darccos(x: float) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, x))))


def _darctan2(y: float, x: float) -> float:
    return math.degrees(math.atan2(y, x))


def _darccot(x: float) -> float:
    return math.degrees(math.atan2(1.0, x))


def _fixangle(a: float) -> float:
    a = a % 360.0
    return a + 360.0 if a < 0 else a


def _fixhour(a: float) -> float:
    a = a % 24.0
    return a + 24.0 if a < 0 else a


def _julian_date(y: int, m: int, d: int) -> float:
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5


def _sun_position(jd: float) -> tuple[float, float]:
    """Returns (declination_deg, equation_of_time_hours) for a Julian date."""
    d = jd - 2451545.0
    g = _fixangle(357.529 + 0.98560028 * d)
    q = _fixangle(280.459 + 0.98564736 * d)
    ell = _fixangle(q + 1.915 * _dsin(g) + 0.020 * _dsin(2 * g))

    e = 23.439 - 0.00000036 * d
    ra = _darctan2(_dcos(e) * _dsin(ell), _dcos(ell)) / 15.0
    ra = _fixhour(ra)
    eqt = q / 15.0 - ra
    decl = _darcsin(_dsin(e) * _dsin(ell))
    return decl, eqt


# ── calculation method presets ───────────────────────────────────────────
@dataclass(frozen=True)
class CalcMethod:
    id: str
    label_en: str
    label_bn: str
    fajr_angle: float
    isha_angle: float | None = None
    isha_interval_min: int | None = None  # used instead of isha_angle when set
    maghrib_angle: float = 0.833  # standard horizon dip (refraction + solar radius)
    # per-prayer minute adjustments applied after the raw calculation
    adjustments: dict = field(default_factory=dict)


CALC_METHODS: dict[str, CalcMethod] = {
    m.id: m
    for m in [
        CalcMethod("karachi", "Karachi (common in Bangladesh)", "কারাচী (বাংলাদেশে প্রচলিত)", 18.0, isha_angle=18.0),
        CalcMethod("muslim_world_league", "Muslim World League", "মুসলিম ওয়ার্ল্ড লীগ", 18.0, isha_angle=17.0),
        CalcMethod("egyptian", "Egyptian", "মিশর", 19.5, isha_angle=17.5),
        CalcMethod("umm_al_qura", "Umm al-Qura (Makkah)", "উম্মুল কুরা (মক্কা)", 18.5, isha_interval_min=90),
        CalcMethod("dubai", "Dubai", "দুবাই", 18.2, isha_angle=18.2,
                   adjustments={"sunrise": -3, "dhuhr": 3, "asr": 3, "maghrib": 3}),
        CalcMethod("qatar", "Qatar", "কাতার", 18.0, isha_interval_min=90),
        CalcMethod("kuwait", "Kuwait", "কুয়েত", 18.0, isha_angle=17.5),
        CalcMethod("moon_sighting_committee", "Moonsighting Committee", "মুনসাইটিং কমিটি", 18.0, isha_angle=18.0,
                   adjustments={"dhuhr": 5}),
        CalcMethod("singapore", "Singapore", "সিঙ্গাপুর", 20.0, isha_angle=18.0),
        CalcMethod("north_america", "North America (ISNA)", "উত্তর আমেরিকা (ISNA)", 15.0, isha_angle=15.0),
        CalcMethod("turkey", "Turkey", "তুরস্ক", 18.0, isha_angle=17.0,
                   adjustments={"sunrise": -7, "dhuhr": 5, "asr": 4, "maghrib": 7}),
        CalcMethod("tehran", "Tehran", "তেহরান", 17.7, isha_angle=14.0, maghrib_angle=4.5),
    ]
}
DEFAULT_METHOD_ID = "karachi"

MADHAB_SHAFI = "shafi"
MADHAB_HANAFI = "hanafi"
ASR_FACTOR = {MADHAB_SHAFI: 1.0, MADHAB_HANAFI: 2.0}

PRAYER_KEYS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]


@dataclass
class PrayerTimes:
    fajr: datetime
    sunrise: datetime
    dhuhr: datetime
    asr: datetime
    maghrib: datetime
    isha: datetime

    def as_dict(self) -> dict[str, datetime]:
        return {
            "fajr": self.fajr, "sunrise": self.sunrise, "dhuhr": self.dhuhr,
            "asr": self.asr, "maghrib": self.maghrib, "isha": self.isha,
        }


def _hours_to_time(day: date, hours: float, tz_offset_hours: float) -> datetime:
    """hours is a fixhour()'d value in [0,24); may legitimately round to 24:00."""
    base = datetime(day.year, day.month, day.day)
    return base + timedelta(hours=hours)


def calculate(
    d: date,
    lat: float,
    lon: float,
    tz_offset_hours: float,
    method_id: str = DEFAULT_METHOD_ID,
    madhab: str = MADHAB_HANAFI,
) -> PrayerTimes:
    """Computes the 6 daily prayer clock times (as naive local datetimes)."""
    method = CALC_METHODS.get(method_id, CALC_METHODS[DEFAULT_METHOD_ID])
    asr_factor = ASR_FACTOR.get(madhab, 2.0)

    jd = _julian_date(d.year, d.month, d.day)

    def mid_day(time_frac: float) -> float:
        _, eqt = _sun_position(jd + time_frac)
        return _fixhour(12 - eqt)

    def sun_angle_time(angle: float, time_frac: float, ccw: bool = False) -> float:
        decl, _ = _sun_position(jd + time_frac)
        noon = mid_day(time_frac)
        denom = _dcos(decl) * _dcos(lat)
        if abs(denom) < 1e-9:
            t = 0.0
        else:
            ratio = (-_dsin(angle) - _dsin(decl) * _dsin(lat)) / denom
            if ratio < -1 or ratio > 1:
                # polar day/night edge case: no sunrise/sunset at this angle today.
                t = 0.0
            else:
                t = _darccos(ratio) / 15.0
        return noon - t if ccw else noon + t

    def asr_time(factor: float, time_frac: float) -> float:
        decl, _ = _sun_position(jd + time_frac)
        angle = -_darccot(factor + _dtan(abs(lat - decl)))
        return sun_angle_time(angle, time_frac)

    # default day-fraction guesses (praytimes.org convention)
    fajr_h = sun_angle_time(method.fajr_angle, 5.0 / 24.0, ccw=True)
    sunrise_h = sun_angle_time(0.833, 6.5 / 24.0, ccw=True)
    dhuhr_h = mid_day(12.0 / 24.0)
    asr_h = asr_time(asr_factor, 13.25 / 24.0)
    maghrib_h = sun_angle_time(method.maghrib_angle, 18.5 / 24.0)

    if method.isha_interval_min is not None:
        isha_h = _fixhour(maghrib_h + method.isha_interval_min / 60.0)
    else:
        isha_h = sun_angle_time(method.isha_angle or 18.0, 18.5 / 24.0)

    raw = {"fajr": fajr_h, "sunrise": sunrise_h, "dhuhr": dhuhr_h, "asr": asr_h,
           "maghrib": maghrib_h, "isha": isha_h}

    # convert from "solar apparent time referenced to this longitude" to the
    # requested civil timezone, then apply the method's per-prayer minute tweaks.
    final = {}
    for key, hours in raw.items():
        hours = hours + tz_offset_hours - lon / 15.0
        hours += method.adjustments.get(key, 0) / 60.0
        final[key] = _fixhour(hours)

    return PrayerTimes(**{k: _hours_to_time(d, v, tz_offset_hours) for k, v in final.items()})


def apply_manual_offsets(times: PrayerTimes, offsets: dict[str, int]) -> PrayerTimes:
    """Shifts each calculated time by a user-chosen +/- minute offset (default 0,
    i.e. the original astronomically-calculated time is used unless the user
    has explicitly adjusted it, e.g. to match a local mosque's announced time)."""
    d = times.as_dict()
    return PrayerTimes(**{
        k: v + timedelta(minutes=offsets.get(k, 0)) for k, v in d.items()
    })


def next_and_current_prayer(times: PrayerTimes, now: datetime) -> tuple[str | None, str | None]:
    """Returns (current_prayer_key, next_prayer_key). Salah-only (no sunrise)."""
    ordered = [("fajr", times.fajr), ("dhuhr", times.dhuhr), ("asr", times.asr),
               ("maghrib", times.maghrib), ("isha", times.isha)]
    current = None
    for key, t in ordered:
        if now >= t:
            current = key
        else:
            return current, key
    return "isha", None  # after isha: next is tomorrow's fajr (caller handles rollover)
