"""Resolves the active lat/lon/timezone/display-name from user settings.

Two ways to set a location:
- "city": country dropdown -> city dropdown. Bangladesh uses the richer,
  Bangla-named cities_bd.json; every other country uses the offline
  world_cities.json (generated from geonamescache, 244 countries/3200
  cities, no network needed). The UTC offset is computed live from each
  city's IANA timezone (DST-aware) via zoneinfo.
- "manual": desktop user (no GPS) enters lat/lon/UTC-offset directly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

from app.paths import data_path
from app.settings import settings

BD_TZ_OFFSET = 6.0
BD_TIMEZONE = "Asia/Dhaka"


@dataclass(frozen=True)
class ResolvedLocation:
    lat: float
    lon: float
    tz_offset: float
    display_name_en: str
    display_name_bn: str


@lru_cache(maxsize=1)
def _bd_cities() -> list[dict]:
    return json.loads(data_path("cities_bd.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _world_countries() -> dict:
    return json.loads(data_path("world_cities.json").read_text(encoding="utf-8"))


def city_list() -> list[dict]:
    """Legacy alias: the Bangladesh city list (kept for any old callers)."""
    return _bd_cities()


def country_list() -> list[dict]:
    """[{code, name}], sorted, Bangladesh pinned first since it's the common case."""
    countries = [{"code": code, "name": c["name"]} for code, c in _world_countries().items()]
    countries.sort(key=lambda c: (c["code"] != "BD", c["name"]))
    return countries


def cities_for_country(code: str) -> list[dict]:
    """[{name, name_local, lat, lon, timezone}] for the given country code."""
    if code == "BD":
        return [
            {"name": c["key"], "name_local": c["name_bn"], "lat": c["lat"], "lon": c["lon"], "timezone": BD_TIMEZONE}
            for c in _bd_cities()
        ]
    country = _world_countries().get(code)
    if not country:
        return []
    return [
        {"name": c["name"], "name_local": c["name"], "lat": c["lat"], "lon": c["lon"], "timezone": c["timezone"]}
        for c in country["cities"]
    ]


def _tz_offset_hours(tz_name: str) -> float:
    try:
        offset = datetime.now(ZoneInfo(tz_name)).utcoffset()
        return offset.total_seconds() / 3600.0 if offset is not None else 0.0
    except Exception:
        return BD_TZ_OFFSET


def current_location() -> ResolvedLocation:
    if settings.location_mode == "manual":
        return ResolvedLocation(
            lat=settings.manual_lat,
            lon=settings.manual_lon,
            tz_offset=settings.manual_tz_offset,
            display_name_en=settings.manual_label,
            display_name_bn=settings.manual_label,
        )

    code = settings.country_code or "BD"
    name = settings.city_key
    for c in cities_for_country(code):
        if c["name"] == name:
            tz_offset = BD_TZ_OFFSET if code == "BD" else _tz_offset_hours(c["timezone"])
            return ResolvedLocation(c["lat"], c["lon"], tz_offset, c["name"], c["name_local"])

    # fallback: Dhaka
    return ResolvedLocation(23.8103, 90.4125, BD_TZ_OFFSET, "Dhaka", "ঢাকা")
