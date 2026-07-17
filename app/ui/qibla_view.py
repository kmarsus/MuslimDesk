from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.i18n import translator
from app.location import current_location
from app.qibla import bearing_to_kaaba, distance_to_kaaba_km
from app.ui.widgets.card import Card


class _CompassWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self._bearing = 0.0

    def set_bearing(self, degrees: float) -> None:
        self._bearing = degrees
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 20
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        center = rect.center()
        radius = side / 2

        painter.setPen(QPen(QColor("#42A866"), 3))
        painter.setBrush(QBrush(QColor(255, 255, 255, 0)))
        painter.drawEllipse(rect)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        for label, angle in [("N", 0), ("E", 90), ("S", 180), ("W", 270)]:
            rad = math.radians(angle - 90)
            x = center.x() + (radius - 16) * math.cos(rad)
            y = center.y() + (radius - 16) * math.sin(rad)
            painter.drawText(QRectF(x - 10, y - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, label)

        rad = math.radians(self._bearing - 90)
        tip = QPointF(center.x() + radius * 0.82 * math.cos(rad), center.y() + radius * 0.82 * math.sin(rad))
        left = QPointF(center.x() + radius * 0.12 * math.cos(rad + 2.6), center.y() + radius * 0.12 * math.sin(rad + 2.6))
        right = QPointF(center.x() + radius * 0.12 * math.cos(rad - 2.6), center.y() + radius * 0.12 * math.sin(rad - 2.6))
        painter.setBrush(QBrush(QColor("#FF8B73")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([tip, left, right]))
        painter.setBrush(QBrush(QColor("#0B2C4D")))
        painter.drawEllipse(center, 6, 6)


class QiblaView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.card = Card(margins=24, spacing=12)
        self.compass = _CompassWidget()
        self.card.addWidget(self.compass)
        self.bearing_label = QLabel()
        self.bearing_label.setObjectName("PrayerName")
        self.bearing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(self.bearing_label)
        self.bearing_caption = QLabel()
        self.bearing_caption.setObjectName("Muted")
        self.bearing_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(self.bearing_caption)
        self.distance_label = QLabel()
        self.distance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(self.distance_label)
        self.note_label = QLabel()
        self.note_label.setWordWrap(True)
        self.note_label.setObjectName("Muted")
        self.card.addWidget(self.note_label)
        layout.addWidget(self.card)
        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def refresh(self) -> None:
        loc = current_location()
        bearing = bearing_to_kaaba(loc.lat, loc.lon)
        distance = distance_to_kaaba_km(loc.lat, loc.lon)
        self.compass.set_bearing(bearing)
        self.bearing_label.setText(f"{bearing:.1f}°")
        self.distance_label.setText(f"{distance:,.0f} km")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh()

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_qibla"))
        self.bearing_caption.setText(translator.t("qibla_bearing"))
        self.note_label.setText(translator.t("qibla_note"))
        self.refresh()
