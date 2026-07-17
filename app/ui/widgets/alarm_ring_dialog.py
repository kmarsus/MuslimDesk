"""Modal dialog shown when an alarm fires: plays a looping sound until the
user hits Stop, and -- only if the alarm was explicitly configured with
"shut down PC on ring" -- shows a cancellable countdown before invoking a
real Windows shutdown. The shutdown never happens silently: it always shows
this countdown with a Cancel button first.
"""
from __future__ import annotations

import subprocess

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from app import azan_voices
from app.alarms import Alarm
from app.i18n import translator


class AlarmRingDialog(QDialog):
    def __init__(self, alarm: Alarm, parent=None) -> None:
        super().__init__(parent)
        self._alarm = alarm
        self._shutdown_seconds_left = alarm.shutdown_delay_sec
        self._shutdown_cancelled = False

        self.setWindowTitle(translator.t("app_title"))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel(f"⏰  {alarm.label or translator.t('nav_alarm')}")
        title.setStyleSheet("font-size: 20px; font-weight: 800;")
        layout.addWidget(title)

        time_label = QLabel(alarm.time)
        time_label.setStyleSheet("font-size: 40px; font-weight: 800;")
        layout.addWidget(time_label)

        self.shutdown_label = QLabel()
        self.shutdown_label.setObjectName("Muted")
        layout.addWidget(self.shutdown_label)

        self.stop_btn = QPushButton(translator.t("stop"))
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.clicked.connect(self._stop)
        layout.addWidget(self.stop_btn)

        self.cancel_shutdown_btn = QPushButton(translator.t("cancel_shutdown"))
        self.cancel_shutdown_btn.setObjectName("Ghost")
        self.cancel_shutdown_btn.clicked.connect(self._cancel_shutdown)
        layout.addWidget(self.cancel_shutdown_btn)
        self.cancel_shutdown_btn.setVisible(alarm.shutdown_on_ring)
        self.shutdown_label.setVisible(alarm.shutdown_on_ring)

        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._player.setLoops(QMediaPlayer.Loops.Infinite)
        self._player.setSource(QUrl.fromLocalFile(azan_voices.resolve_path(alarm.voice_id)))
        self._player.play()

        if alarm.shutdown_on_ring:
            self._countdown_timer = QTimer(self)
            self._countdown_timer.timeout.connect(self._tick_countdown)
            self._countdown_timer.start(1000)
            self._tick_countdown(first=True)

    def _tick_countdown(self, first: bool = False) -> None:
        if not first:
            self._shutdown_seconds_left -= 1
        self.shutdown_label.setText(
            translator.t("shutdown_countdown", seconds=max(0, self._shutdown_seconds_left))
        )
        if self._shutdown_seconds_left <= 0:
            self._countdown_timer.stop()
            self._do_shutdown()

    def _cancel_shutdown(self) -> None:
        self._shutdown_cancelled = True
        if hasattr(self, "_countdown_timer"):
            self._countdown_timer.stop()
        self.shutdown_label.setText(translator.t("shutdown_cancelled"))
        self.cancel_shutdown_btn.setEnabled(False)

    def _do_shutdown(self) -> None:
        if self._shutdown_cancelled:
            return
        self._stop()
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
        except Exception:
            pass

    def _stop(self) -> None:
        self._player.stop()
        if hasattr(self, "_countdown_timer"):
            self._countdown_timer.stop()
        self.accept()

    def closeEvent(self, event) -> None:
        self._player.stop()
        if hasattr(self, "_countdown_timer"):
            self._countdown_timer.stop()
        super().closeEvent(event)
