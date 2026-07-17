"""Resolves bundled asset paths, both running from source and from a
PyInstaller-frozen exe (where data files live under sys._MEIPASS)."""
from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def assets_root() -> Path:
    return app_root() / "assets"


def data_path(*parts: str) -> Path:
    return assets_root() / "data" / Path(*parts)


def audio_path(*parts: str) -> Path:
    return assets_root() / "audio" / Path(*parts)


def font_path(*parts: str) -> Path:
    return assets_root() / "fonts" / Path(*parts)


def icon_path(*parts: str) -> Path:
    return assets_root() / "icons" / Path(*parts)


def user_data_dir() -> Path:
    """Writable per-user directory for cache/preferences (not inside the exe)."""
    import os
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    d = base / "MuslimDesk"
    d.mkdir(parents=True, exist_ok=True)
    return d
