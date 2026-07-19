"""Junk-file cleaning backend for the PC Clean tab -- pure logic, no Qt
imports, so it's testable standalone. Every function here only ever touches
a single well-known cache/temp path; none of them recurse into arbitrary
user-chosen folders, and every deletion is wrapped so a locked file (browser
still open, etc.) is skipped rather than crashing the cleaner.
"""
from __future__ import annotations

import ctypes
import glob
import os


def _dir_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


def _clear_dir_contents(path: str) -> int:
    """Deletes everything *inside* path, but never path itself -- returns
    bytes freed. Locked files/folders are skipped, not fatal."""
    if not os.path.isdir(path):
        return 0
    freed = _dir_size(path)
    for entry in os.scandir(path):
        try:
            if entry.is_dir(follow_symlinks=False):
                _remove_tree(entry.path)
            else:
                os.remove(entry.path)
        except OSError:
            pass
    return freed


def _remove_tree(path: str) -> None:
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except OSError:
                pass
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except OSError:
                pass
    try:
        os.rmdir(path)
    except OSError:
        pass


def clean_windows_temp() -> int:
    """Clears the contents of %TEMP% (not the folder itself)."""
    temp_dir = os.environ.get("TEMP")
    if not temp_dir:
        return 0
    return _clear_dir_contents(temp_dir)


def _chrome_cache_dir() -> str:
    local = os.environ.get("LOCALAPPDATA", "")
    return os.path.join(local, "Google", "Chrome", "User Data", "Default", "Cache")


def _edge_cache_dir() -> str:
    local = os.environ.get("LOCALAPPDATA", "")
    return os.path.join(local, "Microsoft", "Edge", "User Data", "Default", "Cache")


def _firefox_cache_dirs() -> list[str]:
    appdata = os.environ.get("APPDATA", "")
    pattern = os.path.join(appdata, "Mozilla", "Firefox", "Profiles", "*.default*", "cache2")
    return glob.glob(pattern)


def chrome_cache_exists() -> bool:
    return os.path.isdir(_chrome_cache_dir())


def edge_cache_exists() -> bool:
    return os.path.isdir(_edge_cache_dir())


def firefox_cache_exists() -> bool:
    return len(_firefox_cache_dirs()) > 0


def clean_chrome_cache() -> int:
    """Only ever touches the Cache subfolder -- never the parent profile
    folder, which holds bookmarks, saved passwords, and history."""
    return _clear_dir_contents(_chrome_cache_dir())


def clean_edge_cache() -> int:
    return _clear_dir_contents(_edge_cache_dir())


def clean_firefox_cache() -> int:
    freed = 0
    for cache_dir in _firefox_cache_dirs():
        freed += _clear_dir_contents(cache_dir)
    return freed


def format_bytes(n: int) -> str:
    if n >= 1024 ** 3:
        return f"{n / 1024 ** 3:.2f} GB"
    if n >= 1024 ** 2:
        return f"{n / 1024 ** 2:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def empty_recycle_bin() -> None:
    """Semi-irreversible -- callers must gate this behind its own explicit
    confirmation, never bundle it into a generic "clean everything" action."""
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI = 0x00000002
    SHERB_NOSOUND = 0x00000004
    flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
