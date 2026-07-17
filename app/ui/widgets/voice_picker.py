from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog

from app import azan_voices
from app.custom_sounds import UPLOAD_SENTINEL, add_custom_sound, load_custom_sounds
from app.i18n import translator
from app.ui.widgets.no_scroll import NoScrollComboBox


class VoicePickerCombo(NoScrollComboBox):
    voice_changed = Signal(str)  # voice id, never the upload sentinel

    def __init__(self, bundled: list[azan_voices.AzanVoice], current_id: str, parent=None) -> None:
        super().__init__(parent)
        self._bundled = bundled
        self._current_id = current_id
        self._repopulate()
        self.currentIndexChanged.connect(self._on_index_changed)

    def _repopulate(self) -> None:
        self.blockSignals(True)
        self.clear()
        for v in self._bundled:
            self.addItem(v.label_en, v.id)
        for c in load_custom_sounds():
            self.addItem(f"🎵 {c.label}", c.id)
        self.addItem("+ " + translator.t("upload_sound"), UPLOAD_SENTINEL)
        idx = self.findData(self._current_id)
        self.setCurrentIndex(idx if idx >= 0 else 0)
        self.blockSignals(False)

    def _on_index_changed(self, _idx: int) -> None:
        data = self.currentData()
        if data == UPLOAD_SENTINEL:
            path, _ = QFileDialog.getOpenFileName(
                self, translator.t("upload_sound"), "", "Audio files (*.mp3 *.wav *.ogg *.m4a)"
            )
            if path:
                custom = add_custom_sound(path)
                self._current_id = custom.id
                self._repopulate()
                self.voice_changed.emit(custom.id)
            else:
                # user cancelled the file dialog -- fall back to the previous selection
                self._repopulate()
            return
        self._current_id = data
        self.voice_changed.emit(data)

    def current_voice_id(self) -> str:
        return self._current_id
