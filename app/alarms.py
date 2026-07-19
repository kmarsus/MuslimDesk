"""Persisted alarm-clock entries, independent of prayer-time azan.

Stored as a small JSON file (not QSettings) since it's a list of records
rather than flat key/value preferences.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field

from app.paths import user_data_dir

ALARMS_FILE = user_data_dir() / "alarms.json"

WEEKDAY_LABELS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_LABELS_BN = ["সোম", "মঙ্গল", "বুধ", "বৃহঃ", "শুক্র", "শনি", "রবি"]


@dataclass
class Alarm:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    time: str = "06:00"  # "HH:MM", 24h
    label: str = ""
    enabled: bool = True
    weekdays: list[int] = field(default_factory=list)  # 0=Mon..6=Sun; empty = every day
    voice_id: str = "beep_classic"
    shutdown_on_ring: bool = False
    shutdown_delay_sec: int = 60

    def repeats_today(self, python_weekday: int) -> bool:
        """python_weekday: date.weekday() convention, 0=Monday..6=Sunday."""
        return not self.weekdays or python_weekday in self.weekdays

    @property
    def time_12h(self) -> str:
        """self.time is stored as 24h "HH:MM"; display it as 12h with AM/PM."""
        hour, minute = (int(x) for x in self.time.split(":"))
        period = "AM" if hour < 12 else "PM"
        hour12 = hour % 12 or 12
        return f"{hour12:02d}:{minute:02d} {period}"


def load_alarms() -> list[Alarm]:
    if not ALARMS_FILE.exists():
        return []
    try:
        raw = json.loads(ALARMS_FILE.read_text(encoding="utf-8"))
        return [Alarm(**a) for a in raw]
    except Exception:
        return []


def save_alarms(alarms: list[Alarm]) -> None:
    ALARMS_FILE.write_text(
        json.dumps([asdict(a) for a in alarms], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
