"""Closes running web browsers -- used only by the opt-in (default OFF)
"close browsers when Azan starts" setting, and only after the user has
seen a cancellable on-screen countdown (see AzanNotificationDialog).

Uses terminate() (a graceful close request, same as clicking the window's
close button) rather than kill(), so each browser gets a chance to run its
own shutdown/save-session handling.
"""
from __future__ import annotations

import psutil

BROWSER_PROCESS_NAMES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe",
    "opera.exe", "opera_gx.exe", "iexplore.exe", "vivaldi.exe",
}


def running_browser_count() -> int:
    count = 0
    for proc in psutil.process_iter(["name"]):
        try:
            if (proc.info["name"] or "").lower() in BROWSER_PROCESS_NAMES:
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return count


def close_all_browsers() -> int:
    """Sends a graceful terminate() to every running browser process.
    Returns how many processes were signalled."""
    signalled = 0
    for proc in psutil.process_iter(["name"]):
        try:
            if (proc.info["name"] or "").lower() in BROWSER_PROCESS_NAMES:
                proc.terminate()
                signalled += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return signalled
