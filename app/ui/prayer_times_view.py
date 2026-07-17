from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.i18n import translator
from app.location import current_location
from app.ui.widgets.card import Card


class PrayerTimesView(QWidget):
    """Read-only display of today's prayer times. All configuration
    (location, calculation method, manual adjustment, azan voices) lives
    under Settings."""

    def __init__(self, scheduler, navigate, parent=None) -> None:
        super().__init__(parent)
        self._scheduler = scheduler
        self._navigate = navigate

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(16)

        header_row = QHBoxLayout()
        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        header_row.addWidget(self.heading)
        header_row.addStretch(1)
        self.loc_label = QLabel()
        self.loc_label.setObjectName("Muted")
        header_row.addWidget(self.loc_label)
        self._layout.addLayout(header_row)

        self.times_grid = QGridLayout()
        self.times_grid.setSpacing(10)
        self._layout.addLayout(self.times_grid)
        self._value_labels: dict[str, QLabel] = {}
        self._refresh_times_grid()

        settings_row = QHBoxLayout()
        self.settings_btn = QPushButton()
        self.settings_btn.clicked.connect(lambda: self._navigate("settings"))
        settings_row.addWidget(self.settings_btn)
        settings_row.addStretch(1)
        self._layout.addLayout(settings_row)
        self._layout.addStretch(1)

        self._scheduler.times_recomputed.connect(lambda *_: self._refresh_times_grid())
        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _refresh_times_grid(self) -> None:
        while self.times_grid.count():
            item = self.times_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._value_labels.clear()

        times = self._scheduler.times
        keys = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
        for i, key in enumerate(keys):
            card = Card(margins=14, spacing=4)
            name = QLabel(translator.t(f"prayer_{key}"))
            name.setObjectName("SubHeading")
            value = QLabel("--:--")
            value.setStyleSheet("font-size: 20px; font-weight: 800;")
            card.addWidget(name)
            card.addWidget(value)
            self.times_grid.addWidget(card, i // 3, i % 3)
            self._value_labels[key] = value
        if times is not None:
            for key, label in self._value_labels.items():
                label.setText(times.as_dict()[key].strftime("%I:%M %p"))

        loc = current_location()
        name = loc.display_name_en if translator.lang == "en" else loc.display_name_bn
        self.loc_label.setText(f"📍 {name}")

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_prayer_times"))
        self.settings_btn.setText("⚙ " + translator.t("nav_settings"))
        self._refresh_times_grid()
