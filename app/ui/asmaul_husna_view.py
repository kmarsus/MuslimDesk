from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.i18n import translator
from app.paths import data_path
from app.settings import settings
from app.ui.widgets.card import Card


class AsmaulHusnaView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._names = json.loads(data_path("asmaul_husna.json").read_text(encoding="utf-8"))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        layout.addLayout(self.grid)
        layout.addStretch(1)

        self._cards = []
        self._build_grid()
        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _build_grid(self) -> None:
        for i, n in enumerate(self._names):
            card = Card(margins=12, spacing=4)
            idx_label = QLabel(f"{n['id']}")
            idx_label.setObjectName("Muted")
            arabic = QLabel(n["arabic"])
            arabic.setObjectName("Arabic")
            arabic.setAlignment(Qt.AlignmentFlag.AlignRight)
            arabic.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            f = arabic.font()
            f.setFamily(settings.arabic_font)
            f.setPointSize(18)
            arabic.setFont(f)
            name = QLabel(n["name"])
            name.setStyleSheet("font-weight: 700;")
            meaning = QLabel()
            meaning.setObjectName("Muted")
            meaning.setWordWrap(True)
            card.addWidget(idx_label)
            card.addWidget(arabic)
            card.addWidget(name)
            card.addWidget(meaning)
            self.grid.addWidget(card, i // 3, i % 3)
            self._cards.append((n, meaning, arabic))

    def apply_font(self, family: str) -> None:
        for _n, _meaning, arabic in self._cards:
            f = arabic.font()
            f.setFamily(family)
            arabic.setFont(f)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("ninety_nine_names"))
        english = translator.lang == "en"
        for n, meaning, _arabic in self._cards:
            meaning.setText(n["meaningEn"] if english else n["meaning"])
