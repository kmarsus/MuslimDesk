from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QListWidget,
                                QListWidgetItem, QPushButton, QScrollArea,
                                QVBoxLayout, QWidget)

from app.hijri import HijriCalendarService, month_name
from app.i18n import translator
from app.settings import settings
from app.ui.widgets.card import Card
from app.ui.widgets.no_scroll import NoScrollSpinBox

_WEEKDAY_EN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
_WEEKDAY_BN = ["রবি", "সোম", "মঙ্গল", "বুধ", "বৃহঃ", "শুক্র", "শনি"]
_FRIDAY_COL = 5     # weekly holiday in Bangladesh
_SIYAM_COLS = (1, 4)  # Monday & Thursday -- recommended (sunnah) voluntary fasting days

_GRID_BORDER = "#E5EEF7"
_TODAY_BG = "#42A866"
_HOLIDAY_BG = "#FDEAE4"
_HOLIDAY_FG = "#C1503A"
_SIYAM_BG = "#FFF3D6"
_SIYAM_FG = "#8A6414"
_EVENT_FG = "#FF8B73"


class HijriView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._svc = HijriCalendarService()
        today = self._svc.today(settings.hijri_offset)
        self._view_year = today.year
        self._view_month = today.month

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("Ghost")
        self.prev_btn.clicked.connect(self._prev_month)
        self.month_label = QLabel()
        self.month_label.setObjectName("SectionTitle")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("Ghost")
        self.next_btn.clicked.connect(self._next_month)
        self.today_btn = QPushButton()
        self.today_btn.setObjectName("Ghost")
        self.today_btn.clicked.connect(self._go_today)
        nav_row.addWidget(self.prev_btn)
        nav_row.addWidget(self.month_label, 1)
        nav_row.addWidget(self.next_btn)
        nav_row.addWidget(self.today_btn)
        layout.addLayout(nav_row)

        self.grid_card = Card(margins=1, spacing=0)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid_card.addLayout(self.grid)
        layout.addWidget(self.grid_card)

        legend_row = QHBoxLayout()
        self.legend_holiday = QLabel()
        self.legend_holiday.setStyleSheet(f"color: {_HOLIDAY_FG}; font-size: 10px; font-weight: 700;")
        self.legend_siyam = QLabel()
        self.legend_siyam.setStyleSheet(f"color: {_SIYAM_FG}; font-size: 10px; font-weight: 700;")
        self.legend_event = QLabel()
        self.legend_event.setStyleSheet(f"color: {_EVENT_FG}; font-size: 10px; font-weight: 700;")
        legend_row.addWidget(self.legend_holiday)
        legend_row.addWidget(self.legend_siyam)
        legend_row.addWidget(self.legend_event)
        legend_row.addStretch(1)
        layout.addLayout(legend_row)

        offset_row = QHBoxLayout()
        self.offset_label = QLabel()
        offset_row.addWidget(self.offset_label)
        self.offset_spin = NoScrollSpinBox()
        self.offset_spin.setRange(-3, 3)
        self.offset_spin.setValue(settings.hijri_offset)
        self.offset_spin.valueChanged.connect(self._set_offset)
        offset_row.addWidget(self.offset_spin)
        offset_row.addStretch(1)
        layout.addLayout(offset_row)

        self.upcoming_title = QLabel()
        self.upcoming_title.setObjectName("SectionTitle")
        layout.addWidget(self.upcoming_title)
        self.upcoming_list = QListWidget()
        self.upcoming_list.setMaximumHeight(220)
        layout.addWidget(self.upcoming_list)
        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _set_offset(self, v: int) -> None:
        settings.hijri_offset = v
        self._refresh()

    def _prev_month(self) -> None:
        self._view_month -= 1
        if self._view_month < 1:
            self._view_month = 12
            self._view_year -= 1
        self._refresh()

    def _next_month(self) -> None:
        self._view_month += 1
        if self._view_month > 12:
            self._view_month = 1
            self._view_year += 1
        self._refresh()

    def _go_today(self) -> None:
        today = self._svc.today(settings.hijri_offset)
        self._view_year, self._view_month = today.year, today.month
        self._refresh()

    def _refresh(self) -> None:
        english = translator.lang == "en"
        weekday_names = _WEEKDAY_EN if english else _WEEKDAY_BN

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for col, wd in enumerate(weekday_names):
            lbl = QLabel(wd)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumSize(52, 30)
            border = f"border: 1px solid {_GRID_BORDER};"
            if col == _FRIDAY_COL:
                lbl.setStyleSheet(f"background-color: {_HOLIDAY_BG}; color: {_HOLIDAY_FG}; font-weight: 800; {border}")
            elif col in _SIYAM_COLS:
                lbl.setStyleSheet(f"background-color: {_SIYAM_BG}; color: {_SIYAM_FG}; font-weight: 800; {border}")
            else:
                lbl.setStyleSheet(f"font-weight: 800; {border}")
            self.grid.addWidget(lbl, 0, col)

        first_weekday = self._svc.weekday_of_first_day(self._view_year, self._view_month, settings.hijri_offset)
        days_in_month = self._svc.days_in_month(self._view_year, self._view_month)
        today = self._svc.today(settings.hijri_offset)

        row, col = 1, first_weekday
        for day in range(1, days_in_month + 1):
            events = self._svc.events_on(self._view_month, day)
            is_today = (self._view_year == today.year and self._view_month == today.month and day == today.day)
            is_friday = col == _FRIDAY_COL
            is_siyam = col in _SIYAM_COLS

            text = str(day)
            if events:
                text += "\n●"
            elif is_siyam:
                text += "\n" + translator.t("siyam_short")

            cell = QLabel(text)
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setMinimumSize(52, 44)

            if is_today:
                style = f"background-color: {_TODAY_BG}; color: white; font-weight: 800;"
            elif is_friday:
                style = f"background-color: {_HOLIDAY_BG}; color: {_HOLIDAY_FG}; font-weight: 700;"
            elif is_siyam:
                style = f"background-color: {_SIYAM_BG}; color: {_SIYAM_FG}; font-weight: 700;"
            else:
                style = "background-color: transparent;"
            if events and not is_today:
                style += f" color: {_EVENT_FG}; font-weight: 800;"
            style += f" border: 1px solid {_GRID_BORDER};"
            cell.setStyleSheet(style)

            tooltip_parts = [e.name(english) for e in events]
            if is_siyam and not events:
                tooltip_parts.append(translator.t("siyam_tooltip"))
            if tooltip_parts:
                cell.setToolTip(", ".join(tooltip_parts))

            self.grid.addWidget(cell, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

        self.month_label.setText(f"{month_name(self._view_month, english)} {self._view_year} AH")

        self.upcoming_list.clear()
        for u in self._svc.upcoming_events(settings.hijri_offset, limit=10):
            days_txt = translator.t("today_label") if u.days_remaining == 0 else translator.t("days_left", n=u.days_remaining)
            text = f"{u.event.name(english)} — {u.gregorian_date.strftime('%d %b %Y')} ({days_txt})"
            self.upcoming_list.addItem(QListWidgetItem(text))

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_hijri"))
        self.today_btn.setText(translator.t("hijri_today"))
        self.offset_label.setText(translator.t("hijri_offset_label"))
        self.upcoming_title.setText(translator.t("upcoming_events"))
        self.legend_holiday.setText("🟥 " + translator.t("legend_holiday"))
        self.legend_siyam.setText("🟨 " + translator.t("legend_siyam"))
        self.legend_event.setText("● " + translator.t("legend_event"))
        self._refresh()
