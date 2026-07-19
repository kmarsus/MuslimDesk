from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QLabel, QMessageBox, QProgressBar,
                                QPushButton, QVBoxLayout, QWidget)

from app import pc_cleaner
from app.i18n import translator
from app.ui.widgets.card import Card


class _CleanWorker(QThread):
    """Runs the (potentially slow, e.g. large Temp folders) cleaning
    functions off the UI thread so the window doesn't freeze and the user
    can't fire off a second clean by clicking again while one is running."""
    finished_with_results = Signal(list)  # list[tuple[str, int]] of (i18n key, bytes freed)

    def __init__(self, targets: list[tuple[str, object]], parent=None) -> None:
        super().__init__(parent)
        self._targets = targets

    def run(self) -> None:
        results = [(key, cleaner()) for key, cleaner in self._targets]
        self.finished_with_results.emit(results)


class PcCleanView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.caption = QLabel()
        self.caption.setObjectName("Muted")
        self.caption.setWordWrap(True)
        layout.addWidget(self.caption)

        self.clean_card = Card(spacing=8)
        self.temp_checkbox = QCheckBox()
        self.temp_checkbox.setChecked(True)
        self.clean_card.addWidget(self.temp_checkbox)

        self.chrome_checkbox = QCheckBox()
        self.chrome_checkbox.setVisible(pc_cleaner.chrome_cache_exists())
        self.clean_card.addWidget(self.chrome_checkbox)

        self.edge_checkbox = QCheckBox()
        self.edge_checkbox.setVisible(pc_cleaner.edge_cache_exists())
        self.clean_card.addWidget(self.edge_checkbox)

        self.firefox_checkbox = QCheckBox()
        self.firefox_checkbox.setVisible(pc_cleaner.firefox_cache_exists())
        self.clean_card.addWidget(self.firefox_checkbox)

        self.clean_btn = QPushButton()
        self.clean_btn.clicked.connect(self._on_clean_clicked)
        self.clean_card.addWidget(self.clean_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate -- we don't know byte counts up front
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setVisible(False)
        self.clean_card.addWidget(self.progress_bar)
        layout.addWidget(self.clean_card)

        self._worker: _CleanWorker | None = None

        self.recycle_card = Card(spacing=8)
        self.recycle_caption = QLabel()
        self.recycle_caption.setObjectName("Muted")
        self.recycle_caption.setWordWrap(True)
        self.recycle_card.addWidget(self.recycle_caption)
        self.recycle_btn = QPushButton()
        self.recycle_btn.setObjectName("Ghost")
        self.recycle_btn.clicked.connect(self._on_empty_recycle_bin_clicked)
        self.recycle_card.addWidget(self.recycle_btn)
        layout.addWidget(self.recycle_card)

        self.results_label = QLabel()
        self.results_label.setObjectName("Muted")
        self.results_label.setWordWrap(True)
        layout.addWidget(self.results_label)

        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _on_clean_clicked(self) -> None:
        if self._worker is not None:
            return  # already cleaning -- ignore a double click instead of starting a second run

        targets = []
        if self.temp_checkbox.isChecked():
            targets.append(("pc_clean_windows_temp", pc_cleaner.clean_windows_temp))
        if self.chrome_checkbox.isVisible() and self.chrome_checkbox.isChecked():
            targets.append(("pc_clean_chrome_cache", pc_cleaner.clean_chrome_cache))
        if self.edge_checkbox.isVisible() and self.edge_checkbox.isChecked():
            targets.append(("pc_clean_edge_cache", pc_cleaner.clean_edge_cache))
        if self.firefox_checkbox.isVisible() and self.firefox_checkbox.isChecked():
            targets.append(("pc_clean_firefox_cache", pc_cleaner.clean_firefox_cache))

        if not targets:
            self.results_label.setText(translator.t("pc_clean_nothing_selected"))
            return

        self.clean_btn.setEnabled(False)
        self.clean_btn.setText(translator.t("pc_clean_cleaning"))
        self.recycle_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.results_label.setText("")

        self._worker = _CleanWorker(targets, self)
        self._worker.finished_with_results.connect(self._on_clean_finished)
        self._worker.start()

    def _on_clean_finished(self, results: list) -> None:
        self._worker = None
        self.progress_bar.setVisible(False)
        self.clean_btn.setEnabled(True)
        self.recycle_btn.setEnabled(True)
        self.clean_btn.setText(translator.t("pc_clean_clean_selected"))

        total = sum(freed for _key, freed in results)
        lines = [
            translator.t("pc_clean_freed").format(name=translator.t(key), size=pc_cleaner.format_bytes(freed))
            for key, freed in results
        ]
        lines.append(translator.t("pc_clean_done_message").format(size=pc_cleaner.format_bytes(total)))
        self.results_label.setText("\n".join(lines))

    def _on_empty_recycle_bin_clicked(self) -> None:
        reply = QMessageBox.question(
            self, translator.t("pc_clean_recycle_bin"), translator.t("pc_clean_confirm_recycle_bin"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.recycle_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)
        pc_cleaner.empty_recycle_bin()
        self.recycle_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)
        self.results_label.setText(translator.t("pc_clean_recycle_bin_emptied"))

    def retranslate(self) -> None:
        self.heading.setText(translator.t("pc_clean_heading"))
        self.caption.setText(translator.t("pc_clean_caption"))
        self.temp_checkbox.setText(translator.t("pc_clean_windows_temp"))
        self.chrome_checkbox.setText(translator.t("pc_clean_chrome_cache"))
        self.edge_checkbox.setText(translator.t("pc_clean_edge_cache"))
        self.firefox_checkbox.setText(translator.t("pc_clean_firefox_cache"))
        if self._worker is None:
            self.clean_btn.setText(translator.t("pc_clean_clean_selected"))
        self.recycle_caption.setText(translator.t("pc_clean_recycle_bin_caption"))
        self.recycle_btn.setText(translator.t("pc_clean_empty_recycle_bin_btn"))
