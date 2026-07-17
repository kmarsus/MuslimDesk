"""Loads Dua & Hadith content from a bundled offline snapshot.

This used to fetch live from the Android app's backend on every launch;
per product requirement, MuslimDesk's core features must work fully
independently of that (or any) website, so the content ships as a static
asset instead. Both languages are bundled -- switching language just
switches which file is read, no network involved.
"""
from __future__ import annotations

import json

from app.paths import data_path


def fetch_home_content(lang: str) -> dict:
    """Returns {'categories': [...], 'dua': [...], 'hadith': [...]} from the
    bundled offline snapshot for the given language ('bn' or 'en')."""
    path = data_path(f"dua_hadith_{lang}.json")
    if not path.exists():
        path = data_path("dua_hadith_bn.json")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"categories": [], "dua": [], "hadith": []}
