"""Generates tiny up/down triangle PNG icons for QSpinBox arrows.

Qt's QSS border-triangle trick (zero-size box + colored borders meeting at
a point) turned out to render unreliably on this Qt/style combination --
it painted as a flat bar instead of a triangle. Drawing a real (tiny)
triangle bitmap and referencing it via `image: url(...)` is far more
reliable, so that's what this does, caching one pair of PNGs per ink color
in the user's local app-data folder.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QPolygon

from app.paths import user_data_dir

_SIZE = 8


def _triangle_path(color_hex: str, pointing: str) -> str:
    safe_name = color_hex.lstrip("#")
    out_dir = user_data_dir() / "icons_cache"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"spin_{pointing}_{safe_name}.png"
    if path.exists():
        return str(path).replace("\\", "/")

    pix = QPixmap(_SIZE, _SIZE)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color_hex))
    if pointing == "up":
        points = [QPoint(1, 6), QPoint(7, 6), QPoint(4, 1)]
    else:
        points = [QPoint(1, 2), QPoint(7, 2), QPoint(4, 7)]
    painter.drawPolygon(QPolygon(points))
    painter.end()
    pix.save(str(path), "PNG")
    return str(path).replace("\\", "/")


def spin_arrow_qss(ink_color_hex: str) -> str:
    up_path = _triangle_path(ink_color_hex, "up")
    down_path = _triangle_path(ink_color_hex, "down")
    return f"""
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({up_path});
        width: 8px; height: 8px;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({down_path});
        width: 8px; height: 8px;
    }}
    """
