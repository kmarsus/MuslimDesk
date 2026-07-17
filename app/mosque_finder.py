"""Nearby mosque lookup. Location comes from the laptop's IP (approximate --
desktops rarely have real GPS) with manual lat/lon as a fallback, and mosque
data comes from OpenStreetMap's public Overpass API (free, no key). Both are
optional, on-demand network calls -- the app's core features never depend
on them.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import requests

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
_HEADERS = {"User-Agent": "MuslimDesk/1.0 (desktop Islamic app; nearby-mosque lookup)"}


@dataclass(frozen=True)
class IpLocation:
    lat: float
    lon: float
    city: str
    country: str


@dataclass(frozen=True)
class Mosque:
    name: str
    lat: float
    lon: float
    distance_km: float


def detect_ip_location(timeout: float = 8.0) -> IpLocation | None:
    try:
        r = requests.get("http://ip-api.com/json/", timeout=timeout)
        r.raise_for_status()
        d = r.json()
        if d.get("status") != "success":
            return None
        return IpLocation(lat=d["lat"], lon=d["lon"], city=d.get("city", ""), country=d.get("country", ""))
    except Exception:
        return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearby_mosques(lat: float, lon: float, radius_m: int = 5000, timeout: float = 25.0) -> list[Mosque]:
    query = (
        "[out:json][timeout:20];"
        "("
        f'node["amenity"="place_of_worship"]["religion"="muslim"](around:{radius_m},{lat},{lon});'
        f'way["amenity"="place_of_worship"]["religion"="muslim"](around:{radius_m},{lat},{lon});'
        ");"
        "out center 40;"
    )
    last_error: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            r = requests.post(endpoint, data={"data": query}, headers=_HEADERS, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            results = []
            for el in data.get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en") or "Mosque"
                m_lat = el.get("lat") or el.get("center", {}).get("lat")
                m_lon = el.get("lon") or el.get("center", {}).get("lon")
                if m_lat is None or m_lon is None:
                    continue
                dist = _haversine_km(lat, lon, m_lat, m_lon)
                results.append(Mosque(name=name, lat=m_lat, lon=m_lon, distance_km=dist))
            results.sort(key=lambda m: m.distance_km)
            return results
        except Exception as e:
            last_error = e
            continue
    if last_error:
        raise last_error
    return []
