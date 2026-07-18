from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget,
                                QListWidgetItem, QPushButton, QScrollArea,
                                QSplitter, QStackedWidget, QTabWidget,
                                QVBoxLayout, QWidget)

from app.azkar_count import format_count
from app.i18n import translator
from app.paths import data_path
from app.settings import settings
from app.ui.widgets.arabic_font import set_arabic_font
from app.ui.widgets.card import Card

_TIER_ORDER = ["High", "Medium", "Low"]
_TIER_TITLE_KEY = {"High": "tier_high_title", "Medium": "tier_medium_title", "Low": "tier_low_title"}
_HEADER_ROLE = Qt.ItemDataRole.UserRole + 1


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
    """One tab: search box + list on the left, detail card on the right.

    When the entries span more than one "priority" tier (High/Medium/Low --
    matching the Android app's 3-level structure), the list groups entries
    under a tier header and advancing past the last item of a tier shows a
    "MashaAllah!" checkpoint screen before continuing into the next tier."""

    def __init__(self, entries: list[dict]) -> None:
        super().__init__()
        self._entries = entries
        self._filtered = entries
        self._tiered = len({e.get("priority") for e in entries} & set(_TIER_ORDER)) > 1
        self._pending_tier: str | None = None  # tier we're about to enter, mid-checkpoint

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
        self.right_stack = QStackedWidget()
        right.setWidget(self.right_stack)
        splitter.addWidget(right)
        splitter.setSizes([260, 640])

        self._build_detail_page()
        self._build_checkpoint_page()

        self._populate_list()
        self.apply_font(settings.arabic_font)

    # ── detail page ──────────────────────────────────────────────────
    def _build_detail_page(self) -> None:
        self.detail_card = Card(margins=20, spacing=10)
        self.right_stack.addWidget(self.detail_card)

        next_row = QHBoxLayout()
        next_row.addStretch(1)
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self._go_next)
        next_row.addWidget(self.next_btn)
        self.detail_card.addLayout(next_row)

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

    # ── tier-complete checkpoint page ───────────────────────────────
    def _build_checkpoint_page(self) -> None:
        self.checkpoint_card = Card(margins=32, spacing=14)
        self.checkpoint_icon = QLabel("✅")
        self.checkpoint_icon.setStyleSheet("font-size: 40px;")
        self.checkpoint_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_headline = QLabel()
        self.checkpoint_headline.setObjectName("Heading")
        self.checkpoint_headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_done_msg = QLabel()
        self.checkpoint_done_msg.setWordWrap(True)
        self.checkpoint_done_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_next_msg = QLabel()
        self.checkpoint_next_msg.setWordWrap(True)
        self.checkpoint_next_msg.setObjectName("SubHeading")
        self.checkpoint_next_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_continue_btn = QPushButton()
        self.checkpoint_continue_btn.clicked.connect(self._continue_after_checkpoint)
        for w in [self.checkpoint_icon, self.checkpoint_headline, self.checkpoint_done_msg,
                  self.checkpoint_next_msg, self.checkpoint_continue_btn]:
            self.checkpoint_card.addWidget(w)
        self.right_stack.addWidget(self.checkpoint_card)

    # ── list population (with tier headers) ─────────────────────────
    def _entry_title(self, e: dict) -> str:
        if translator.lang == "en" and e.get("title_en"):
            return e["title_en"]
        return e.get("title", "").strip()

    def _tier_title(self, priority: str) -> str:
        key = _TIER_TITLE_KEY.get(priority)
        return translator.t(key) if key else priority

    def _populate_list(self) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        last_tier = None
        for e in self._filtered:
            tier = e.get("priority") if self._tiered else None
            if tier is not None and tier != last_tier:
                header = QListWidgetItem(f"— {self._tier_title(tier)} —")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                header.setData(_HEADER_ROLE, True)
                header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                header.setForeground(Qt.GlobalColor.darkGreen)
                self.list_widget.addItem(header)
                last_tier = tier
            item = QListWidgetItem(self._entry_title(e) or "—")
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        first_real_row = 1 if (self.list_widget.count() and self.list_widget.item(0).data(_HEADER_ROLE)) else 0
        if self._filtered:
            self.list_widget.setCurrentRow(first_real_row)
            self._show_index(first_real_row)

    def _filter(self, text: str) -> None:
        text = text.strip().lower()
        if not text:
            self._filtered = self._entries
        else:
            self._filtered = [e for e in self._entries if text in self._entry_title(e).lower()]
        self._populate_list()

    # ── selection maps list-row (including headers) <-> entry index ──
    def _entry_index_for_row(self, row: int) -> int | None:
        """Row in the QListWidget (headers included) -> index into
        self._filtered (headers excluded), or None if row is a header."""
        entry_i = -1
        for r in range(row + 1):
            item = self.list_widget.item(r)
            if item is not None and not item.data(_HEADER_ROLE):
                entry_i += 1
        item = self.list_widget.item(row)
        if item is None or item.data(_HEADER_ROLE):
            return None
        return entry_i

    def _row_for_entry_index(self, entry_i: int) -> int:
        count = -1
        for r in range(self.list_widget.count()):
            item = self.list_widget.item(r)
            if item is not None and not item.data(_HEADER_ROLE):
                count += 1
                if count == entry_i:
                    return r
        return 0

    def _show_index(self, row: int) -> None:
        entry_i = self._entry_index_for_row(row)
        if entry_i is None or entry_i < 0 or entry_i >= len(self._filtered):
            return
        self.right_stack.setCurrentWidget(self.detail_card)
        e = self._filtered[entry_i]
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
        row = self.list_widget.currentRow()
        entry_i = self._entry_index_for_row(row)
        if entry_i is None:
            return
        next_i = (entry_i + 1) % len(self._filtered)

        if self._tiered and next_i != 0:
            cur_tier = self._filtered[entry_i].get("priority")
            next_tier = self._filtered[next_i].get("priority")
            if next_tier != cur_tier:
                self._show_checkpoint(cur_tier, next_tier, next_i)
                return

        self.list_widget.setCurrentRow(self._row_for_entry_index(next_i))

    def _show_checkpoint(self, done_tier: str, next_tier: str, next_entry_i: int) -> None:
        self._pending_tier = next_entry_i
        self.checkpoint_headline.setText(translator.t("mashallah"))
        self.checkpoint_done_msg.setText(translator.t("completed_tier_message", tier=self._tier_title(done_tier)))
        self.checkpoint_next_msg.setText(translator.t("now_starting_tier", tier=self._tier_title(next_tier)))
        self.checkpoint_continue_btn.setText(translator.t("continue_btn"))
        self.right_stack.setCurrentWidget(self.checkpoint_card)

    def _continue_after_checkpoint(self) -> None:
        if self._pending_tier is not None:
            self.list_widget.setCurrentRow(self._row_for_entry_index(self._pending_tier))
            self._pending_tier = None

    def apply_font(self, family: str) -> None:
        set_arabic_font(self.arabic_label, family, size_px=21)

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
