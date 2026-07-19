"""Shown when a prayer's Azan starts: an always-on-top, centered notification
reminding the user to pause and prepare for Salah. If the user has opted
into "close browsers when Azan starts" (default off), this also runs that
countdown -- the browsers are never closed silently, always with a visible
Cancel / Close Now choice first.
"""
from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                                QSlider, QVBoxLayout)

from app.browser_control import close_all_browsers, running_browser_count
from app.i18n import translator
from app.settings import settings


class AzanNotificationDialog(QDialog):
    def __init__(self, prayer_key: str, scheduler=None, parent=None) -> None:
        super().__init__(parent)
        self._browsers_closed = False
        self._scheduler = scheduler

        self.setWindowTitle(translator.t("azan_playing_title"))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        icon = QLabel("🕌")
        icon.setStyleSheet("font-size: 40px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        self.prayer_label = QLabel(translator.t(f"prayer_{prayer_key}"))
        self.prayer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prayer_label.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(self.prayer_label)

        message = settings.azan_custom_message.strip() or translator.t("azan_reminder_text")
        self.reminder_label = QLabel(message)
        self.reminder_label.setWordWrap(True)
        self.reminder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.reminder_label)

        self.hadith_label = QLabel(f'"{translator.t("azan_hadith_text")}"')
        self.hadith_label.setWordWrap(True)
        self.hadith_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hadith_label.setStyleSheet("font-style: italic;")
        layout.addWidget(self.hadith_label)

        self.hadith_ref_label = QLabel(translator.t("azan_hadith_ref"))
        self.hadith_ref_label.setObjectName("Muted")
        self.hadith_ref_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.hadith_ref_label)

        if scheduler is not None:
            volume_row = QHBoxLayout()
            volume_row.addWidget(QLabel("🔉"))
            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(max(0, min(100, settings.azan_volume)))
            self.volume_slider.valueChanged.connect(self._on_volume_changed)
            volume_row.addWidget(self.volume_slider, 1)
            volume_row.addWidget(QLabel("🔊"))
            layout.addLayout(volume_row)

            self.volume_hint_label = QLabel(translator.t("azan_volume_temp_hint"))
            self.volume_hint_label.setObjectName("Muted")
            self.volume_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.volume_hint_label)

        btn_row = QHBoxLayout()
        self.minimize_btn = QPushButton(translator.t("minimize"))
        self.minimize_btn.setObjectName("Ghost")
        self.minimize_btn.clicked.connect(self.hide)
        self.close_btn = QPushButton(translator.t("close"))
        self.close_btn.clicked.connect(self.close)
        btn_row.addWidget(self.minimize_btn)
        btn_row.addWidget(self.close_btn)
        layout.addLayout(btn_row)

        self._browser_seconds_left = settings.close_browsers_delay_sec
        if settings.close_browsers_on_azan and running_browser_count() > 0:
            self.browser_label = QLabel()
            self.browser_label.setObjectName("Muted")
            self.browser_label.setWordWrap(True)
            layout.addWidget(self.browser_label)

            browser_btn_row = QHBoxLayout()
            self.cancel_close_btn = QPushButton(translator.t("cancel"))
            self.cancel_close_btn.setObjectName("Ghost")
            self.cancel_close_btn.clicked.connect(self._cancel_browser_close)
            self.close_now_btn = QPushButton(translator.t("close_now"))
            self.close_now_btn.clicked.connect(self._close_browsers_now)
            browser_btn_row.addWidget(self.cancel_close_btn)
            browser_btn_row.addWidget(self.close_now_btn)
            layout.addLayout(browser_btn_row)

            self._browser_timer = QTimer(self)
            self._browser_timer.timeout.connect(self._tick_browser_countdown)
            self._browser_timer.start(1000)
            self._tick_browser_countdown(first=True)

    def _on_volume_changed(self, value: int) -> None:
        if self._scheduler is not None:
            self._scheduler.set_live_volume(value)

    def _tick_browser_countdown(self, first: bool = False) -> None:
        if not first:
            self._browser_seconds_left -= 1
        self.browser_label.setText(
            translator.t("closing_browsers_countdown", seconds=max(0, self._browser_seconds_left))
        )
        if self._browser_seconds_left <= 0:
            self._browser_timer.stop()
            self._close_browsers_now()

    def _cancel_browser_close(self) -> None:
        if hasattr(self, "_browser_timer"):
            self._browser_timer.stop()
        self.browser_label.setText(translator.t("shutdown_cancelled"))
        self.cancel_close_btn.setEnabled(False)
        self.close_now_btn.setEnabled(False)

    def _close_browsers_now(self) -> None:
        if self._browsers_closed:
            return
        self._browsers_closed = True
        if hasattr(self, "_browser_timer"):
            self._browser_timer.stop()
        close_all_browsers()
        self.browser_label.setText(translator.t("close_now"))
        self.cancel_close_btn.setEnabled(False)
        self.close_now_btn.setEnabled(False)
