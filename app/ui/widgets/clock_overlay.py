"""A small always-on-top floating clock, draggable to any position, visible
even over other fullscreen apps (e.g. a presentation slideshow). Follows the
exact SpeedOverlay pattern (topmost reassertion via ctypes, drag handling) --
see speed_overlay.py.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.settings import settings

WINDOW_WIDTH = 128
WINDOW_HEIGHT = 34
UPDATE_MS = 1000

_HWND_TOPMOST = -1
_SWP_NOMOVE = 0x0002
_SWP_NOSIZE = 0x0001
_SWP_NOACTIVATE = 0x0010


def _force_topmost(hwnd: int) -> None:
    """Same reassertion trick as SpeedOverlay._force_topmost -- a plain
    WindowStaysOnTopHint widget can still lose the z-order fight against
    the taskbar or a fullscreen app, so this needs to run on a timer."""
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        set_window_pos = user32.SetWindowPos
        set_window_pos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, wintypes.UINT]
        set_window_pos.restype = wintypes.BOOL
        set_window_pos(hwnd, wintypes.HWND(_HWND_TOPMOST), 0, 0, 0, 0,
                       _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE)
    except OSError:
        pass


class ClockOverlay(QWidget):
    closed = Signal()  # emitted when the user closes it via its own X button

    def __init__(self, use_12h: bool = True) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self._use_12h = use_12h
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._drag_offset = QPoint()
        self._dragging = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.time_label = QLabel("--:--:--")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.time_label, 1)

        # floats over the top-right corner instead of living in the layout,
        # so it never eats into the space the time label centers itself in
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(11, 11)
        self.close_btn.setObjectName("ClockOverlayClose")
        self.close_btn.clicked.connect(self._on_close_clicked)
        self.close_btn.move(WINDOW_WIDTH - 11 - 3, 2)

        self.setStyleSheet(
            "QWidget { background-color: #1f1f1f; } "
            "QLabel { color: #ffffff; font-family: 'Segoe UI'; font-size: 10pt; "
            "font-weight: 600; background: transparent; } "
            "QPushButton#ClockOverlayClose { color: #cccccc; background: transparent; "
            "border: none; font-size: 6pt; } "
            "QPushButton#ClockOverlayClose:hover { color: #ffffff; }"
        )

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(UPDATE_MS)

        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._reassert_topmost)
        self._topmost_timer.start(2000)

        self._update_time()
        self._restore_position()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._reassert_topmost()

    def _reassert_topmost(self) -> None:
        _force_topmost(int(self.winId()))

    def _update_time(self) -> None:
        now = datetime.now()
        fmt = "%I:%M:%S %p" if self._use_12h else "%H:%M:%S"
        self.time_label.setText(now.strftime(fmt))

    def _restore_position(self) -> None:
        x, y = settings.clock_overlay_pos_x, settings.clock_overlay_pos_y
        if x >= 0 and y >= 0:
            self.move(x, y)
            return
        screen = self.screen()
        geo = screen.availableGeometry() if screen else None
        if geo is not None:
            self.move(geo.right() - WINDOW_WIDTH - 16, geo.top() + 16)

    def _save_position(self) -> None:
        pos = self.pos()
        settings.clock_overlay_pos_x = pos.x()
        settings.clock_overlay_pos_y = pos.y()

    def _on_close_clicked(self) -> None:
        settings.show_clock_overlay = False
        self.stop()
        self.closed.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self._dragging = False
            self._save_position()

    def stop(self) -> None:
        self._timer.stop()
        self._topmost_timer.stop()
        self.close()
