"""Registers MuslimDesk to launch automatically at Windows sign-in
(HKCU Run key -- no admin rights needed, applies to the current user only)."""
from __future__ import annotations

import sys
import winreg

APP_NAME = "MuslimDesk"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    from pathlib import Path
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    interpreter = pythonw if pythonw.exists() else Path(sys.executable)
    entry_point = Path(__file__).resolve().parent.parent / "main.py"
    return f'"{interpreter}" "{entry_point}"'


def ensure_autostart_registered() -> None:
    """Idempotently (re-)writes the Run key so the app keeps starting with
    Windows even if the key is ever cleared by an AV tool or manual edit."""
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())
    except OSError:
        pass
