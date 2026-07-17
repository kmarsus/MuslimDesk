from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QMainWindow,
                                QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from app.i18n import translator
from app.paths import icon_path
from app.settings import settings
from app.ui import theme
from app.ui.about_view import AboutView
from app.ui.alarm_view import AlarmView
from app.ui.asmaul_husna_view import AsmaulHusnaView
from app.ui.azkar_view import AzkarView
from app.ui.dua_view import DuaView
from app.ui.hijri_view import HijriView
from app.ui.home_view import HomeView
from app.ui.mosque_view import MosqueView
from app.ui.prayer_times_view import PrayerTimesView
from app.ui.qibla_view import QiblaView
from app.ui.settings_view import SettingsView
from app.ui.tasbih_view import TasbihView

NAV_ITEMS = [
    ("home", "nav_home", "🏠"),
    ("prayer_times", "nav_prayer_times", "🕌"),
    ("daily_azkar", "nav_daily_azkar", "📿"),
    ("dua", "nav_dua", "🤲"),
    ("asmaul_husna", "nav_asmaul_husna", "✨"),
    ("quran", "nav_quran", "📖"),
    ("hijri", "nav_hijri", "🌙"),
    ("qibla", "nav_qibla", "🧭"),
    ("mosques", "nav_mosques", "🕌"),
    ("tasbih", "nav_tasbih", "☪"),
    ("alarm", "nav_alarm", "⏰"),
    ("settings", "nav_settings", "⚙"),
    ("about", "nav_about", "ℹ"),
]


class MainWindow(QMainWindow):
    def __init__(self, scheduler, alarm_manager, available_arabic_fonts: list[str],
                 on_speed_tray_changed=None, voice_clock=None) -> None:
        super().__init__()
        self._scheduler = scheduler
        self._alarm_manager = alarm_manager
        self._on_speed_tray_changed = on_speed_tray_changed
        self._voice_clock = voice_clock
        self.setWindowTitle("MuslimDesk")
        self.resize(1180, 760)
        icon_file = icon_path("logo.png")
        if icon_file.exists():
            self.setWindowIcon(QIcon(str(icon_file)))

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._build_sidebar(root)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self._routes: dict[str, int] = {}
        self._pages: dict[str, QWidget] = {}
        self._build_pages(available_arabic_fonts)

        self._select("home")
        translator.language_changed.connect(lambda *_: self._retranslate_sidebar())
        self.apply_theme(settings.dark_mode)

    def _build_sidebar(self, root: QHBoxLayout) -> None:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.title_label = QLabel(translator.t("app_title"))
        self.title_label.setObjectName("SidebarTitle")
        layout.addWidget(self.title_label)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_buttons: dict[str, QPushButton] = {}
        for route, key, emoji in NAV_ITEMS:
            btn = QPushButton(f"  {emoji}   {translator.t(key)}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _=False, r=route: self._select(r))
            layout.addWidget(btn)
            self._nav_group.addButton(btn)
            self._nav_buttons[route] = btn
        layout.addStretch(1)

        self.footer_label = QLabel(translator.t("developed_by"))
        self.footer_label.setObjectName("SidebarFooter")
        self.footer_label.setWordWrap(True)
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.footer_label)

        root.addWidget(sidebar)

    def _build_pages(self, available_arabic_fonts: list[str]) -> None:
        def add(route: str, widget: QWidget) -> None:
            idx = self.stack.addWidget(widget)
            self._routes[route] = idx
            self._pages[route] = widget

        add("home", HomeView(self._scheduler, self._select))
        add("prayer_times", PrayerTimesView(self._scheduler, self._select))
        add("daily_azkar", AzkarView())
        add("dua", DuaView())
        add("asmaul_husna", AsmaulHusnaView())
        from app.ui.quran_view import QuranView
        add("quran", QuranView())
        add("hijri", HijriView())
        add("qibla", QiblaView())
        add("mosques", MosqueView())
        add("tasbih", TasbihView())
        add("alarm", AlarmView(self._alarm_manager))
        add("settings", SettingsView(
            self._scheduler, self.apply_theme, self.apply_arabic_font, available_arabic_fonts,
            self._on_speed_tray_changed, self._voice_clock,
        ))
        add("about", AboutView())

    def _select(self, route: str) -> None:
        if route not in self._routes:
            return
        self.stack.setCurrentIndex(self._routes[route])
        for r, btn in self._nav_buttons.items():
            btn.setChecked(r == route)

    def apply_theme(self, dark: bool) -> None:
        palette = theme.DARK if dark else theme.LIGHT
        self.setStyleSheet(theme.stylesheet(palette))

    def apply_arabic_font(self, family: str) -> None:
        if family == "System Default":
            family = QFont().family()
        for page in self._pages.values():
            if hasattr(page, "apply_font"):
                page.apply_font(family)

    def _retranslate_sidebar(self) -> None:
        self.title_label.setText(translator.t("app_title"))
        for route, key, emoji in NAV_ITEMS:
            self._nav_buttons[route].setText(f"  {emoji}   {translator.t(key)}")
        self.footer_label.setText(translator.t("developed_by"))

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        tray = getattr(self, "_tray_icon", None)
        if tray is not None:
            tray.showMessage(translator.t("app_title"), translator.t("tray_show"))

    def set_tray_icon(self, tray_icon) -> None:
        self._tray_icon = tray_icon
