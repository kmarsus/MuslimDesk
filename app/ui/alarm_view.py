from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QPushButton,
                                QScrollArea, QVBoxLayout, QWidget)

from app.alarms import WEEKDAY_LABELS_BN, WEEKDAY_LABELS_EN, Alarm
from app.i18n import translator
from app.ui.widgets.alarm_edit_dialog import AlarmEditDialog
from app.ui.widgets.card import Card


class AlarmView(QWidget):
    def __init__(self, alarm_manager, parent=None) -> None:
        super().__init__(parent)
        self._manager = alarm_manager

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(14)

        header_row = QHBoxLayout()
        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        header_row.addWidget(self.heading)
        header_row.addStretch(1)
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(self._add_alarm)
        header_row.addWidget(self.add_btn)
        self._layout.addLayout(header_row)

        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(10)
        self._layout.addLayout(self.list_container)
        self.empty_label = QLabel()
        self.empty_label.setObjectName("Muted")
        self._layout.addWidget(self.empty_label)
        self._layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()
        self._refresh_list()

    def _add_alarm(self) -> None:
        dialog = AlarmEditDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._manager.add_or_update(dialog.result_alarm())
            self._refresh_list()

    def _edit_alarm(self, alarm: Alarm) -> None:
        dialog = AlarmEditDialog(alarm, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._manager.add_or_update(dialog.result_alarm())
            self._refresh_list()

    def _delete_alarm(self, alarm_id: str) -> None:
        self._manager.delete(alarm_id)
        self._refresh_list()

    def _toggle_enabled(self, alarm: Alarm, checked: bool) -> None:
        alarm.enabled = checked
        self._manager.add_or_update(alarm)

    def _refresh_list(self) -> None:
        while self.list_container.count():
            item = self.list_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alarms = sorted(self._manager.alarms, key=lambda a: a.time)
        self.empty_label.setVisible(not alarms)
        english = translator.lang == "en"
        day_labels = WEEKDAY_LABELS_EN if english else WEEKDAY_LABELS_BN

        for alarm in alarms:
            card = Card(margins=14, spacing=4)
            top_row = QHBoxLayout()
            time_label = QLabel(alarm.time)
            time_label.setStyleSheet("font-size: 22px; font-weight: 800;")
            top_row.addWidget(time_label)
            top_row.addStretch(1)

            enabled_box = QCheckBox()
            enabled_box.setChecked(alarm.enabled)
            enabled_box.toggled.connect(lambda checked, a=alarm: self._toggle_enabled(a, checked))
            top_row.addWidget(enabled_box)

            edit_btn = QPushButton(translator.t("edit_alarm"))
            edit_btn.setObjectName("Ghost")
            edit_btn.clicked.connect(lambda _=False, a=alarm: self._edit_alarm(a))
            top_row.addWidget(edit_btn)

            delete_btn = QPushButton(translator.t("delete"))
            delete_btn.setObjectName("Ghost")
            delete_btn.clicked.connect(lambda _=False, aid=alarm.id: self._delete_alarm(aid))
            top_row.addWidget(delete_btn)
            card.addLayout(top_row)

            if alarm.label:
                lbl = QLabel(alarm.label)
                card.addWidget(lbl)

            days_text = translator.t("every_day") if not alarm.weekdays else ", ".join(
                day_labels[d] for d in sorted(alarm.weekdays)
            )
            days_label = QLabel(days_text)
            days_label.setObjectName("Muted")
            card.addWidget(days_label)

            if alarm.shutdown_on_ring:
                warn = QLabel("⚡ " + translator.t("shutdown_on_ring"))
                warn.setObjectName("Muted")
                card.addWidget(warn)

            self.list_container.addWidget(card)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_alarm"))
        self.add_btn.setText(translator.t("add_alarm"))
        self.empty_label.setText(translator.t("no_alarms"))
        self._refresh_list()
