from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.i18n import translator
from app.settings import settings
from app.ui.widgets.card import Card
from app.ui.widgets.no_scroll import NoScrollSpinBox


class TasbihView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.card = Card(margins=30, spacing=16)
        self.count_label = QLabel(str(settings.tasbih_count))
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("font-size: 64px; font-weight: 800;")
        self.card.addWidget(self.count_label)

        self.count_btn = QPushButton("+ ১")
        self.count_btn.setMinimumHeight(80)
        self.count_btn.setStyleSheet("font-size: 20px;")
        self.count_btn.clicked.connect(self._increment)
        self.card.addWidget(self.count_btn)

        target_row = QHBoxLayout()
        self.target_label = QLabel()
        target_row.addWidget(self.target_label)
        self.target_spin = NoScrollSpinBox()
        self.target_spin.setRange(1, 10000)
        self.target_spin.setValue(settings.tasbih_target)
        self.target_spin.valueChanged.connect(self._set_target)
        target_row.addWidget(self.target_spin)
        target_row.addStretch(1)
        self.reset_btn = QPushButton()
        self.reset_btn.setObjectName("Ghost")
        self.reset_btn.clicked.connect(self._reset)
        target_row.addWidget(self.reset_btn)
        self.card.addLayout(target_row)

        layout.addWidget(self.card)
        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _increment(self) -> None:
        settings.tasbih_count += 1
        if settings.tasbih_count >= settings.tasbih_target:
            settings.tasbih_count = 0
        self.count_label.setText(str(settings.tasbih_count))

    def _reset(self) -> None:
        settings.tasbih_count = 0
        self.count_label.setText("0")

    def _set_target(self, v: int) -> None:
        settings.tasbih_target = v

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_tasbih"))
        self.target_label.setText(translator.t("tasbih_target"))
        self.reset_btn.setText(translator.t("reset"))
