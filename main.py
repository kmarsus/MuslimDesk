"""MuslimDesk -- Windows desktop companion to the IOM Daily Azkar Android app.

Daily azkar, 5x daily azan (background-scheduled, offline astronomical
calculation), Quran, Asmaul Husna, Hijri calendar, Qibla direction, and a
tasbih counter, running from the system tray.
"""
from __future__ import annotations

import sys

from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from app.alarm_manager import AlarmManager
from app.autostart import (ensure_autostart_registered,
                            ensure_uninstall_entry_registered,
                            remove_windows_integration)
from app.azan_scheduler import AzanScheduler
from app.i18n import translator
from app.paths import assets_root, icon_path
from app.settings import settings
from app.ui.main_window import MainWindow
from app.ui.widgets.alarm_ring_dialog import AlarmRingDialog
from app.ui.widgets.azan_notification_dialog import AzanNotificationDialog
from app.ui.widgets.speed_overlay import SpeedOverlay
from app.voice_clock import VoiceClock


_ARABIC_FONT_FILES = ["Amiri-Regular.ttf", "ScheherazadeNew-Regular.ttf", "IndoPak.ttf", "Uthmanic.otf"]

# Common Windows-installed fonts worth offering alongside the bundled Arabic
# ones -- only added if actually present on this machine (QFontDatabase
# reports what's really installed, so this degrades gracefully elsewhere).
_COMMON_SYSTEM_FONTS = [
    "Segoe UI", "Arial", "Calibri", "Tahoma", "Times New Roman", "Georgia", "Verdana",
]


def _load_fonts() -> tuple[list[str], list[str]]:
    """Registers every bundled font and returns (all_families, selectable_font_choices)."""
    all_families: list[str] = []
    arabic_families: list[str] = []
    fonts_dir = assets_root() / "fonts"
    if fonts_dir.exists():
        for f in sorted(fonts_dir.glob("*")):
            if f.suffix.lower() not in (".ttf", ".otf"):
                continue
            font_id = QFontDatabase.addApplicationFont(str(f))
            if font_id == -1:
                continue
            fams = QFontDatabase.applicationFontFamilies(font_id)
            for fam in fams:
                if fam not in all_families:
                    all_families.append(fam)
            if f.name in _ARABIC_FONT_FILES and fams:
                if fams[0] not in arabic_families:
                    arabic_families.append(fams[0])

    installed = set(QFontDatabase.families())
    for fam in _COMMON_SYSTEM_FONTS:
        if fam in installed and fam not in arabic_families:
            arabic_families.append(fam)

    return all_families, arabic_families


def _run_uninstall() -> int:
    """Entry point for Apps & Features -> Uninstall (registered as
    `"<exe>" --uninstall` in ensure_uninstall_entry_registered())."""
    remove_windows_integration()
    app = QApplication(sys.argv)
    QMessageBox.information(
        None, "MuslimDesk",
        "MuslimDesk has been uninstalled: it will no longer start with Windows "
        "and has been removed from Apps & Features.\n\n"
        "You can now delete MuslimDesk.exe.",
    )
    return 0


def main() -> int:
    if "--uninstall" in sys.argv:
        return _run_uninstall()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("MuslimDesk")

    ensure_autostart_registered()
    ensure_uninstall_entry_registered()

    _all_families, available_arabic_fonts = _load_fonts()
    if not available_arabic_fonts:
        available_arabic_fonts = ["Amiri"]

    translator.set_language(settings.language)

    scheduler = AzanScheduler()
    alarm_manager = AlarmManager()
    voice_clock = VoiceClock()

    _speed_overlay: SpeedOverlay | None = None

    def _set_speed_tray_visible(enabled: bool) -> None:
        nonlocal _speed_overlay
        if enabled:
            if _speed_overlay is None:
                _speed_overlay = SpeedOverlay()
            _speed_overlay.show()
        elif _speed_overlay is not None:
            _speed_overlay.stop()
            _speed_overlay = None

    window = MainWindow(scheduler, alarm_manager, available_arabic_fonts,
                         on_speed_tray_changed=_set_speed_tray_visible, voice_clock=voice_clock)

    if settings.show_speed_tray:
        _set_speed_tray_visible(True)

    _ring_dialogs: list[AlarmRingDialog] = []

    def _on_alarm_fired(alarm) -> None:
        window.show()
        window.raise_()
        window.activateWindow()
        dialog = AlarmRingDialog(alarm, parent=window)
        _ring_dialogs.append(dialog)
        dialog.finished.connect(lambda *_: _ring_dialogs.remove(dialog) if dialog in _ring_dialogs else None)
        dialog.show()

    alarm_manager.alarm_fired.connect(_on_alarm_fired)

    _azan_dialogs: list[AzanNotificationDialog] = []

    def _on_prayer_fired(prayer_key: str, sound_played: bool) -> None:
        if not sound_played:
            return
        window.show()
        window.raise_()
        window.activateWindow()
        dialog = AzanNotificationDialog(prayer_key, parent=window)
        _azan_dialogs.append(dialog)
        dialog.finished.connect(lambda *_: _azan_dialogs.remove(dialog) if dialog in _azan_dialogs else None)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    scheduler.prayer_fired.connect(_on_prayer_fired)

    icon_file = icon_path("logo.png")
    tray_icon = QSystemTrayIcon(QIcon(str(icon_file)) if icon_file.exists() else QIcon(), app)
    tray_icon.setToolTip("MuslimDesk")
    menu = QMenu()
    show_action = menu.addAction(translator.t("tray_show"))
    show_action.triggered.connect(lambda: (window.show(), window.raise_(), window.activateWindow()))
    tray_icon.setContextMenu(menu)
    tray_icon.activated.connect(
        lambda reason: (window.show(), window.raise_(), window.activateWindow())
        if reason == QSystemTrayIcon.ActivationReason.Trigger else None
    )

    def _retranslate_tray(*_args) -> None:
        show_action.setText(translator.t("tray_show"))

    translator.language_changed.connect(_retranslate_tray)

    window.set_tray_icon(tray_icon)
    scheduler.set_tray_icon(tray_icon)
    tray_icon.show()

    if not settings.start_minimized:
        window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
