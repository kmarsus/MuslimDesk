from __future__ import annotations

from PySide6.QtCore import QThread, QUrl, Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QListWidget,
                                QListWidgetItem, QPushButton, QScrollArea,
                                QVBoxLayout, QWidget)

from app.i18n import translator
from app.location import current_location
from app.mosque_finder import IpLocation, Mosque, detect_ip_location, find_nearby_mosques
from app.ui.widgets.card import Card
from app.ui.widgets.no_scroll import NoScrollComboBox, NoScrollDoubleSpinBox

RADIUS_OPTIONS_M = [1000, 2000, 3000, 5000, 10000]


class _DetectThread(QThread):
    done = Signal(object)  # IpLocation | None

    def run(self) -> None:
        self.done.emit(detect_ip_location())


class _SearchThread(QThread):
    done = Signal(list, object)  # list[Mosque], Exception | None

    def __init__(self, lat: float, lon: float, radius_m: int) -> None:
        super().__init__()
        self._lat, self._lon, self._radius_m = lat, lon, radius_m

    def run(self) -> None:
        try:
            results = find_nearby_mosques(self._lat, self._lon, self._radius_m)
            self.done.emit(results, None)
        except Exception as e:
            self.done.emit([], e)


class MosqueView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._lat: float | None = None
        self._lon: float | None = None
        self._detect_thread: _DetectThread | None = None
        self._search_thread: _SearchThread | None = None

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

        self.loc_card = Card(spacing=12)
        self.detect_btn = QPushButton()
        self.detect_btn.clicked.connect(self._detect_location)
        self.loc_card.addWidget(self.detect_btn)

        self.detected_label = QLabel()
        self.detected_label.setObjectName("Muted")
        self.detected_label.setWordWrap(True)
        self.loc_card.addWidget(self.detected_label)

        manual_row = QHBoxLayout()
        self.lat_spin = NoScrollDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(4)
        self.lon_spin = NoScrollDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(4)
        self.use_manual_btn = QPushButton()
        self.use_manual_btn.setObjectName("Ghost")
        self.use_manual_btn.clicked.connect(self._use_manual)
        manual_row.addWidget(self.lat_spin)
        manual_row.addWidget(self.lon_spin)
        manual_row.addWidget(self.use_manual_btn)
        self.loc_card.addLayout(manual_row)

        radius_row = QHBoxLayout()
        self.radius_label = QLabel()
        radius_row.addWidget(self.radius_label)
        self.radius_combo = NoScrollComboBox()
        for m in RADIUS_OPTIONS_M:
            self.radius_combo.addItem(f"{m/1000:.0f} km", m)
        self.radius_combo.setCurrentIndex(2)
        radius_row.addWidget(self.radius_combo)
        radius_row.addStretch(1)
        self.search_btn = QPushButton()
        self.search_btn.clicked.connect(self._search)
        self.search_btn.setEnabled(False)
        radius_row.addWidget(self.search_btn)
        self.loc_card.addLayout(radius_row)

        self._layout.addWidget(self.loc_card)

        self.status_label = QLabel()
        self.status_label.setObjectName("Muted")
        self._layout.addWidget(self.status_label)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._open_in_maps)
        self._layout.addWidget(self.results_list)
        self._layout.addStretch(1)

        # Pre-fill manual fields with the app's already-configured prayer-time location.
        loc = current_location()
        self.lat_spin.setValue(loc.lat)
        self.lon_spin.setValue(loc.lon)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def _detect_location(self) -> None:
        self.detect_btn.setEnabled(False)
        self.detected_label.setText(translator.t("loading"))
        self._detect_thread = _DetectThread()
        self._detect_thread.done.connect(self._on_detected)
        self._detect_thread.start()

    def _on_detected(self, loc: IpLocation | None) -> None:
        self.detect_btn.setEnabled(True)
        if loc is None:
            self.detected_label.setText(translator.t("location_detect_failed"))
            return
        self._lat, self._lon = loc.lat, loc.lon
        self.lat_spin.setValue(loc.lat)
        self.lon_spin.setValue(loc.lon)
        self.detected_label.setText(f"📍 {loc.city}, {loc.country} ({loc.lat:.4f}, {loc.lon:.4f})")
        self.search_btn.setEnabled(True)

    def _use_manual(self) -> None:
        self._lat, self._lon = self.lat_spin.value(), self.lon_spin.value()
        self.detected_label.setText(f"📍 {self._lat:.4f}, {self._lon:.4f}")
        self.search_btn.setEnabled(True)

    def _search(self) -> None:
        if self._lat is None or self._lon is None:
            return
        self.results_list.clear()
        self.status_label.setText(translator.t("loading"))
        self.search_btn.setEnabled(False)
        radius_m = self.radius_combo.currentData()
        self._search_thread = _SearchThread(self._lat, self._lon, radius_m)
        self._search_thread.done.connect(self._on_searched)
        self._search_thread.start()

    def _on_searched(self, results: list[Mosque], error) -> None:
        self.search_btn.setEnabled(True)
        if error is not None:
            self.status_label.setText(translator.t("mosque_search_failed"))
            return
        if not results:
            self.status_label.setText(translator.t("no_mosques_found"))
            return
        self.status_label.setText(translator.t("mosques_found", n=len(results)))
        for m in results:
            text = f"🕌 {m.name}  —  {m.distance_km:.1f} km"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, (m.lat, m.lon))
            item.setToolTip(translator.t("open_in_maps"))
            self.results_list.addItem(item)

    def _open_in_maps(self, item: QListWidgetItem) -> None:
        coords = item.data(Qt.ItemDataRole.UserRole)
        if not coords:
            return
        lat, lon = coords
        url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        QDesktopServices.openUrl(QUrl(url))

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_mosques"))
        self.detect_btn.setText("📍 " + translator.t("detect_location"))
        self.use_manual_btn.setText(translator.t("use_these_coordinates"))
        self.radius_label.setText(translator.t("search_radius"))
        self.search_btn.setText(translator.t("search_mosques"))
        if not self.detected_label.text():
            self.detected_label.setText(translator.t("mosque_location_hint"))
