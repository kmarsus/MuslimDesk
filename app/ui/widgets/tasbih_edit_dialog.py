from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from app.i18n import translator
from app.tasbih_targets import TasbihTarget
from app.ui.widgets.no_scroll import NoScrollSpinBox


class TasbihEditDialog(QDialog):
    def __init__(self, target: TasbihTarget | None = None, parent=None) -> None:
        super().__init__(parent)
        self._target = target or TasbihTarget()
        self.setWindowTitle(translator.t("edit_tasbih_target"))
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.name_edit = QLineEdit(self._target.name)
        self.name_edit.setPlaceholderText(translator.t("tasbih_name_placeholder"))
        layout.addWidget(self.name_edit)

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel(translator.t("tasbih_target")))
        self.target_spin = NoScrollSpinBox()
        self.target_spin.setRange(1, 100000)
        self.target_spin.setValue(self._target.target)
        target_row.addWidget(self.target_spin)
        layout.addLayout(target_row)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("✕")
        cancel_btn.setObjectName("Ghost")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton(translator.t("save"))
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def result_target(self) -> TasbihTarget:
        self._target.name = self.name_edit.text().strip() or self._target.name
        self._target.target = self.target_spin.value()
        return self._target
