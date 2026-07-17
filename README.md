# MuslimDesk

A Windows desktop companion to the [IOM Daily Azkar](https://github.com/kmarsus/app-iom-daily-azkar) Android app — daily azkar, five-times-daily azan, Qur'an, Asmaul Husna, Hijri calendar, Qibla direction, nearby mosques, an alarm clock, and more, running quietly from the system tray.

## Features

- **Prayer times** — offline astronomical calculation (12 calculation methods, Hanafi/Shafi madhab), manual per-prayer time adjustment, country → city picker (offline, 244 countries) or manual lat/lon.
- **5x daily Azan** — background scheduler plays your chosen recitation (7 bundled voices or your own uploaded MP3) at each prayer time, even while minimized to tray. A full-screen, always-on-top notification appears when Azan starts.
- **Daily Azkar** — the complete IOM Daily Azkar and Self-Ruqyah collections, with reading-count badges, a Next button, and English translations.
- **Dua & Hadith** — bundled offline, no internet required.
- **Al-Qur'an** — independent Arabic / Translation / Recitation toggles, live Mishary Alafasy recitation, paragraph reading mode, bookmarks.
- **Asmaul Husna**, **Hijri calendar** with Islamic events, **Qibla compass**, **Tasbih counter**.
- **Nearby Mosques** — IP-based or manual location, live results from OpenStreetMap.
- **Alarm Clock** — repeatable alarms with an optional "shut down PC" countdown.
- **Voice Clock** — announces the time out loud every 15/30/60 minutes.
- **Taskbar internet speed meter** — optional, docks next to the system tray.
- Bengali/English UI, light/dark theme, selectable Arabic and system fonts.

## Running from source

```
pip install -r requirements.txt
python main.py
```

Requires Windows and Python 3.11+.

## Building the .exe

```
pip install pyinstaller
python -m PyInstaller MuslimDesk.spec --noconfirm
```

The built app appears under `dist/MuslimDesk/`.

## Project layout

- `main.py` — application entry point.
- `app/` — core logic (prayer-time calculation, azan scheduling, settings, i18n, etc.) and `app/ui/` (PySide6 screens).
- `assets/data/` — bundled offline content (azkar, Qur'an, Asmaul Husna, Hijri events, world city list).
- `assets/audio/`, `assets/fonts/`, `assets/icons/` — bundled azan recordings, Arabic/Bengali fonts, and app icon.
- `scripts/` — one-off scripts used to generate the bundled data assets from source data.

---

Developed by Engr. Maw. Khandaker Marsus
