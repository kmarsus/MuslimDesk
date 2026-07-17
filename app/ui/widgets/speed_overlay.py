"""A small always-on-top readout docked next to the Windows taskbar tray,
showing live upload/download speed. Ported from the standalone SpeedTray
utility onto Qt (a Tkinter mainloop can't coexist with Qt's), ctypes/Win32
calls unchanged.
"""
from __future__ import annotations

import time

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QMouseEvent
from PySide6.QtWidgets import QLabel, QMenu, QVBoxLayout, QWidget

from app.network_speed import NetworkCounters, default_position, format_rate, taskbar_colors

WINDOW_WIDTH = 128
WINDOW_HEIGHT = 40
UPDATE_MS = 1000


class SpeedOverlay(QWidget):
    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._counters = NetworkCounters()
        try:
            self._previous = self._counters.read()
        except OSError:
            self._previous = {}
        self._previous_time = time.perf_counter()
        self._drag_offset = QPoint()
        self._dragging = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(0)
        self.up_label = QLabel("↑: 0.0 Kb/s")
        self.down_label = QLabel("↓: 0.0 Kb/s")
        for lbl in (self.up_label, self.down_label):
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(lbl)

        self._bg, self._fg = "#1f1f1f", "#ffffff"
        self._apply_colors()

        self._menu = QMenu(self)
        reset_action = QAction("Reset position", self)
        reset_action.triggered.connect(self.reset_position)
        self._menu.addAction(reset_action)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_speed)
        self._timer.start(UPDATE_MS)

        self._theme_timer = QTimer(self)
        self._theme_timer.timeout.connect(self._refresh_theme)
        self._theme_timer.start(3000)

        self.reset_position()

    def _apply_colors(self) -> None:
        self.setStyleSheet(
            f"QWidget {{ background-color: {self._bg}; }} "
            f"QLabel {{ color: {self._fg}; font-family: 'Segoe UI'; font-size: 9pt; background: transparent; }}"
        )

    def _refresh_theme(self) -> None:
        bg, fg = taskbar_colors()
        if (bg, fg) != (self._bg, self._fg):
            self._bg, self._fg = bg, fg
            self._apply_colors()

    def reset_position(self) -> None:
        x, y = default_position(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.move(x, y)

    def _update_speed(self) -> None:
        try:
            now = time.perf_counter()
            current = self._counters.read()
            elapsed = max(now - self._previous_time, 0.001)
            downloaded = uploaded = 0
            for interface, (received, sent) in current.items():
                old = self._previous.get(interface)
                if old:
                    downloaded += max(0, received - old[0])
                    uploaded += max(0, sent - old[1])
            self.up_label.setText(f"↑: {format_rate(uploaded / elapsed)}")
            self.down_label.setText(f"↓: {format_rate(downloaded / elapsed)}")
            self._previous = current
            self._previous_time = now
        except OSError:
            self.up_label.setText("↑: --")
            self.down_label.setText("↓: --")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self._menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging = False

    def stop(self) -> None:
        self._timer.stop()
        self._theme_timer.stop()
        self.close()
