import sys
sys.path.insert(0, r"C:\Claude\MuslimDesk")

from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

from app.alarms import Alarm
from app.alarm_manager import AlarmManager
from app.i18n import translator
from app.settings import settings
from main import _load_fonts
from app.ui.main_window import MainWindow
from app.ui.widgets.alarm_edit_dialog import AlarmEditDialog
from app.ui.widgets.alarm_ring_dialog import AlarmRingDialog
from app.azan_scheduler import AzanScheduler

translator.set_language(settings.language)
_all, arabic_fonts = _load_fonts()

alarm_manager = AlarmManager()
alarm_manager.add_or_update(Alarm(time="06:30", label="Fajr wake-up", weekdays=[0, 1, 2, 3, 4],
                                   shutdown_on_ring=True, shutdown_delay_sec=30))
alarm_manager.add_or_update(Alarm(time="22:00", label="", weekdays=[]))

scheduler = AzanScheduler()
window = MainWindow(scheduler, alarm_manager, arabic_fonts or ["Amiri"])
window.resize(1180, 760)
window.show()
window._select("alarm")
app.processEvents()
window.grab().save(r"C:\Claude\MuslimDesk\shots\alarm_with_entries.png")
print("saved alarm list")

edit_dialog = AlarmEditDialog(parent=window)
edit_dialog.show()
app.processEvents()
edit_dialog.grab().save(r"C:\Claude\MuslimDesk\shots\alarm_edit_dialog.png")
print("saved edit dialog")
edit_dialog.close()

ring_dialog = AlarmRingDialog(alarm_manager.alarms[0], parent=window)
ring_dialog.show()
app.processEvents()
ring_dialog.grab().save(r"C:\Claude\MuslimDesk\shots\alarm_ring_dialog.png")
print("saved ring dialog")
ring_dialog._stop()

print("DONE")
