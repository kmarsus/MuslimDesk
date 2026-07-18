from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QProgressBar,
                                QPushButton, QScrollArea, QVBoxLayout, QWidget)

from app.i18n import translator
from app.tasbih_targets import TasbihTarget, load_targets, save_targets
from app.ui.widgets.card import Card
from app.ui.widgets.tasbih_edit_dialog import TasbihEditDialog

_DONE_BG = "rgba(66,168,102,0.15)"


class TasbihView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._targets: list[TasbihTarget] = load_targets()
        self._current_id: str | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        header_row.addWidget(self.heading)
        header_row.addStretch(1)
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(self._add_target)
        header_row.addWidget(self.add_btn)
        self.reset_all_btn = QPushButton()
        self.reset_all_btn.setObjectName("Ghost")
        self.reset_all_btn.clicked.connect(self._reset_all)
        header_row.addWidget(self.reset_all_btn)
        layout.addLayout(header_row)

        # ── big counter for the current active target ──────────────
        self.counter_card = Card(margins=30, spacing=12)
        self.current_name_label = QLabel()
        self.current_name_label.setObjectName("SectionTitle")
        self.current_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_card.addWidget(self.current_name_label)

        self.count_label = QLabel("0")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("font-size: 64px; font-weight: 800;")
        self.counter_card.addWidget(self.count_label)

        count_btn_row = QHBoxLayout()
        self.count_down_btn = QPushButton("−1")
        self.count_down_btn.setObjectName("Ghost")
        self.count_down_btn.setMinimumHeight(80)
        self.count_down_btn.setFixedWidth(70)
        self.count_down_btn.setStyleSheet("font-size: 20px;")
        self.count_down_btn.clicked.connect(self._untap)
        count_btn_row.addWidget(self.count_down_btn)

        self.count_btn = QPushButton()
        self.count_btn.setMinimumHeight(80)
        self.count_btn.setStyleSheet("font-size: 20px;")
        self.count_btn.clicked.connect(self._tap)
        count_btn_row.addWidget(self.count_btn, 1)
        self.counter_card.addLayout(count_btn_row)

        self.all_done_label = QLabel()
        self.all_done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.all_done_label.setObjectName("Muted")
        self.counter_card.addWidget(self.all_done_label)

        layout.addWidget(self.counter_card)

        # ── list of all targets ─────────────────────────────────────
        self.targets_title = QLabel()
        self.targets_title.setObjectName("SectionTitle")
        layout.addWidget(self.targets_title)

        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(10)
        layout.addLayout(self.list_container)
        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self._pick_current()
        self.retranslate()

    # ── persistence / sequencing ─────────────────────────────────────
    def _save(self) -> None:
        save_targets(self._targets)

    def _pick_current(self) -> None:
        """Advances self._current_id to the first active, not-yet-completed target."""
        for t in self._targets:
            if t.active and not t.completed:
                self._current_id = t.id
                return
        self._current_id = None

    def _current_target(self) -> TasbihTarget | None:
        for t in self._targets:
            if t.id == self._current_id:
                return t
        return None

    def _tap(self) -> None:
        t = self._current_target()
        if t is None:
            return
        t.count = min(t.count + 1, t.target)
        if t.completed:
            self._pick_current()
        self._save()
        self._refresh()

    def _untap(self) -> None:
        t = self._current_target()
        if t is None:
            return
        t.count = max(0, t.count - 1)
        self._save()
        self._refresh()

    def _reset_all(self) -> None:
        for t in self._targets:
            t.count = 0
        self._save()
        self._pick_current()
        self._refresh()

    def _add_target(self) -> None:
        dialog = TasbihEditDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._targets.append(dialog.result_target())
            self._save()
            if self._current_id is None:
                self._pick_current()
            self._refresh()

    def _edit_target(self, target: TasbihTarget) -> None:
        dialog = TasbihEditDialog(target, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            dialog.result_target()
            self._save()
            self._refresh()

    def _delete_target(self, target_id: str) -> None:
        self._targets = [t for t in self._targets if t.id != target_id]
        self._save()
        if self._current_id == target_id:
            self._pick_current()
        self._refresh()

    def _toggle_active(self, target: TasbihTarget, checked: bool) -> None:
        target.active = checked
        self._save()
        if not checked and self._current_id == target.id:
            self._pick_current()
        elif checked and self._current_id is None and not target.completed:
            self._current_id = target.id
        self._refresh()

    def _reset_one(self, target: TasbihTarget) -> None:
        target.count = 0
        self._save()
        if self._current_id is None:
            self._pick_current()
        self._refresh()

    def _move_target(self, target: TasbihTarget, offset: int) -> None:
        i = next((idx for idx, t in enumerate(self._targets) if t.id == target.id), None)
        if i is None:
            return
        j = i + offset
        if not (0 <= j < len(self._targets)):
            return
        self._targets[i], self._targets[j] = self._targets[j], self._targets[i]
        self._save()
        self._refresh()

    # ── rendering ─────────────────────────────────────────────────────
    def _refresh(self) -> None:
        current = self._current_target()
        if current is None:
            self.current_name_label.setText("—")
            self.count_label.setText("0")
            self.count_btn.setEnabled(False)
            self.count_down_btn.setEnabled(False)
            self.all_done_label.setVisible(bool(self._targets))
        else:
            self.current_name_label.setText(f"{current.name}  ({current.count}/{current.target})")
            self.count_label.setText(str(current.count))
            self.count_btn.setEnabled(True)
            self.count_down_btn.setEnabled(current.count > 0)
            self.all_done_label.setVisible(False)

        while self.list_container.count():
            item = self.list_container.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        for idx, t in enumerate(self._targets):
            card = Card(margins=12, spacing=6)
            if t.completed:
                card.setStyleSheet(f"#Card {{ background-color: {_DONE_BG}; }}")

            top_row = QHBoxLayout()

            move_col = QVBoxLayout()
            move_col.setSpacing(2)
            _move_btn_style = "padding: 0px; font-size: 11px;"
            up_btn = QPushButton("▲")
            up_btn.setObjectName("Ghost")
            up_btn.setFixedSize(28, 22)
            up_btn.setStyleSheet(_move_btn_style)
            up_btn.setEnabled(idx > 0)
            up_btn.clicked.connect(lambda _=False, tt=t: self._move_target(tt, -1))
            down_btn = QPushButton("▼")
            down_btn.setObjectName("Ghost")
            down_btn.setFixedSize(28, 22)
            down_btn.setStyleSheet(_move_btn_style)
            down_btn.setEnabled(idx < len(self._targets) - 1)
            down_btn.clicked.connect(lambda _=False, tt=t: self._move_target(tt, 1))
            move_col.addWidget(up_btn)
            move_col.addWidget(down_btn)
            top_row.addLayout(move_col)

            is_current = t.id == self._current_id
            name_text = ("▶ " if is_current else "") + t.name
            name_label = QLabel(name_text)
            name_label.setStyleSheet("font-weight: 700;")
            top_row.addWidget(name_label)
            top_row.addStretch(1)

            if t.completed:
                done_label = QLabel("✓ " + translator.t("completed"))
                done_label.setStyleSheet("color: #2E7D32; font-weight: 700;")
                top_row.addWidget(done_label)

            active_checkbox = QCheckBox(translator.t("active"))
            active_checkbox.setChecked(t.active)
            active_checkbox.toggled.connect(lambda checked, tt=t: self._toggle_active(tt, checked))
            top_row.addWidget(active_checkbox)
            card.addLayout(top_row)

            progress = QProgressBar()
            progress.setRange(0, t.target)
            progress.setValue(min(t.count, t.target))
            progress.setFormat(f"{t.count} / {t.target}")
            card.addWidget(progress)

            btn_row = QHBoxLayout()
            btn_row.addStretch(1)
            reset_btn = QPushButton(translator.t("reset"))
            reset_btn.setObjectName("Ghost")
            reset_btn.clicked.connect(lambda _=False, tt=t: self._reset_one(tt))
            btn_row.addWidget(reset_btn)
            edit_btn = QPushButton(translator.t("edit"))
            edit_btn.setObjectName("Ghost")
            edit_btn.clicked.connect(lambda _=False, tt=t: self._edit_target(tt))
            btn_row.addWidget(edit_btn)
            delete_btn = QPushButton(translator.t("delete"))
            delete_btn.setObjectName("Ghost")
            delete_btn.clicked.connect(lambda _=False, tid=t.id: self._delete_target(tid))
            btn_row.addWidget(delete_btn)
            card.addLayout(btn_row)

            self.list_container.addWidget(card)

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_tasbih"))
        self.add_btn.setText(translator.t("add_tasbih_target"))
        self.reset_all_btn.setText(translator.t("reset_all"))
        self.targets_title.setText(translator.t("tasbih_targets_title"))
        self.all_done_label.setText(translator.t("all_targets_completed"))
        self._refresh()
