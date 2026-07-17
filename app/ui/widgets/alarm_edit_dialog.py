from __future__ import annotations

from PySide6.QtCore import QTime
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QVBoxLayout)

from app import azan_voices
from app.alarms import WEEKDAY_LABELS_BN, WEEKDAY_LABELS_EN, Alarm
from app.i18n import translator
from app.ui.widgets.no_scroll import NoScrollSpinBox, NoScrollTimeEdit
from app.ui.widgets.voice_picker import VoicePickerCombo


class AlarmEditDialog(QDialog):
    def __init__(self, alarm: Alarm | None = None, parent=None) -> None:
        super().__init__(parent)
        self._alarm = alarm or Alarm()
        self.setWindowTitle(translator.t("edit_alarm"))
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel(translator.t("alarm_time")))
        self.time_edit = NoScrollTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        h, m = (int(x) for x in self._alarm.time.split(":"))
        self.time_edit.setTime(QTime(h, m))
        time_row.addWidget(self.time_edit)
        time_row.addStretch(1)
        layout.addLayout(time_row)

        self.label_edit = QLineEdit(self._alarm.label)
        self.label_edit.setPlaceholderText(translator.t("alarm_label"))
        layout.addWidget(self.label_edit)

        layout.addWidget(QLabel(translator.t("repeat_days")))
        weekday_row = QHBoxLayout()
        labels = WEEKDAY_LABELS_EN if translator.lang == "en" else WEEKDAY_LABELS_BN
        self.day_buttons: list[QPushButton] = []
        for i, label in enumerate(labels):
            btn = QPushButton(label)
            btn.setObjectName("Ghost")
            btn.setCheckable(True)
            btn.setChecked(i in self._alarm.weekdays)
            weekday_row.addWidget(btn)
            self.day_buttons.append(btn)
        layout.addLayout(weekday_row)
        hint = QLabel(translator.t("every_day"))
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        sound_row = QHBoxLayout()
        sound_row.addWidget(QLabel(translator.t("alarm_sound")))
        self.sound_combo = VoicePickerCombo(azan_voices.REGULAR, self._alarm.voice_id)
        sound_row.addWidget(self.sound_combo, 1)
        layout.addLayout(sound_row)

        self.shutdown_checkbox = QCheckBox(translator.t("shutdown_on_ring"))
        self.shutdown_checkbox.setChecked(self._alarm.shutdown_on_ring)
        self.shutdown_checkbox.toggled.connect(self._on_shutdown_toggled)
        layout.addWidget(self.shutdown_checkbox)

        delay_row = QHBoxLayout()
        self.delay_label = QLabel(translator.t("shutdown_delay"))
        delay_row.addWidget(self.delay_label)
        self.delay_spin = NoScrollSpinBox()
        self.delay_spin.setRange(5, 600)
        self.delay_spin.setValue(self._alarm.shutdown_delay_sec)
        delay_row.addWidget(self.delay_spin)
        layout.addLayout(delay_row)
        self._on_shutdown_toggled(self._alarm.shutdown_on_ring)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("✕")
        cancel_btn.setObjectName("Ghost")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton(translator.t("save"))
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_shutdown_toggled(self, checked: bool) -> None:
        self.delay_label.setVisible(checked)
        self.delay_spin.setVisible(checked)

    def result_alarm(self) -> Alarm:
        t = self.time_edit.time()
        self._alarm.time = f"{t.hour():02d}:{t.minute():02d}"
        self._alarm.label = self.label_edit.text().strip()
        self._alarm.weekdays = [i for i, btn in enumerate(self.day_buttons) if btn.isChecked()]
        self._alarm.voice_id = self.sound_combo.current_voice_id()
        self._alarm.shutdown_on_ring = self.shutdown_checkbox.isChecked()
        self._alarm.shutdown_delay_sec = self.delay_spin.value()
        return self._alarm
