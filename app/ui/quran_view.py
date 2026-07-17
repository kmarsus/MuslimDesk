from __future__ import annotations

import json

from PySide6.QtCore import QUrl, Qt
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QLineEdit,
                                QListWidget, QListWidgetItem, QPushButton,
                                QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from app.i18n import translator
from app.paths import data_path
from app.settings import settings
from app.ui.widgets.card import Card

RECITATION_CDN = "https://cdn.islamic.network/quran/audio/128/ar.alafasy/{n}.mp3"


class QuranView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._index = json.loads(data_path("quran", "surah_index.json").read_text(encoding="utf-8"))
        self._filtered = self._index
        self._current_surah: int | None = None
        self._current_data: dict | None = None

        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._playing_global_ayah: int | None = None
        self._play_buttons: dict[int, QPushButton] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        outer.addWidget(self.heading)

        self.continue_btn = QPushButton()
        self.continue_btn.clicked.connect(self._continue_reading)
        outer.addWidget(self.continue_btn)

        self.bookmark_go_btn = QPushButton()
        self.bookmark_go_btn.setObjectName("Ghost")
        self.bookmark_go_btn.clicked.connect(self._go_to_bookmark)
        outer.addWidget(self.bookmark_go_btn)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        # ── surah list page ──────────────────────────────────────────
        list_page = QWidget()
        list_layout = QVBoxLayout(list_page)
        list_layout.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit()
        self.search.textChanged.connect(self._filter)
        list_layout.addWidget(self.search)
        self.surah_list = QListWidget()
        self.surah_list.itemActivated.connect(self._open_from_item)
        list_layout.addWidget(self.surah_list)
        self.stack.addWidget(list_page)

        # ── ayah reader page ────────────────────────────────────────
        reader_page = QWidget()
        reader_layout = QVBoxLayout(reader_page)
        top_row = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setObjectName("Ghost")
        self.back_btn.clicked.connect(self._go_back_to_list)
        top_row.addWidget(self.back_btn)
        self.surah_title_label = QLabel()
        self.surah_title_label.setObjectName("SectionTitle")
        top_row.addWidget(self.surah_title_label)
        top_row.addStretch(1)
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setObjectName("Ghost")
        self.bookmark_btn.setFixedWidth(40)
        self.bookmark_btn.clicked.connect(self._toggle_bookmark)
        top_row.addWidget(self.bookmark_btn)
        reader_layout.addLayout(top_row)

        filter_row = QHBoxLayout()
        self.arabic_checkbox = QCheckBox()
        self.arabic_checkbox.setChecked(settings.quran_show_arabic)
        self.arabic_checkbox.toggled.connect(self._on_arabic_toggled)
        filter_row.addWidget(self.arabic_checkbox)
        self.translation_checkbox = QCheckBox()
        self.translation_checkbox.setChecked(settings.quran_show_translation)
        self.translation_checkbox.toggled.connect(self._on_translation_toggled)
        filter_row.addWidget(self.translation_checkbox)
        self.recitation_checkbox = QCheckBox()
        self.recitation_checkbox.setChecked(settings.quran_show_recitation)
        self.recitation_checkbox.toggled.connect(self._on_recitation_toggled)
        filter_row.addWidget(self.recitation_checkbox)
        filter_row.addStretch(1)
        self.stop_btn = QPushButton()
        self.stop_btn.setObjectName("Ghost")
        self.stop_btn.clicked.connect(self._stop_playback)
        self.stop_btn.setVisible(False)
        filter_row.addWidget(self.stop_btn)
        reader_layout.addLayout(filter_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        reader_layout.addWidget(scroll)
        self.ayah_container = QWidget()
        self.ayah_layout = QVBoxLayout(self.ayah_container)
        self.ayah_layout.setSpacing(10)
        scroll.setWidget(self.ayah_container)
        self.stack.addWidget(reader_page)

        self._populate_list()
        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    # ── list page ────────────────────────────────────────────────────
    def _populate_list(self) -> None:
        self.surah_list.clear()
        for s in self._filtered:
            label = f"{s['number']}. {s['englishName']} ({s['name']}) — {s['numberOfAyahs']}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, s["number"])
            self.surah_list.addItem(item)

    def _filter(self, text: str) -> None:
        text = text.strip().lower()
        if not text:
            self._filtered = self._index
        else:
            self._filtered = [
                s for s in self._index
                if text in s["englishName"].lower() or text in s["englishNameTranslation"].lower()
                or text in str(s["number"])
            ]
        self._populate_list()

    def _open_from_item(self, item: QListWidgetItem) -> None:
        self._open_surah(item.data(Qt.ItemDataRole.UserRole))

    def _continue_reading(self) -> None:
        self._open_surah(settings.last_read_surah)

    def _go_to_bookmark(self) -> None:
        if settings.bookmark_surah:
            self._open_surah(settings.bookmark_surah)

    def _go_back_to_list(self) -> None:
        self._stop_playback()
        self.stack.setCurrentIndex(0)

    # ── reader page ──────────────────────────────────────────────────
    def _open_surah(self, number: int) -> None:
        self._stop_playback()
        self._current_surah = number
        settings.last_read_surah = number
        self._current_data = json.loads(data_path("quran", f"surah_{number:03d}.json").read_text(encoding="utf-8"))

        self.surah_title_label.setText(f"{self._current_data['englishName']} — {self._current_data['name']}")
        self._update_bookmark_icon()
        self._render_ayahs()
        self.stack.setCurrentIndex(1)

    def _update_bookmark_icon(self) -> None:
        is_bookmarked = self._current_surah is not None and settings.bookmark_surah == self._current_surah
        self.bookmark_btn.setText("★" if is_bookmarked else "☆")

    def _toggle_bookmark(self) -> None:
        if self._current_surah is None:
            return
        settings.bookmark_surah = 0 if settings.bookmark_surah == self._current_surah else self._current_surah
        self._update_bookmark_icon()
        self.retranslate()

    def _on_arabic_toggled(self, checked: bool) -> None:
        settings.quran_show_arabic = checked
        self._render_ayahs()

    def _on_translation_toggled(self, checked: bool) -> None:
        settings.quran_show_translation = checked
        self._render_ayahs()

    def _on_recitation_toggled(self, checked: bool) -> None:
        settings.quran_show_recitation = checked
        if not checked:
            self._stop_playback()
        self._render_ayahs()

    def _clear_ayah_layout(self) -> None:
        while self.ayah_layout.count():
            item = self.ayah_layout.takeAt(0)
            w = item.widget()
            if w:
                # setParent(None) detaches it from the visible tree immediately
                # (deleteLater() alone leaves it lingering in the layout until
                # the event loop next runs, which can render as an overlap if
                # this is called right before a repaint/grab).
                w.setParent(None)
                w.deleteLater()
        self._play_buttons.clear()

    def _render_ayahs(self) -> None:
        if self._current_data is None:
            return
        self._clear_ayah_layout()
        data = self._current_data
        show_ar = settings.quran_show_arabic
        show_tr = settings.quran_show_translation
        show_recite = settings.quran_show_recitation

        if show_recite:
            self._render_card_mode(data, show_ar, show_tr)
        else:
            self._render_paragraph_mode(data, show_ar, show_tr)

    def _render_card_mode(self, data: dict, show_ar: bool, show_tr: bool) -> None:
        first_global = data.get("firstGlobalAyah", 0)
        for ayah in data["ayahs"]:
            card = Card(margins=14, spacing=6)
            top = QHBoxLayout()
            num = QLabel(f"{data['number']}:{ayah['n']}")
            num.setObjectName("Muted")
            top.addWidget(num)
            top.addStretch(1)
            global_n = first_global + ayah["n"] - 1
            play_btn = QPushButton("▶")
            play_btn.setObjectName("Ghost")
            play_btn.setFixedWidth(36)
            play_btn.clicked.connect(lambda _=False, g=global_n: self._play_from(g))
            top.addWidget(play_btn)
            card.addLayout(top)
            self._play_buttons[global_n] = play_btn

            if show_ar:
                arabic = QLabel(ayah["ar"])
                arabic.setObjectName("Arabic")
                arabic.setWordWrap(True)
                arabic.setAlignment(Qt.AlignmentFlag.AlignRight)
                arabic.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
                f = arabic.font()
                f.setFamily(settings.arabic_font)
                f.setPointSize(17)
                arabic.setFont(f)
                card.addWidget(arabic)
            if show_tr:
                bn = QLabel(ayah.get("bn", ""))
                bn.setWordWrap(True)
                card.addWidget(bn)
            self.ayah_layout.addWidget(card)
        self._highlight_playing()

    def _render_paragraph_mode(self, data: dict, show_ar: bool, show_tr: bool) -> None:
        """Clean continuous-paragraph reading layout (no recitation controls)."""
        if show_ar:
            card = Card(margins=18, spacing=10)
            title = QLabel(translator.t("arabic_text"))
            title.setObjectName("SubHeading")
            card.addWidget(title)
            arabic_text = " ".join(f"{a['ar']} ﴿{a['n']}﴾" for a in data["ayahs"])
            arabic = QLabel(arabic_text)
            arabic.setObjectName("Arabic")
            arabic.setWordWrap(True)
            arabic.setAlignment(Qt.AlignmentFlag.AlignRight)
            arabic.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            f = arabic.font()
            f.setFamily(settings.arabic_font)
            f.setPointSize(17)
            arabic.setFont(f)
            card.addWidget(arabic)
            self.ayah_layout.addWidget(card)

        if show_tr:
            card = Card(margins=18, spacing=10)
            title = QLabel(translator.t("translation"))
            title.setObjectName("SubHeading")
            card.addWidget(title)
            translation_text = " ".join(f"({a['n']}) {a.get('bn', '')}" for a in data["ayahs"])
            tr = QLabel(translation_text)
            tr.setWordWrap(True)
            tr.setStyleSheet("line-height: 1.6;")
            card.addWidget(tr)
            self.ayah_layout.addWidget(card)

    # ── recitation playback ──────────────────────────────────────────
    def _play_from(self, global_ayah: int) -> None:
        self._playing_global_ayah = global_ayah
        self._player.setSource(QUrl(RECITATION_CDN.format(n=global_ayah)))
        self._player.play()
        self.stop_btn.setVisible(True)
        self._highlight_playing()

    def _stop_playback(self) -> None:
        self._player.stop()
        self._playing_global_ayah = None
        self.stop_btn.setVisible(False)
        self._highlight_playing()

    def _highlight_playing(self) -> None:
        for global_n, btn in self._play_buttons.items():
            btn.setText("⏸" if global_n == self._playing_global_ayah else "▶")

    def _on_media_status_changed(self, status) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._playing_global_ayah is not None:
            data = self._current_data
            if data is None:
                return
            first_global = data.get("firstGlobalAyah", 0)
            last_global = first_global + len(data["ayahs"]) - 1
            next_ayah = self._playing_global_ayah + 1
            if next_ayah <= last_global:
                self._play_from(next_ayah)
            else:
                self._stop_playback()

    def apply_font(self, family: str) -> None:
        self._render_ayahs()

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_quran"))
        self.continue_btn.setText(f"▶ {translator.t('continue_reading')}")
        self.bookmark_go_btn.setText("★ " + translator.t("go_to_bookmark"))
        self.bookmark_go_btn.setVisible(bool(settings.bookmark_surah))
        self.search.setPlaceholderText(translator.t("search"))
        self.back_btn.setText("← " + translator.t("surah_list"))
        self.arabic_checkbox.setText(translator.t("arabic_text"))
        self.translation_checkbox.setText(translator.t("translation"))
        self.recitation_checkbox.setText(translator.t("recitation"))
        self.stop_btn.setText("⏹ " + translator.t("stop"))
