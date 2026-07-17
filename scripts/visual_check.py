"""Renders each page to a PNG via QWidget.grab() for visual review, without
needing OS-level screenshot/automation tooling."""
import sys

sys.path.insert(0, r"C:\Claude\MuslimDesk")

from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

from app.alarm_manager import AlarmManager
from app.azan_scheduler import AzanScheduler
from app.i18n import translator
from app.settings import settings
from main import _load_fonts
from app.ui.main_window import MainWindow

translator.set_language(settings.language)
_all, arabic_fonts = _load_fonts()

scheduler = AzanScheduler()
alarm_manager = AlarmManager()
window = MainWindow(scheduler, alarm_manager, arabic_fonts or ["Amiri"])
window.resize(1180, 760)
window.show()
app.processEvents()

routes = ["prayer_times", "settings"]
for route in routes:
    window._select(route)
    app.processEvents()
    if route == "quran":
        # open a surah so the reader page has content
        window._pages["quran"]._open_surah(1)
        app.processEvents()
    pix = window.grab()
    out = rf"C:\Claude\MuslimDesk\shots\{route}.png"
    pix.save(out)
    print("saved", out)

# also grab dua after its background fetch has had a moment to complete
import time
window._select("dua")
for _ in range(30):
    app.processEvents()
    time.sleep(0.1)
pix = window.grab()
pix.save(r"C:\Claude\MuslimDesk\shots\dua.png")
print("saved dua")

print("ALL DONE")
