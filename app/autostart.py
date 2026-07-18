"""Registers MuslimDesk to launch automatically at Windows sign-in (HKCU Run
key) and, for the packaged exe, a proper "Apps & Features" uninstall entry
plus Start Menu / Desktop shortcuts -- all per-user, no admin rights needed."""
from __future__ import annotations

import sys
import winreg
from pathlib import Path

APP_NAME = "MuslimDesk"
APP_VERSION = "1.0.3"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\MuslimDesk"


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
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


def _start_menu_shortcut_path() -> Path:
    import os
    return Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "MuslimDesk.lnk"


def _desktop_shortcut_path() -> Path:
    import os
    return Path(os.environ["USERPROFILE"]) / "Desktop" / "MuslimDesk.lnk"


def _create_shortcut(shortcut_path: Path, exe_path: Path) -> None:
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = str(exe_path)
        shortcut.WorkingDirectory = str(exe_path.parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()
    except Exception:
        pass


def _remove_shortcuts() -> None:
    for path in (_start_menu_shortcut_path(), _desktop_shortcut_path()):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def ensure_uninstall_entry_registered() -> None:
    """Registers MuslimDesk in Windows' "Apps & Features" (only meaningful
    for the packaged exe -- a dev/source run has nothing to point users at)
    so there's an actual uninstall path now that the tray has no Exit option."""
    if not getattr(sys, "frozen", False):
        return
    exe_path = Path(sys.executable)
    try:
        _create_shortcut(_start_menu_shortcut_path(), exe_path)
        _create_shortcut(_desktop_shortcut_path(), exe_path)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Khandaker Marsus")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(exe_path.parent))
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(exe_path))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{exe_path}" --uninstall')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            try:
                size_kb = exe_path.stat().st_size // 1024
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            except OSError:
                pass
    except OSError:
        pass


def remove_windows_integration() -> None:
    """Reverses ensure_autostart_registered() + ensure_uninstall_entry_registered()
    -- called when the user runs `MuslimDesk.exe --uninstall` from Apps & Features."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except OSError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY)
    except OSError:
        pass
    _remove_shortcuts()
