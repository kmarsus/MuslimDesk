from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                                QListWidget, QListWidgetItem, QPushButton,
                                QScrollArea, QSplitter, QStackedWidget,
                                QVBoxLayout, QWidget)

from app.data_loader import fetch_home_content
from app.i18n import translator
from app.settings import settings
from app.ui.widgets.arabic_font import set_arabic_font
from app.ui.widgets.card import Card


class DuaView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data = {"categories": [], "dua": [], "hadith": []}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        outer.addWidget(self.heading)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.loading_label)

        self.category_page = QWidget()
        self.category_grid = QGridLayout(self.category_page)
        self.category_grid.setSpacing(12)
        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setWidget(self.category_page)
        self.stack.addWidget(cat_scroll)

        self.detail_page = QWidget()
        detail_layout = QVBoxLayout(self.detail_page)
        self.back_btn = QPushButton()
        self.back_btn.setObjectName("Ghost")
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        detail_layout.addWidget(self.back_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        detail_layout.addWidget(splitter)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        self.dua_search = QLineEdit()
        self.dua_search.textChanged.connect(self._filter_duas)
        left_layout.addWidget(self.dua_search)
        self.dua_list = QListWidget()
        self.dua_list.currentRowChanged.connect(self._show_dua)
        left_layout.addWidget(self.dua_list)
        splitter.addWidget(left)

        right = QScrollArea()
        right.setWidgetResizable(True)
        self.dua_detail = Card(margins=20, spacing=10)
        right.setWidget(self.dua_detail)
        splitter.addWidget(right)
        splitter.setSizes([260, 640])

        self.dua_title_label = QLabel()
        self.dua_title_label.setObjectName("Heading")
        self.dua_title_label.setWordWrap(True)
        self.dua_arabic_label = QLabel()
        self.dua_arabic_label.setObjectName("Arabic")
        self.dua_arabic_label.setWordWrap(True)
        self.dua_arabic_label.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.dua_arabic_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.dua_translit_label = QLabel()
        self.dua_translit_label.setWordWrap(True)
        self.dua_translation_label = QLabel()
        self.dua_translation_label.setWordWrap(True)
        self.dua_ref_label = QLabel()
        self.dua_ref_label.setWordWrap(True)
        self.dua_ref_label.setObjectName("Muted")
        for w in [self.dua_title_label, self.dua_arabic_label, self.dua_translit_label,
                  self.dua_translation_label, self.dua_ref_label]:
            self.dua_detail.addWidget(w)

        self.stack.addWidget(self.detail_page)

        self._current_tag = ""
        self._filtered_duas: list[dict] = []

        translator.language_changed.connect(self._reload)
        self.retranslate()
        self._reload()
        self.apply_font(settings.arabic_font)

    def _reload(self, *_args) -> None:
        self._data = fetch_home_content(translator.lang)
        if not self._data["categories"] and not self._data["dua"]:
            self.loading_label.setText(translator.t("offline_no_data"))
            self.stack.setCurrentIndex(0)
            return
        self._populate_categories()
        self.stack.setCurrentIndex(1)

    def _populate_categories(self) -> None:
        while self.category_grid.count():
            item = self.category_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i, cat in enumerate(self._data["categories"]):
            btn = QPushButton(cat.get("title", ""))
            btn.setObjectName("Ghost")
            btn.setMinimumHeight(64)
            tag = cat.get("tag", "")
            btn.clicked.connect(lambda _=False, t=tag, title=cat.get("title", ""): self._open_category(t, title))
            self.category_grid.addWidget(btn, i // 3, i % 3)

    def _open_category(self, tag: str, title: str) -> None:
        self._current_tag = tag
        self._filtered_duas = [d for d in self._data["dua"] if d.get("category", "").strip() == tag.strip()]
        self.dua_search.clear()
        self._populate_dua_list()
        self.stack.setCurrentIndex(2)

    def _populate_dua_list(self) -> None:
        self.dua_list.clear()
        for d in self._filtered_duas:
            self.dua_list.addItem(QListWidgetItem(d.get("title", "").strip() or "—"))
        if self._filtered_duas:
            self.dua_list.setCurrentRow(0)

    def _filter_duas(self, text: str) -> None:
        text = text.strip().lower()
        base = [d for d in self._data["dua"] if d.get("category", "").strip() == self._current_tag.strip()]
        self._filtered_duas = base if not text else [d for d in base if text in d.get("title", "").lower()]
        self._populate_dua_list()

    def _show_dua(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered_duas):
            return
        d = self._filtered_duas[row]
        self.dua_title_label.setText(d.get("title", "").strip())
        self.dua_arabic_label.setText(d.get("dua_in_arabic", "").strip())
        self.dua_translit_label.setText(d.get("dua_in_bangla", "").strip())
        self.dua_translation_label.setText(d.get("bangla_translation", "").strip())
        self.dua_ref_label.setText(d.get("reference", "").strip())

    def apply_font(self, family: str) -> None:
        set_arabic_font(self.dua_arabic_label, family, size_px=21)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_dua"))
        self.back_btn.setText("← " + translator.t("categories"))
        self.dua_search.setPlaceholderText(translator.t("search"))
