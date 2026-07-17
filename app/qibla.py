"""Great-circle bearing + distance from a location to the Kaaba."""
from __future__ import annotations

import math

KAABA_LAT = 21.4225
KAABA_LON = 39.8262
EARTH_RADIUS_KM = 6371.0


def bearing_to_kaaba(lat: float, lon: float) -> float:
    phi1, phi2 = math.radians(lat), math.radians(KAABA_LAT)
    d_lambda = math.radians(KAABA_LON - lon)
    x = math.sin(d_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    theta = math.degrees(math.atan2(x, y))
    return (theta + 360) % 360


def distance_to_kaaba_km(lat: float, lon: float) -> float:
    phi1, phi2 = math.radians(lat), math.radians(KAABA_LAT)
    d_phi = math.radians(KAABA_LAT - lat)
    d_lambda = math.radians(KAABA_LON - lon)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c
