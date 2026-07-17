from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget,
                                QListWidgetItem, QPushButton, QScrollArea,
                                QSplitter, QTabWidget, QVBoxLayout, QWidget)

from app.azkar_count import format_count
from app.i18n import translator
from app.paths import data_path
from app.settings import settings
from app.ui.widgets.card import Card


def _load(name: str) -> list[dict]:
    return json.loads(data_path(name).read_text(encoding="utf-8"))


def _merged_entries(bn_file: str, en_file: str) -> list[dict]:
    """Bangla entries with an English title/reference/translation overlay
    matched by index (both files are generated from -- and stay aligned
    with -- the same source list)."""
    bn = _load(bn_file)
    try:
        en = _load(en_file)
    except FileNotFoundError:
        en = []
    merged = []
    for i, e in enumerate(bn):
        entry = dict(e)
        if i < len(en):
            entry["title_en"] = en[i].get("title", "")
            entry["reference_en"] = en[i].get("reference", "")
            entry["translation_en"] = en[i].get("translation", "")
        merged.append(entry)
    return merged


class _AzkarList(QWidget):
    """One tab: search box + list on the left, detail card on the right."""

    def __init__(self, entries: list[dict]) -> None:
        super().__init__()
        self._entries = entries
        self._filtered = entries

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        self.search = QLineEdit()
        self.search.textChanged.connect(self._filter)
        left_layout.addWidget(self.search)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._show_index)
        left_layout.addWidget(self.list_widget)
        splitter.addWidget(left)

        right = QScrollArea()
        right.setWidgetResizable(True)
        self.detail_card = Card(margins=20, spacing=10)
        right.setWidget(self.detail_card)
        splitter.addWidget(right)
        splitter.setSizes([260, 640])

        title_row = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("Heading")
        self.title_label.setWordWrap(True)
        title_row.addWidget(self.title_label, 1)
        self.count_badge = QLabel()
        self.count_badge.setStyleSheet(
            "background-color: rgba(66,168,102,0.15); color: #2E7D32; border-radius: 10px; "
            "padding: 4px 10px; font-weight: 700; font-size: 11px;"
        )
        title_row.addWidget(self.count_badge)
        self.detail_card.addLayout(title_row)

        self.arabic_label = QLabel()
        self.arabic_label.setObjectName("Arabic")
        self.arabic_label.setWordWrap(True)
        self.arabic_label.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.arabic_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.translit_label = QLabel()
        self.translit_label.setWordWrap(True)
        self.translation_label = QLabel()
        self.translation_label.setWordWrap(True)
        self.rules_title = QLabel()
        self.rules_title.setObjectName("SubHeading")
        self.rules_label = QLabel()
        self.rules_label.setWordWrap(True)
        self.ref_title = QLabel()
        self.ref_title.setObjectName("SubHeading")
        self.ref_label = QLabel()
        self.ref_label.setWordWrap(True)
        self.benefit_title = QLabel()
        self.benefit_title.setObjectName("SubHeading")
        self.benefit_label = QLabel()
        self.benefit_label.setWordWrap(True)
        for w in [self.arabic_label, self.translit_label,
                  self.translation_label, self.rules_title, self.rules_label,
                  self.ref_title, self.ref_label, self.benefit_title, self.benefit_label]:
            self.detail_card.addWidget(w)

        next_row = QHBoxLayout()
        next_row.addStretch(1)
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self._go_next)
        next_row.addWidget(self.next_btn)
        self.detail_card.addLayout(next_row)

        self._populate_list()
        self.apply_font(settings.arabic_font)

    def _entry_title(self, e: dict) -> str:
        if translator.lang == "en" and e.get("title_en"):
            return e["title_en"]
        return e.get("title", "").strip()

    def _populate_list(self) -> None:
        self.list_widget.blockSignals(True)
        current_row = self.list_widget.currentRow()
        self.list_widget.clear()
        for e in self._filtered:
            item = QListWidgetItem(self._entry_title(e) or "—")
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        if self._filtered:
            self.list_widget.setCurrentRow(max(0, current_row) if current_row < len(self._filtered) else 0)
            self._show_index(self.list_widget.currentRow())

    def _filter(self, text: str) -> None:
        text = text.strip().lower()
        if not text:
            self._filtered = self._entries
        else:
            self._filtered = [e for e in self._entries if text in self._entry_title(e).lower()]
        self._populate_list()

    def _show_index(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered):
            return
        e = self._filtered[row]
        english = translator.lang == "en" and bool(e.get("title_en"))

        self.title_label.setText(self._entry_title(e))
        self.arabic_label.setText(e.get("dua_in_arabic", "").strip())

        if english:
            self.translit_label.setVisible(False)
            self.translation_label.setText(e.get("translation_en", "").strip())
            self.ref_label.setText(e.get("reference_en", "").strip() or "—")
        else:
            self.translit_label.setVisible(True)
            self.translit_label.setText(e.get("dua_in_bangla", "").strip())
            self.translation_label.setText(e.get("bangla_translation", "").strip())
            self.ref_label.setText(e.get("reference", "").strip() or "—")

        count = format_count(e.get("rules", ""), english=english)
        self.count_badge.setText(count or "")
        self.count_badge.setVisible(bool(count))

        # The long-form "rules"/"benefit" commentary only exists in Bangla in
        # the source data -- hide it in English mode rather than show raw
        # untranslated text under an English-language screen (the count badge
        # and reference already carry the essential English-mode info).
        self.rules_title.setVisible(not english)
        self.rules_label.setVisible(not english)
        self.benefit_title.setVisible(not english)
        self.benefit_label.setVisible(not english)
        if not english:
            self.rules_label.setText(e.get("rules", "").strip() or "—")
            benefit = (e.get("benefitorhadith") or e.get("benefit") or e.get("hadith") or "").strip()
            self.benefit_label.setText(benefit or "—")
        self.next_btn.setEnabled(len(self._filtered) > 1)

    def _go_next(self) -> None:
        if not self._filtered:
            return
        row = (self.list_widget.currentRow() + 1) % len(self._filtered)
        self.list_widget.setCurrentRow(row)

    def apply_font(self, family: str) -> None:
        f = self.arabic_label.font()
        f.setFamily(family)
        f.setPointSize(16)
        self.arabic_label.setFont(f)

    def retranslate(self) -> None:
        self.search.setPlaceholderText(translator.t("search"))
        self.rules_title.setText(translator.t("rules"))
        self.ref_title.setText(translator.t("reference"))
        self.benefit_title.setText(translator.t("benefit_hadith"))
        self.next_btn.setText(translator.t("next") + " →")
        self._populate_list()


class AzkarView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.daily_list = _AzkarList(_merged_entries("daily_azkar.json", "daily_azkar_en.json"))
        self.rukaiya_list = _AzkarList(_merged_entries("self_rukaiya.json", "self_rukaiya_en.json"))
        self.tabs.addTab(self.daily_list, "")
        self.tabs.addTab(self.rukaiya_list, "")

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def apply_font(self, family: str) -> None:
        self.daily_list.apply_font(family)
        self.rukaiya_list.apply_font(family)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_daily_azkar"))
        self.tabs.setTabText(0, translator.t("morning_azkar"))
        self.tabs.setTabText(1, translator.t("self_rukaiya"))
        self.daily_list.retranslate()
        self.rukaiya_list.retranslate()
