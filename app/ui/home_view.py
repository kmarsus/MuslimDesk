from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                                QScrollArea, QVBoxLayout, QWidget)

from app.hijri import HijriCalendarService, month_name
from app.i18n import translator
from app.location import current_location
from app.settings import settings
from app.ui.widgets.card import Card

FEATURE_GRID = [
    ("nav_prayer_times", "🕌"),
    ("nav_daily_azkar", "📿"),
    ("nav_quran", "📖"),
    ("nav_qibla", "🧭"),
    ("nav_hijri", "🌙"),
    ("nav_tasbih", "☪"),
]


class HomeView(QWidget):
    def __init__(self, scheduler, navigate, parent=None) -> None:
        super().__init__(parent)
        self._scheduler = scheduler
        self._navigate = navigate
        self._hijri = HijriCalendarService()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(18)

        self._build_hero()
        self._build_hijri_panel()
        self._build_times_row()
        self._build_feature_grid()
        self._layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._scheduler.times_recomputed.connect(lambda *_: self._refresh_times_row())
        translator.language_changed.connect(lambda *_: self.retranslate())
        self._tick()

    # ── hero ──────────────────────────────────────────────────────────
    def _build_hero(self) -> None:
        self.hero = Card("HeroCard")
        row = QHBoxLayout()
        self.loc_label = QLabel()
        self.loc_label.setObjectName("Muted")
        row.addWidget(self.loc_label)
        row.addStretch(1)
        self.lang_btn = QPushButton("EN / বাং")
        self.lang_btn.setObjectName("Ghost")
        self.lang_btn.clicked.connect(self._toggle_language)
        row.addWidget(self.lang_btn)
        self.hero.addLayout(row)

        self.current_prayer_label = QLabel()
        self.current_prayer_label.setObjectName("PrayerName")
        self.hero.addWidget(self.current_prayer_label)

        self.remaining_label = QLabel()
        self.remaining_label.setObjectName("Muted")
        self.hero.addWidget(self.remaining_label)

        self.date_label = QLabel()
        self.date_label.setObjectName("Muted")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.hero.addWidget(self.date_label)

        self._layout.addWidget(self.hero)

    def _toggle_language(self) -> None:
        new_lang = "en" if translator.lang == "bn" else "bn"
        settings.language = new_lang
        translator.set_language(new_lang)

    # ── hijri panel ──────────────────────────────────────────────────
    def _build_hijri_panel(self) -> None:
        self.hijri_card = Card()
        row = QHBoxLayout()
        self.hijri_label = QLabel()
        self.hijri_label.setObjectName("SectionTitle")
        row.addWidget(self.hijri_label)
        row.addStretch(1)
        self.hijri_card.addLayout(row)
        self._layout.addWidget(self.hijri_card)
        self.hijri_card.mousePressEvent = lambda e: self._navigate("hijri")

    # ── today's times row ────────────────────────────────────────────
    def _build_times_row(self) -> None:
        self.times_title = QLabel()
        self.times_title.setObjectName("SectionTitle")
        self._layout.addWidget(self.times_title)

        self.times_row = QHBoxLayout()
        self.times_row.setSpacing(10)
        self._layout.addLayout(self.times_row)
        self._time_value_labels: dict[str, QLabel] = {}
        self._refresh_times_row()

    def _refresh_times_row(self) -> None:
        while self.times_row.count():
            item = self.times_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._time_value_labels.clear()

        times = self._scheduler.times
        keys = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
        for key in keys:
            card = Card(margins=10, spacing=2)
            name = QLabel(translator.t(f"prayer_{key}"))
            name.setObjectName("Muted")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value = QLabel("--:--")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setStyleSheet("font-weight: 800; font-size: 14px;")
            card.addWidget(name)
            card.addWidget(value)
            self.times_row.addWidget(card)
            self._time_value_labels[key] = value

        if times is not None:
            for key, label in self._time_value_labels.items():
                label.setText(times.as_dict()[key].strftime("%I:%M %p"))

    # ── feature grid ─────────────────────────────────────────────────
    def _build_feature_grid(self) -> None:
        self.features_title = QLabel()
        self.features_title.setObjectName("SectionTitle")
        self._layout.addWidget(self.features_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        self._layout.addLayout(grid)
        self._feature_buttons = []
        for i, (key, emoji) in enumerate(FEATURE_GRID):
            btn = QPushButton(f"{emoji}  {translator.t(key)}")
            btn.setObjectName("Ghost")
            btn.setMinimumHeight(56)
            route = key.replace("nav_", "")
            btn.clicked.connect(lambda checked=False, r=route: self._navigate(r))
            grid.addWidget(btn, i // 3, i % 3)
            self._feature_buttons.append((btn, key, emoji))

    # ── periodic tick ────────────────────────────────────────────────
    def _tick(self) -> None:
        current, nxt, next_time = self._scheduler.current_and_next()
        now = datetime.now()

        cur_label = translator.t(f"prayer_{current}") if current else "--"
        self.current_prayer_label.setText(cur_label)

        if next_time is not None:
            remaining = next_time - now
            total_min = max(0, int(remaining.total_seconds() // 60))
            h, m = divmod(total_min, 60)
            remaining_str = (f"{h}h {m}m" if translator.lang == "en" else f"{h} ঘণ্টা {m} মিনিট")
            next_label = translator.t(f"prayer_{nxt}") if nxt else "--"
            self.remaining_label.setText(translator.t("next_prayer_in", remaining=remaining_str, next=next_label))
        else:
            self.remaining_label.setText("")

        self.date_label.setText(now.strftime("%A, %d %B %Y"))

        loc = current_location()
        name = loc.display_name_en if translator.lang == "en" else loc.display_name_bn
        self.loc_label.setText(f"📍 {name}")

        h = self._hijri.today(settings.hijri_offset)
        mname = month_name(h.month, translator.lang == "en")
        self.hijri_label.setText(f"{h.day} {mname} {h.year} AH")

    def retranslate(self) -> None:
        self.times_title.setText(translator.t("todays_prayer_times"))
        self.features_title.setText(translator.t("quick_actions"))
        self._refresh_times_row()
        for btn, key, emoji in self._feature_buttons:
            btn.setText(f"{emoji}  {translator.t(key)}")
        self._tick()
