from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QButtonGroup, QColorDialog, QFileDialog,
                                QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                                QWidget)

from app.i18n import translator
from app.settings import settings
from app.ui.widgets.card import Card
from app.ui.widgets.no_scroll import NoScrollSlider
from app.ui.widgets.whiteboard_canvas import Tool, WhiteboardCanvas

_PALETTE = ["#000000", "#e03131", "#1971c2", "#2f9e44", "#f08c00", "#ffffff"]
_SWATCH_SIZE = 22
_ICON_SIZE = 20

# (tool, i18n key)
_TOOL_BUTTONS = [
    (Tool.FREEHAND, "whiteboard_tool_pen"),
    (Tool.LINE, "whiteboard_tool_line"),
    (Tool.ARROW, "whiteboard_tool_arrow"),
    (Tool.RECTANGLE, "whiteboard_tool_rectangle"),
    (Tool.ELLIPSE, "whiteboard_tool_ellipse"),
    (Tool.ERASER, "whiteboard_eraser"),
]


def _draw_tool_glyph(painter: QPainter, tool: str, color: QColor) -> None:
    """Vector icon for each tool -- drawn directly rather than relying on an
    emoji/symbol glyph, since the app's active UI font (Bangla-focused, for
    the Bangla-first audience) doesn't carry glyphs like an arrow or box
    outline and they were rendering as blank squares."""
    m = 4.0
    size = _ICON_SIZE
    pen = QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    if tool == Tool.FREEHAND:
        painter.drawLine(QPointF(m, size - m), QPointF(size - m, m))
        painter.setBrush(color)
        painter.drawEllipse(QPointF(size - m, m), 1.6, 1.6)
    elif tool == Tool.LINE:
        painter.drawLine(QPointF(m, size - m), QPointF(size - m, m))
    elif tool == Tool.ARROW:
        painter.drawLine(QPointF(m, size - m), QPointF(size - m, m))
        painter.drawLine(QPointF(size - m, m), QPointF(size - m - 6, m))
        painter.drawLine(QPointF(size - m, m), QPointF(size - m, m + 6))
    elif tool == Tool.RECTANGLE:
        painter.drawRect(QRectF(m, m, size - 2 * m, size - 2 * m))
    elif tool == Tool.ELLIPSE:
        painter.drawEllipse(QRectF(m, m, size - 2 * m, size - 2 * m))
    elif tool == Tool.ERASER:
        painter.setBrush(color)
        painter.translate(size / 2, size / 2)
        painter.rotate(-35)
        painter.drawRoundedRect(QRectF(-7, -5, 14, 10), 2, 2)


def _make_tool_icon(tool: str, normal_color: str, checked_color: str = "#ffffff") -> QIcon:
    icon = QIcon()
    for state, hex_color in ((QIcon.State.Off, normal_color), (QIcon.State.On, checked_color)):
        pixmap = QPixmap(_ICON_SIZE, _ICON_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        _draw_tool_glyph(painter, tool, QColor(hex_color))
        painter.end()
        icon.addPixmap(pixmap, QIcon.Mode.Normal, state)
    return icon


class WhiteboardView(QWidget):
    def __init__(self, on_fullscreen_changed=None, parent=None) -> None:
        super().__init__(parent)
        self._on_fullscreen_changed = on_fullscreen_changed
        self._fullscreen = False

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(12)
        layout = self._layout

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        toolbar_card = Card(spacing=8)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        self._tool_buttons: dict[str, QPushButton] = {}
        icon_color = "#F8FAFC" if settings.dark_mode else "#0B2C4D"
        for tool, _key in _TOOL_BUTTONS:
            btn = QPushButton()
            btn.setIcon(_make_tool_icon(tool, icon_color))
            btn.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
            btn.setObjectName("Ghost")
            btn.setCheckable(True)
            btn.setFixedSize(32, 32)
            btn.clicked.connect(lambda _=False, t=tool: self._select_tool(t))
            toolbar.addWidget(btn)
            self._tool_group.addButton(btn)
            self._tool_buttons[tool] = btn
        self._tool_buttons[Tool.FREEHAND].setChecked(True)

        toolbar.addSpacing(16)

        self._color_buttons: list[QPushButton] = []
        for hex_color in _PALETTE:
            btn = QPushButton()
            btn.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
            btn.setCheckable(True)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {hex_color}; border: 2px solid #888; border-radius: 4px; }} "
                f"QPushButton:checked {{ border: 2px solid #42A866; }}"
            )
            btn.clicked.connect(lambda _=False, c=hex_color: self._select_color(c))
            toolbar.addWidget(btn)
            self._color_buttons.append(btn)
        self._color_buttons[0].setChecked(True)

        self.custom_color_btn = QPushButton()
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        toolbar.addWidget(self.custom_color_btn)

        toolbar.addSpacing(16)

        self.width_label = QLabel()
        toolbar.addWidget(self.width_label)
        self.width_slider = NoScrollSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 24)
        self.width_slider.setValue(3)
        self.width_slider.setFixedWidth(120)
        self.width_slider.valueChanged.connect(self._on_width_changed)
        toolbar.addWidget(self.width_slider)

        toolbar.addSpacing(16)

        self.undo_btn = QPushButton()
        self.undo_btn.setObjectName("Ghost")
        self.undo_btn.clicked.connect(self._on_undo_clicked)
        toolbar.addWidget(self.undo_btn)

        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("Ghost")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        toolbar.addWidget(self.clear_btn)

        self.save_btn = QPushButton()
        self.save_btn.clicked.connect(self._on_save_clicked)
        toolbar.addWidget(self.save_btn)

        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setObjectName("Ghost")
        self.fullscreen_btn.setCheckable(True)
        self.fullscreen_btn.toggled.connect(self._on_fullscreen_toggled)
        toolbar.addWidget(self.fullscreen_btn)

        toolbar.addStretch(1)
        toolbar_card.addLayout(toolbar)
        layout.addWidget(toolbar_card)

        self.canvas = WhiteboardCanvas()
        layout.addWidget(self.canvas, 1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _select_tool(self, tool: str) -> None:
        self.canvas.tool = tool

    def _select_color(self, hex_color: str) -> None:
        self.canvas.pen_color = QColor(hex_color)
        if self.canvas.tool == Tool.ERASER:
            self.canvas.tool = Tool.FREEHAND
            self._tool_buttons[Tool.FREEHAND].setChecked(True)
        for btn in self._color_buttons:
            btn.setChecked(False)
        idx = _PALETTE.index(hex_color)
        self._color_buttons[idx].setChecked(True)

    def _pick_custom_color(self) -> None:
        color = QColorDialog.getColor(self.canvas.pen_color, self, translator.t("whiteboard_custom_color"))
        if color.isValid():
            self.canvas.pen_color = color
            if self.canvas.tool == Tool.ERASER:
                self.canvas.tool = Tool.FREEHAND
                self._tool_buttons[Tool.FREEHAND].setChecked(True)
            for btn in self._color_buttons:
                btn.setChecked(False)

    def _on_width_changed(self, value: int) -> None:
        self.canvas.pen_width = value

    def _on_undo_clicked(self) -> None:
        self.canvas.undo()

    def _on_clear_clicked(self) -> None:
        self.canvas.clear()

    def _on_save_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, translator.t("whiteboard_save"), "", "PNG (*.png)"
        )
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            self.canvas.save_to_file(path)

    def _on_fullscreen_toggled(self, checked: bool) -> None:
        self._fullscreen = checked
        self.heading.setVisible(not checked)
        self._layout.setContentsMargins(4, 4, 4, 4) if checked else self._layout.setContentsMargins(24, 24, 24, 24)
        self.fullscreen_btn.setText(translator.t("whiteboard_exit_fullscreen") if checked
                                     else translator.t("whiteboard_fullscreen"))
        if self._on_fullscreen_changed is not None:
            self._on_fullscreen_changed(checked)

    def exit_fullscreen(self) -> None:
        """Called by MainWindow when Escape is pressed while this tab is
        showing fullscreen -- unchecking the button re-triggers the same
        toggle handler that leaving fullscreen via the toolbar button does."""
        if self._fullscreen:
            self.fullscreen_btn.setChecked(False)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_whiteboard"))
        for tool, key in _TOOL_BUTTONS:
            self._tool_buttons[tool].setToolTip(translator.t(key))
        self.custom_color_btn.setText(translator.t("whiteboard_custom_color"))
        self.width_label.setText(translator.t("whiteboard_pen_width"))
        self.undo_btn.setText(translator.t("whiteboard_undo"))
        self.clear_btn.setText(translator.t("whiteboard_clear"))
        self.save_btn.setText(translator.t("whiteboard_save"))
        self.fullscreen_btn.setText(translator.t("whiteboard_exit_fullscreen") if self._fullscreen
                                     else translator.t("whiteboard_fullscreen"))
