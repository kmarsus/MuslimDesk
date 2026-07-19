"""The drawing surface for the Whiteboard tab -- a plain QPixmap the user
draws strokes/shapes onto with the mouse, kept deliberately simple (no
vector stroke model) since a teacher just needs quick freehand notes and
basic annotations during class, not a full vector editor."""
from __future__ import annotations

import math

from PySide6.QtCore import QPoint, QPointF, QRect, Qt
from PySide6.QtGui import (QColor, QCursor, QFont, QMouseEvent, QPainter,
                            QPaintEvent, QPainterPath, QPen, QPixmap)
from PySide6.QtWidgets import QWidget

MAX_UNDO_STEPS = 20


class Tool:
    FREEHAND = "freehand"
    ERASER = "eraser"
    LINE = "line"
    ARROW = "arrow"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"


_SHAPE_TOOLS = (Tool.LINE, Tool.ARROW, Tool.RECTANGLE, Tool.ELLIPSE)


def _pen_cursor() -> QCursor:
    """Renders the pen emoji onto a small transparent pixmap and uses it as
    the mouse cursor -- Qt has no built-in "pen" cursor shape, and a plain
    crosshair reads as a generic selection tool rather than "you're drawing"."""
    size = 28
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setFont(QFont("Segoe UI Emoji", 16))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "\U0001FA84")  # pen/quill glyph
    painter.end()
    return QCursor(pixmap, 2, size - 4)  # hotspot near the visual nib tip


class WhiteboardCanvas(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setCursor(_pen_cursor())
        self._pixmap = QPixmap(self.size())
        self._pixmap.fill(Qt.GlobalColor.white)
        self._undo_stack: list[QPixmap] = []
        self._drawing = False
        self._stroke_points: list[QPoint] = []
        self._shape_start = QPoint()
        self._shape_base: QPixmap | None = None

        self.pen_color = QColor("#000000")
        self.pen_width = 3
        self.tool = Tool.FREEHAND

    @property
    def eraser_mode(self) -> bool:
        return self.tool == Tool.ERASER

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        new_size = event.size()
        if new_size.width() <= 0 or new_size.height() <= 0:
            return
        new_pixmap = QPixmap(new_size)
        new_pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.end()
        self._pixmap = new_pixmap

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)

    def _push_undo_snapshot(self) -> None:
        self._undo_stack.append(self._pixmap.copy())
        if len(self._undo_stack) > MAX_UNDO_STEPS:
            self._undo_stack.pop(0)

    def undo(self) -> None:
        if not self._undo_stack:
            return
        self._pixmap = self._undo_stack.pop()
        self.update()

    def clear(self) -> None:
        self._push_undo_snapshot()
        self._pixmap.fill(Qt.GlobalColor.white)
        self.update()

    def save_to_file(self, path: str) -> bool:
        return self._pixmap.save(path)

    def _make_pen(self) -> QPen:
        color = Qt.GlobalColor.white if self.tool == Tool.ERASER else self.pen_color
        return QPen(color, self.pen_width, Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    def _draw_shape(self, painter: QPainter, start: QPoint, end: QPoint) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self._make_pen())
        if self.tool == Tool.LINE:
            painter.drawLine(start, end)
        elif self.tool == Tool.ARROW:
            painter.drawLine(start, end)
            self._draw_arrow_head(painter, start, end)
        elif self.tool == Tool.RECTANGLE:
            painter.drawRect(QRect(start, end).normalized())
        elif self.tool == Tool.ELLIPSE:
            painter.drawEllipse(QRect(start, end).normalized())

    def _draw_arrow_head(self, painter: QPainter, start: QPoint, end: QPoint) -> None:
        dx, dy = end.x() - start.x(), end.y() - start.y()
        length = math.hypot(dx, dy)
        if length < 1:
            return
        angle = math.atan2(dy, dx)
        head_len = max(10.0, self.pen_width * 4)
        spread = math.radians(28)
        p1 = QPointF(end.x() - head_len * math.cos(angle - spread),
                      end.y() - head_len * math.sin(angle - spread))
        p2 = QPointF(end.x() - head_len * math.cos(angle + spread),
                      end.y() - head_len * math.sin(angle + spread))
        painter.drawLine(QPointF(end), p1)
        painter.drawLine(QPointF(end), p2)

    def _smoothed_stroke_path(self) -> QPainterPath:
        """Builds one continuous curve through every point of the stroke so
        far, using each raw point as the control point of a quadratic Bezier
        between the midpoints on either side of it (the standard technique
        real drawing apps use for freehand ink). Baking short straight
        segments into the pixmap one mouse-move at a time -- the previous
        approach -- left visible seams/kinks at every sample point whenever
        the pen changed direction quickly; rendering the whole stroke as one
        path every time removes those seams entirely."""
        points = self._stroke_points
        path = QPainterPath()
        if not points:
            return path
        path.moveTo(QPointF(points[0]))
        if len(points) == 1:
            path.lineTo(QPointF(points[0]))
            return path
        for i in range(1, len(points) - 1):
            mid = QPointF((points[i].x() + points[i + 1].x()) / 2,
                           (points[i].y() + points[i + 1].y()) / 2)
            path.quadTo(QPointF(points[i]), mid)
        path.lineTo(QPointF(points[-1]))
        return path

    def _redraw_stroke_preview(self) -> None:
        self._pixmap = self._shape_base.copy()
        painter = QPainter(self._pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self._make_pen())
        painter.drawPath(self._smoothed_stroke_path())
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._push_undo_snapshot()
        self._drawing = True
        pos = event.position().toPoint()
        self._shape_base = self._pixmap.copy()
        if self.tool in _SHAPE_TOOLS:
            self._shape_start = pos
        else:
            self._stroke_points = [pos]

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._drawing:
            return
        current = event.position().toPoint()
        # redraw from the pre-stroke snapshot each move so the in-progress
        # preview doesn't leave a trail of every intermediate frame
        if self.tool in _SHAPE_TOOLS:
            self._pixmap = self._shape_base.copy()
            painter = QPainter(self._pixmap)
            self._draw_shape(painter, self._shape_start, current)
            painter.end()
        else:
            self._stroke_points.append(current)
            self._redraw_stroke_preview()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False
            self._stroke_points = []
            self._shape_base = None
