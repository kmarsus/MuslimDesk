"""Copies the running exe to a stable per-user location on first run, so the
originally-downloaded file (e.g. in Downloads) can be deleted afterwards
without breaking auto-start, shortcuts, or the Apps & Features entry -- all
of which point at wherever the app was running from when first launched."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

INSTALL_DIR = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "MuslimDesk"
INSTALLED_EXE = INSTALL_DIR / "MuslimDesk.exe"


def ensure_installed_and_relaunch() -> None:
    """No-op outside a frozen exe. Otherwise, if not already running from
    INSTALLED_EXE, copies itself there, relaunches from that copy, and exits
    the current process (raising SystemExit)."""
    if not getattr(sys, "frozen", False):
        return

    current = Path(sys.executable).resolve()
    try:
        if current.samefile(INSTALLED_EXE):
            return
    except (FileNotFoundError, OSError):
        pass

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(current, INSTALLED_EXE)
    except OSError:
        return  # e.g. locked/in-use -- keep running from the current location

    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen([str(INSTALLED_EXE)], close_fds=True, creationflags=flags)
    raise SystemExit


def schedule_install_dir_deletion() -> None:
    """Called from --uninstall: deletes the installed copy after this
    process exits (a running exe can't delete its own file directly)."""
    if not getattr(sys, "frozen", False):
        return
    exe_path = Path(sys.executable).resolve()
    if exe_path.parent != INSTALL_DIR.resolve():
        return  # not running from the stable install location -- nothing to clean up
    try:
        subprocess.Popen(
            f'timeout /t 1 /nobreak >nul & rmdir /s /q "{INSTALL_DIR}"',
            shell=True,
            close_fds=True,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError:
        pass
