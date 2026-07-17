from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout


class Card(QFrame):
    def __init__(self, object_name: str = "Card", margins: int = 16, spacing: int = 8, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(margins, margins, margins, margins)
        self.layout_.setSpacing(spacing)

    def addWidget(self, w) -> None:
        self.layout_.addWidget(w)

    def addLayout(self, lay) -> None:
        self.layout_.addLayout(lay)
