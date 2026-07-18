from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QGridLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QScrollArea,
                                QVBoxLayout, QWidget)

from app import azan_voices
from app.i18n import translator
from app.location import cities_for_country, country_list
from app.prayer_times import CALC_METHODS
from app.settings import ALL_PRAYER_KEYS, PRAYER_KEYS, settings
from app.ui.widgets.card import Card
from app.ui.widgets.no_scroll import (NoScrollComboBox, NoScrollDoubleSpinBox,
                                       NoScrollSpinBox, make_searchable)
from app.ui.widgets.voice_picker import VoicePickerCombo

SYSTEM_DEFAULT_FONT_LABEL = "System Default"


class SettingsView(QWidget):
    def __init__(self, scheduler, on_theme_changed, on_font_changed, available_fonts: list[str],
                 on_speed_tray_changed=None, voice_clock=None,
                 available_ui_fonts: list[str] | None = None, on_ui_font_changed=None, parent=None) -> None:
        super().__init__(parent)
        self._scheduler = scheduler
        self._on_theme_changed = on_theme_changed
        self._on_font_changed = on_font_changed
        self._on_speed_tray_changed = on_speed_tray_changed
        self._voice_clock = voice_clock
        self._on_ui_font_changed = on_ui_font_changed
        self._available_fonts = [SYSTEM_DEFAULT_FONT_LABEL] + (available_fonts or ["Amiri"])
        self._available_ui_fonts = [SYSTEM_DEFAULT_FONT_LABEL] + (available_ui_fonts or ["Segoe UI"])

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(16)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        self._layout.addWidget(self.heading)

        self._build_general_card()
        self._build_voice_clock_card()
        self._build_location_card()
        self._build_method_card()
        self._build_adjustment_card()
        self._build_azan_card()
        self._build_azan_behavior_card()
        self._layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    # ── general ──────────────────────────────────────────────────────
    def _build_general_card(self) -> None:
        self.general_card = Card(spacing=16)

        lang_row = QHBoxLayout()
        self.lang_title = QLabel()
        self.lang_title.setObjectName("SectionTitle")
        lang_row.addWidget(self.lang_title)
        lang_row.addStretch(1)
        self.lang_combo = NoScrollComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("বাংলা", "bn")
        idx = self.lang_combo.findData(settings.language)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_combo)
        self.general_card.addLayout(lang_row)

        theme_row = QHBoxLayout()
        self.dark_checkbox = QCheckBox()
        self.dark_checkbox.setChecked(settings.dark_mode)
        self.dark_checkbox.toggled.connect(self._on_dark_toggled)
        theme_row.addWidget(self.dark_checkbox)
        theme_row.addStretch(1)
        self.general_card.addLayout(theme_row)

        font_row = QHBoxLayout()
        self.font_title = QLabel()
        self.font_title.setObjectName("SectionTitle")
        font_row.addWidget(self.font_title)
        font_row.addStretch(1)
        self.font_combo = NoScrollComboBox()
        self.font_combo.addItems(self._available_fonts)
        idx = self.font_combo.findText(settings.arabic_font)
        self.font_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.font_combo.currentTextChanged.connect(self._on_font_selected)
        font_row.addWidget(self.font_combo)
        self.general_card.addLayout(font_row)

        ui_font_row = QHBoxLayout()
        self.ui_font_title = QLabel()
        self.ui_font_title.setObjectName("SectionTitle")
        ui_font_row.addWidget(self.ui_font_title)
        ui_font_row.addStretch(1)
        self.ui_font_combo = NoScrollComboBox()
        self.ui_font_combo.addItems(self._available_ui_fonts)
        ui_idx = self.ui_font_combo.findText(settings.ui_font)
        self.ui_font_combo.setCurrentIndex(ui_idx if ui_idx >= 0 else 0)
        self.ui_font_combo.currentTextChanged.connect(self._on_ui_font_selected)
        ui_font_row.addWidget(self.ui_font_combo)
        self.general_card.addLayout(ui_font_row)

        minimize_row = QHBoxLayout()
        self.minimize_checkbox = QCheckBox()
        self.minimize_checkbox.setChecked(settings.start_minimized)
        self.minimize_checkbox.toggled.connect(self._on_minimize_toggled)
        minimize_row.addWidget(self.minimize_checkbox)
        minimize_row.addStretch(1)
        self.general_card.addLayout(minimize_row)

        speed_row = QHBoxLayout()
        self.speed_tray_checkbox = QCheckBox()
        self.speed_tray_checkbox.setChecked(settings.show_speed_tray)
        self.speed_tray_checkbox.toggled.connect(self._on_speed_tray_toggled)
        speed_row.addWidget(self.speed_tray_checkbox)
        speed_row.addStretch(1)
        self.general_card.addLayout(speed_row)

        self._layout.addWidget(self.general_card)

    def _on_lang_changed(self, _idx: int) -> None:
        lang = self.lang_combo.currentData()
        settings.language = lang
        translator.set_language(lang)

    def _on_dark_toggled(self, checked: bool) -> None:
        settings.dark_mode = checked
        self._on_theme_changed(checked)

    def _on_font_selected(self, family: str) -> None:
        settings.arabic_font = family
        self._on_font_changed(family)

    def _on_ui_font_selected(self, family: str) -> None:
        settings.ui_font = family
        if self._on_ui_font_changed is not None:
            self._on_ui_font_changed(family)

    def _on_minimize_toggled(self, checked: bool) -> None:
        settings.start_minimized = checked

    def _on_speed_tray_toggled(self, checked: bool) -> None:
        settings.show_speed_tray = checked
        if self._on_speed_tray_changed is not None:
            self._on_speed_tray_changed(checked)

    # ── voice clock ──────────────────────────────────────────────────
    def _build_voice_clock_card(self) -> None:
        self.voice_clock_card = Card()
        self.voice_clock_title = QLabel()
        self.voice_clock_title.setObjectName("SectionTitle")
        self.voice_clock_card.addWidget(self.voice_clock_title)

        self.voice_clock_checkbox = QCheckBox()
        self.voice_clock_checkbox.setChecked(settings.voice_clock_enabled)
        self.voice_clock_checkbox.toggled.connect(self._on_voice_clock_toggled)
        self.voice_clock_card.addWidget(self.voice_clock_checkbox)

        lang_row = QHBoxLayout()
        self.voice_clock_lang_label = QLabel()
        lang_row.addWidget(self.voice_clock_lang_label)
        self.voice_clock_lang_combo = NoScrollComboBox()
        self.voice_clock_lang_combo.addItem("বাংলা", "bn")
        self.voice_clock_lang_combo.addItem("English", "en")
        idx = self.voice_clock_lang_combo.findData(settings.voice_clock_language)
        self.voice_clock_lang_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.voice_clock_lang_combo.currentIndexChanged.connect(self._on_voice_clock_lang_changed)
        lang_row.addWidget(self.voice_clock_lang_combo)
        lang_row.addStretch(1)
        self.voice_clock_card.addLayout(lang_row)

        interval_row = QHBoxLayout()
        self.voice_clock_interval_label = QLabel()
        interval_row.addWidget(self.voice_clock_interval_label)
        self.voice_clock_interval_combo = NoScrollComboBox()
        for minutes in (15, 30, 60):
            self.voice_clock_interval_combo.addItem(f"{minutes} min", minutes)
        idx = self.voice_clock_interval_combo.findData(settings.voice_clock_interval_min)
        self.voice_clock_interval_combo.setCurrentIndex(idx if idx >= 0 else 1)
        self.voice_clock_interval_combo.currentIndexChanged.connect(self._on_voice_clock_interval_changed)
        interval_row.addWidget(self.voice_clock_interval_combo)
        interval_row.addStretch(1)
        self.voice_clock_test_btn = QPushButton()
        self.voice_clock_test_btn.setObjectName("Ghost")
        self.voice_clock_test_btn.clicked.connect(self._test_voice_clock)
        interval_row.addWidget(self.voice_clock_test_btn)
        self.voice_clock_card.addLayout(interval_row)

        self._layout.addWidget(self.voice_clock_card)

    def _on_voice_clock_toggled(self, checked: bool) -> None:
        settings.voice_clock_enabled = checked

    def _on_voice_clock_lang_changed(self, _idx: int) -> None:
        settings.voice_clock_language = self.voice_clock_lang_combo.currentData()

    def _on_voice_clock_interval_changed(self, _idx: int) -> None:
        settings.voice_clock_interval_min = self.voice_clock_interval_combo.currentData()

    def _test_voice_clock(self) -> None:
        if self._voice_clock is not None:
            self._voice_clock.announce_now()

    # ── location: country -> city ────────────────────────────────────
    def _build_location_card(self) -> None:
        self.loc_card = Card()
        self.loc_title = QLabel()
        self.loc_title.setObjectName("SectionTitle")
        self.loc_card.addWidget(self.loc_title)

        mode_row = QHBoxLayout()
        self.city_mode_btn = QPushButton()
        self.city_mode_btn.setObjectName("Ghost")
        self.city_mode_btn.setCheckable(True)
        self.manual_mode_btn = QPushButton()
        self.manual_mode_btn.setObjectName("Ghost")
        self.manual_mode_btn.setCheckable(True)
        self.city_mode_btn.clicked.connect(lambda: self._set_mode("city"))
        self.manual_mode_btn.clicked.connect(lambda: self._set_mode("manual"))
        mode_row.addWidget(self.city_mode_btn)
        mode_row.addWidget(self.manual_mode_btn)
        mode_row.addStretch(1)
        self.loc_card.addLayout(mode_row)

        picker_row = QHBoxLayout()
        self.country_combo = NoScrollComboBox()
        for c in country_list():
            self.country_combo.addItem(c["name"], c["code"])
        make_searchable(self.country_combo)
        self.country_combo.currentIndexChanged.connect(self._on_country_changed)
        picker_row.addWidget(self.country_combo, 1)

        self.city_combo = NoScrollComboBox()
        make_searchable(self.city_combo)
        self.city_combo.currentIndexChanged.connect(self._on_city_changed)
        picker_row.addWidget(self.city_combo, 1)
        self.loc_card.addLayout(picker_row)

        manual_row = QGridLayout()
        self.lat_label = QLabel()
        self.lat_spin = NoScrollDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(4)
        self.lon_label = QLabel()
        self.lon_spin = NoScrollDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(4)
        self.tz_label = QLabel()
        self.tz_spin = NoScrollDoubleSpinBox()
        self.tz_spin.setRange(-12, 14)
        self.tz_spin.setDecimals(2)
        self.manual_label_edit = QLineEdit()
        manual_row.addWidget(self.lat_label, 0, 0)
        manual_row.addWidget(self.lat_spin, 0, 1)
        manual_row.addWidget(self.lon_label, 1, 0)
        manual_row.addWidget(self.lon_spin, 1, 1)
        manual_row.addWidget(self.tz_label, 2, 0)
        manual_row.addWidget(self.tz_spin, 2, 1)
        manual_row.addWidget(self.manual_label_edit, 3, 0, 1, 2)
        self.manual_save_btn = QPushButton()
        self.manual_save_btn.clicked.connect(self._save_manual)
        manual_row.addWidget(self.manual_save_btn, 4, 0, 1, 2)
        self.loc_card.addLayout(manual_row)

        self._layout.addWidget(self.loc_card)
        self._load_location_ui()

    def _load_location_ui(self) -> None:
        is_city = settings.location_mode != "manual"
        self.city_mode_btn.setChecked(is_city)
        self.manual_mode_btn.setChecked(not is_city)
        self.country_combo.setVisible(is_city)
        self.city_combo.setVisible(is_city)
        for w in [self.lat_label, self.lat_spin, self.lon_label, self.lon_spin,
                  self.tz_label, self.tz_spin, self.manual_label_edit, self.manual_save_btn]:
            w.setVisible(not is_city)

        idx = self.country_combo.findData(settings.country_code)
        self.country_combo.blockSignals(True)
        self.country_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.country_combo.blockSignals(False)
        self._populate_cities(select_key=settings.city_key)

        self.lat_spin.setValue(settings.manual_lat)
        self.lon_spin.setValue(settings.manual_lon)
        self.tz_spin.setValue(settings.manual_tz_offset)
        self.manual_label_edit.setText(settings.manual_label)

    def _populate_cities(self, select_key: str | None = None) -> None:
        code = self.country_combo.currentData() or "BD"
        self.city_combo.blockSignals(True)
        self.city_combo.clear()
        for c in cities_for_country(code):
            label = c["name"] if c["name"] == c["name_local"] else f"{c['name']} / {c['name_local']}"
            self.city_combo.addItem(label, c["name"])
        if select_key:
            idx = self.city_combo.findData(select_key)
            if idx >= 0:
                self.city_combo.setCurrentIndex(idx)
        self.city_combo.blockSignals(False)

    def _set_mode(self, mode: str) -> None:
        settings.location_mode = mode
        self._load_location_ui()
        self._scheduler.recompute()

    def _on_country_changed(self, _idx: int) -> None:
        code = self.country_combo.currentData()
        settings.country_code = code
        self._populate_cities()
        if self.city_combo.count():
            self.city_combo.setCurrentIndex(0)
            settings.city_key = self.city_combo.currentData()
            self._scheduler.recompute()

    def _on_city_changed(self, _idx: int) -> None:
        name = self.city_combo.currentData()
        if name:
            settings.city_key = name
            self._scheduler.recompute()

    def _save_manual(self) -> None:
        settings.manual_lat = self.lat_spin.value()
        settings.manual_lon = self.lon_spin.value()
        settings.manual_tz_offset = self.tz_spin.value()
        settings.manual_label = self.manual_label_edit.text() or "Custom location"
        self._scheduler.recompute()

    # ── calc method / madhab ─────────────────────────────────────────
    def _build_method_card(self) -> None:
        self.method_card = Card()
        self.method_title = QLabel()
        self.method_title.setObjectName("SectionTitle")
        self.method_card.addWidget(self.method_title)

        self.method_combo = NoScrollComboBox()
        for m in CALC_METHODS.values():
            self.method_combo.addItem(m.label_en, m.id)
        idx = self.method_combo.findData(settings.calc_method)
        if idx >= 0:
            self.method_combo.setCurrentIndex(idx)
        self.method_combo.currentIndexChanged.connect(self._on_method_changed)
        self.method_card.addWidget(self.method_combo)

        self.madhab_title = QLabel()
        self.madhab_title.setObjectName("SubHeading")
        self.method_card.addWidget(self.madhab_title)
        madhab_row = QHBoxLayout()
        self.hanafi_btn = QPushButton()
        self.hanafi_btn.setObjectName("Ghost")
        self.hanafi_btn.setCheckable(True)
        self.shafi_btn = QPushButton()
        self.shafi_btn.setObjectName("Ghost")
        self.shafi_btn.setCheckable(True)
        self.hanafi_btn.clicked.connect(lambda: self._set_madhab("hanafi"))
        self.shafi_btn.clicked.connect(lambda: self._set_madhab("shafi"))
        madhab_row.addWidget(self.hanafi_btn)
        madhab_row.addWidget(self.shafi_btn)
        madhab_row.addStretch(1)
        self.method_card.addLayout(madhab_row)
        self._refresh_madhab_buttons()

        self._layout.addWidget(self.method_card)

    def _refresh_madhab_buttons(self) -> None:
        self.hanafi_btn.setChecked(settings.madhab == "hanafi")
        self.shafi_btn.setChecked(settings.madhab == "shafi")

    def _on_method_changed(self, _idx: int) -> None:
        settings.calc_method = self.method_combo.currentData()
        self._scheduler.recompute()

    def _set_madhab(self, madhab: str) -> None:
        settings.madhab = madhab
        self._refresh_madhab_buttons()
        self._scheduler.recompute()

    # ── manual per-prayer adjustment (+/- minutes) ───────────────────
    def _build_adjustment_card(self) -> None:
        self.adjust_card = Card()
        self.adjust_title = QLabel()
        self.adjust_title.setObjectName("SectionTitle")
        self.adjust_card.addWidget(self.adjust_title)
        self.adjust_caption = QLabel()
        self.adjust_caption.setObjectName("Muted")
        self.adjust_caption.setWordWrap(True)
        self.adjust_card.addWidget(self.adjust_caption)

        grid = QGridLayout()
        grid.setSpacing(8)
        self.adjust_card.addLayout(grid)
        self._adjust_labels: dict[str, QLabel] = {}
        self._time_preview_labels: dict[str, QLabel] = {}
        for i, key in enumerate(ALL_PRAYER_KEYS):
            label = QLabel(translator.t(f"prayer_{key}"))
            spin = NoScrollSpinBox()
            spin.setRange(-1440, 1440)  # +/- 24h -- effectively unlimited for a time-of-day shift
            spin.setSuffix(" min")
            spin.setValue(settings.prayer_offset(key))
            spin.valueChanged.connect(lambda v, k=key: self._set_offset(k, v))
            time_preview = QLabel("--:--")
            time_preview.setObjectName("Muted")
            time_preview.setStyleSheet("font-weight: 700;")
            col = (i % 3) * 3
            grid.addWidget(label, i // 3, col)
            grid.addWidget(spin, i // 3, col + 1)
            grid.addWidget(time_preview, i // 3, col + 2)
            self._adjust_labels[key] = label
            self._time_preview_labels[key] = time_preview

        self._layout.addWidget(self.adjust_card)
        self._scheduler.times_recomputed.connect(lambda *_: self._refresh_time_previews())
        self._refresh_time_previews()

    def _refresh_time_previews(self) -> None:
        times = self._scheduler.times
        if times is None:
            return
        times_map = times.as_dict()
        for key, label in self._time_preview_labels.items():
            t = times_map.get(key)
            if t is not None:
                label.setText(t.strftime("%I:%M %p"))

    def _set_offset(self, key: str, minutes: int) -> None:
        settings.set_prayer_offset(key, minutes)
        self._scheduler.recompute()

    # ── azan per-prayer settings ─────────────────────────────────────
    def _build_azan_card(self) -> None:
        self.azan_card = Card()
        self.azan_title = QLabel()
        self.azan_title.setObjectName("SectionTitle")
        self.azan_card.addWidget(self.azan_title)

        self._prayer_rows = {}
        for key in PRAYER_KEYS:
            row = QHBoxLayout()
            checkbox = QCheckBox(translator.t(f"prayer_{key}"))
            checkbox.setChecked(settings.azan_enabled_for(key))
            checkbox.toggled.connect(lambda checked, k=key: self._toggle_azan(k, checked))
            row.addWidget(checkbox)

            choices = azan_voices.FOR_FAJR if key == "fajr" else azan_voices.REGULAR
            current_id = settings.fajr_azan_voice_id if key == "fajr" else settings.azan_voice_id
            voice_combo = VoicePickerCombo(choices, current_id)
            voice_combo.voice_changed.connect(lambda vid, k=key: self._set_voice(k, vid))
            row.addWidget(voice_combo, 1)

            preview_btn = QPushButton(translator.t("preview"))
            preview_btn.clicked.connect(lambda _=False, k=key, c=voice_combo: self._preview(k, c))
            row.addWidget(preview_btn)

            stop_btn = QPushButton(translator.t("stop"))
            stop_btn.setObjectName("Ghost")
            stop_btn.clicked.connect(self._stop_preview)
            row.addWidget(stop_btn)

            self.azan_card.addLayout(row)
            self._prayer_rows[key] = (checkbox, voice_combo, preview_btn, stop_btn)

        self._layout.addWidget(self.azan_card)

    def _toggle_azan(self, key: str, checked: bool) -> None:
        settings.set_azan_enabled_for(key, checked)

    def _set_voice(self, key: str, voice_id: str) -> None:
        if key == "fajr":
            settings.fajr_azan_voice_id = voice_id
        else:
            settings.azan_voice_id = voice_id

    def _preview(self, key: str, combo: VoicePickerCombo) -> None:
        self._scheduler.preview_voice_id(combo.current_voice_id(), is_fajr=key == "fajr")

    def _stop_preview(self) -> None:
        self._scheduler.stop_preview()

    # ── azan behavior (close browsers) ───────────────────────────────
    def _build_azan_behavior_card(self) -> None:
        self.behavior_card = Card()
        self.behavior_title = QLabel()
        self.behavior_title.setObjectName("SectionTitle")
        self.behavior_card.addWidget(self.behavior_title)

        self.azan_message_label = QLabel()
        self.behavior_card.addWidget(self.azan_message_label)
        message_row = QHBoxLayout()
        self.azan_message_edit = QLineEdit(settings.azan_custom_message)
        self.azan_message_edit.setPlaceholderText(translator.t("azan_reminder_text"))
        self.azan_message_edit.textChanged.connect(self._on_azan_message_changed)
        message_row.addWidget(self.azan_message_edit, 1)
        self.azan_message_reset_btn = QPushButton()
        self.azan_message_reset_btn.setObjectName("Ghost")
        self.azan_message_reset_btn.clicked.connect(self._reset_azan_message)
        message_row.addWidget(self.azan_message_reset_btn)
        self.behavior_card.addLayout(message_row)

        self.close_browsers_checkbox = QCheckBox()
        self.close_browsers_checkbox.setChecked(settings.close_browsers_on_azan)
        self.close_browsers_checkbox.toggled.connect(self._on_close_browsers_toggled)
        self.behavior_card.addWidget(self.close_browsers_checkbox)

        self.close_browsers_caption = QLabel()
        self.close_browsers_caption.setObjectName("Muted")
        self.close_browsers_caption.setWordWrap(True)
        self.behavior_card.addWidget(self.close_browsers_caption)

        delay_row = QHBoxLayout()
        self.close_delay_label = QLabel()
        delay_row.addWidget(self.close_delay_label)
        self.close_delay_spin = NoScrollSpinBox()
        self.close_delay_spin.setRange(5, 300)
        self.close_delay_spin.setValue(settings.close_browsers_delay_sec)
        self.close_delay_spin.valueChanged.connect(self._on_close_delay_changed)
        delay_row.addWidget(self.close_delay_spin)
        delay_row.addStretch(1)
        self.behavior_card.addLayout(delay_row)

        self._layout.addWidget(self.behavior_card)

    def _on_azan_message_changed(self, text: str) -> None:
        settings.azan_custom_message = text

    def _reset_azan_message(self) -> None:
        self.azan_message_edit.clear()
        settings.azan_custom_message = ""

    def _on_close_browsers_toggled(self, checked: bool) -> None:
        settings.close_browsers_on_azan = checked

    def _on_close_delay_changed(self, v: int) -> None:
        settings.close_browsers_delay_sec = v

    # ── i18n ──────────────────────────────────────────────────────────
    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_settings"))
        self.lang_title.setText(translator.t("language"))
        self.dark_checkbox.setText(translator.t("dark_mode"))
        self.font_title.setText(translator.t("arabic_font"))
        self.ui_font_title.setText(translator.t("ui_font"))
        self.minimize_checkbox.setText(translator.t("start_minimized"))
        self.speed_tray_checkbox.setText(translator.t("show_speed_tray"))

        self.voice_clock_title.setText(translator.t("voice_clock"))
        self.voice_clock_checkbox.setText(translator.t("voice_clock_enable"))
        self.voice_clock_lang_label.setText(translator.t("language"))
        self.voice_clock_interval_label.setText(translator.t("voice_clock_interval"))
        self.voice_clock_test_btn.setText(translator.t("test"))

        self.loc_title.setText(translator.t("location"))
        self.city_mode_btn.setText(translator.t("select_city"))
        self.manual_mode_btn.setText(translator.t("manual_location"))
        self.lat_label.setText(translator.t("latitude"))
        self.lon_label.setText(translator.t("longitude"))
        self.tz_label.setText(translator.t("timezone_offset"))
        self.manual_save_btn.setText(translator.t("save"))

        self.method_title.setText(translator.t("calc_method"))
        self.madhab_title.setText(translator.t("madhab"))
        self.hanafi_btn.setText(translator.t("hanafi"))
        self.shafi_btn.setText(translator.t("shafi"))

        self.adjust_title.setText(translator.t("manual_adjustment"))
        self.adjust_caption.setText(translator.t("manual_adjustment_caption"))
        for key, label in self._adjust_labels.items():
            label.setText(translator.t(f"prayer_{key}"))

        self.azan_title.setText(translator.t("azan_settings"))
        for key, (checkbox, _combo, preview_btn, stop_btn) in self._prayer_rows.items():
            checkbox.setText(translator.t(f"prayer_{key}"))
            preview_btn.setText(translator.t("preview"))
            stop_btn.setText(translator.t("stop"))

        self.behavior_title.setText(translator.t("azan_behavior"))
        self.azan_message_label.setText(translator.t("azan_message_label"))
        self.azan_message_edit.setPlaceholderText(translator.t("azan_reminder_text"))
        self.azan_message_reset_btn.setText(translator.t("reset_default"))
        self.close_browsers_checkbox.setText(translator.t("close_browsers_on_azan"))
        self.close_browsers_caption.setText(translator.t("close_browsers_caption"))
        self.close_delay_label.setText(translator.t("close_browsers_delay"))
