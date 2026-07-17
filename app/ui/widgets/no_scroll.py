"""Input widgets that always ignore mouse-wheel events -- prevents the
classic Qt annoyance where scrolling a page silently changes whatever
spinbox/combobox/slider happens to be under the cursor. An earlier version
only blocked the wheel when the widget was unfocused, but a widget left
focused from a previous click (easy to do while scrolling a long settings
page) would still eat the scroll and change its value -- e.g. the azan
voice combo silently switching, or a manual-adjustment spinbox drifting.
Scrolling a page should never change one of these controls; use the
arrows, the dropdown, or type a value instead."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QCompleter, QDoubleSpinBox, QSlider, QSpinBox, QTimeEdit


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event) -> None:
        event.ignore()


class NoScrollSpinBox(QSpinBox):
    def wheelEvent(self, event) -> None:
        event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event) -> None:
        event.ignore()


class NoScrollSlider(QSlider):
    def wheelEvent(self, event) -> None:
        event.ignore()


class NoScrollTimeEdit(QTimeEdit):
    def wheelEvent(self, event) -> None:
        event.ignore()


def make_searchable(combo: QComboBox) -> None:
    """Type-to-filter a combo box's own item list (country/city pickers with
    hundreds/thousands of entries) -- editable, but only existing items can
    be committed (no free text), matching anywhere in the label."""
    combo.setEditable(True)
    combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    completer = QCompleter(combo.model(), combo)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    combo.setCompleter(completer)
