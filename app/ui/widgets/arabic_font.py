"""Applies an Arabic font choice to a QLabel.

Once any QSS stylesheet is active on a widget or its ancestors -- which it
always is here, via the app-wide theme stylesheet -- Qt's CSS engine takes
over font resolution for that widget entirely, and a plain `label.setFont()`
call is silently ignored (it keeps rendering with whatever the stylesheet
cascade resolves to, e.g. the base QWidget font-family). A stylesheet rule
set directly on the widget itself takes precedence over its ancestors', so
routing the font choice through `setStyleSheet()` here is what actually
makes it take effect.
"""
from __future__ import annotations

from PySide6.QtWidgets import QLabel


def set_arabic_font(label: QLabel, family: str, size_px: int = 22) -> None:
    escaped = family.replace("'", "\\'")
    label.setStyleSheet(f"font-family: '{escaped}'; font-size: {size_px}px;")
