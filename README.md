# MuslimDesk — Free Open Source Islamic Prayer Times & Azan App for Windows

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](#download)

**MuslimDesk** is a free, open-source Windows desktop app for Muslims — an all-in-one Islamic companion bringing accurate **prayer times (Salah/Namaz)**, automatic **Azan (Adhan) reminders**, the **Holy Qur'an**, **daily Azkar & Duas**, **Hijri (Islamic) calendar**, **Qibla direction finder**, a **Tasbih counter**, and **nearby mosque finder** to your PC taskbar. It runs quietly in the system tray, calculates prayer times fully **offline** (no internet required), and plays the Azan automatically five times a day — even while minimized.

Think of it as a Windows equivalent to popular mobile Muslim/Azan apps (like Muslim Pro or Athan), purpose-built for the desktop. It's a companion to the [IOM Daily Azkar](https://github.com/kmarsus/app-iom-daily-azkar) Android app, rebuilt from the ground up for Windows in Python/PySide6.

**Keywords:** Islamic prayer times app for Windows, Azan reminder software, Namaz time Windows desktop app, free Muslim prayer app, offline Qur'an reader for PC, Qibla direction finder Windows, Hijri calendar converter, Tasbih counter app, Islamic azkar and dua app, open source Islamic software.

## Download

**[⬇ Download MuslimDesk.exe (v1.0.1)](https://github.com/kmarsus/MuslimDesk/releases/download/v1.0.1/MuslimDesk.exe)** — standalone, no installation required, no Python needed.

Release notes: [v1.0.1](https://github.com/kmarsus/MuslimDesk/releases/tag/v1.0.1)

## Screenshots

<table>
<tr>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/01_home.png" alt="MuslimDesk Windows app Home screen showing today's prayer times and Hijri date"><p align="center"><b>Home</b> — today's prayer times &amp; Hijri date</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/02_prayer_times.png" alt="MuslimDesk offline prayer times (Salah/Namaz) screen for Windows"><p align="center"><b>Prayer Times</b> — offline calculation</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/03_daily_azkar.png" alt="MuslimDesk Daily Azkar and Tibbe Nabawi ruqyah screen"><p align="center"><b>Daily Azkar</b> — Hefazoter Amol &amp; Tibbe Nabawi</p></td>
</tr>
<tr>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/06_quran.png" alt="MuslimDesk offline Al-Quran reader for Windows with Arabic text and translation"><p align="center"><b>Al-Qur'an</b> — offline reader with translation &amp; recitation</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/07_hijri_calendar.png" alt="MuslimDesk Hijri Islamic calendar with Ayyam al-Bidh fasting days marked"><p align="center"><b>Hijri Calendar</b> — Islamic events &amp; fasting days</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/08_qibla.png" alt="MuslimDesk Qibla direction compass for Windows"><p align="center"><b>Qibla Direction</b> — compass finder</p></td>
</tr>
<tr>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/09_nearby_mosques.png" alt="MuslimDesk nearby mosque finder screen"><p align="center"><b>Nearby Mosques</b> — find mosques near you</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/10_tasbih.png" alt="MuslimDesk multi-target Tasbih dhikr counter"><p align="center"><b>Tasbih Counter</b> — multi-target dhikr counter</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/12_settings.png" alt="MuslimDesk settings screen with language, azan voice, and location options"><p align="center"><b>Settings</b> — language, azan voice &amp; location</p></td>
</tr>
</table>

<details>
<summary>More screenshots (Dua &amp; Hadith, Asmaul Husna, Alarm Clock, About)</summary>
<table>
<tr>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/04_dua.png" alt="MuslimDesk Dua and Hadith offline screen"><p align="center"><b>Dua &amp; Hadith</b></p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/05_asmaul_husna.png" alt="MuslimDesk 99 Names of Allah Asmaul Husna screen"><p align="center"><b>Asmaul Husna</b> — the 99 Names</p></td>
<td width="33%"><img src="https://raw.githubusercontent.com/kmarsus/MuslimDesk/main/docs/screenshots/11_alarm.png" alt="MuslimDesk alarm clock screen for Windows"><p align="center"><b>Alarm Clock</b></p></td>
</tr>
</table>
</details>

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
- Starts automatically with Windows and runs continuously from the tray so azan/alarms are never missed — there's no Exit option; uninstalling (or Task Manager) is the only way to stop it.

## Installation & Usage

1. [Download `MuslimDesk.exe`](https://github.com/kmarsus/MuslimDesk/releases/download/v1.0.1/MuslimDesk.exe) — it's a single portable file, no installer needed.
2. Double-click to run it. Windows SmartScreen may warn about an unrecognized publisher (this is expected for an unsigned open-source app) — click **More info → Run anyway**.
3. On first launch, open **Settings** to set your location (country/city or manual coordinates), calculation method, madhab, azan voice, and language (Bengali/English).
4. The app minimizes to the system tray and keeps running in the background so it can play the Azan and any alarms at the right time — click the tray icon to reopen the window.
5. MuslimDesk registers itself to start automatically with Windows (per-user, no admin rights needed). To uninstall, simply delete the `.exe` and remove the `MuslimDesk` entry it created under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (or run the app once and use a future uninstaller, if packaged as one).

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

The built app appears as a single file, `dist/MuslimDesk.exe`.

## Project layout

- `main.py` — application entry point.
- `app/` — core logic (prayer-time calculation, azan scheduling, settings, i18n, etc.) and `app/ui/` (PySide6 screens).
- `assets/data/` — bundled offline content (azkar, Qur'an, Asmaul Husna, Hijri events, world city list).
- `assets/audio/`, `assets/fonts/`, `assets/icons/` — bundled azan recordings, Arabic/Bengali fonts, and app icon.
- `scripts/` — one-off scripts used to generate the bundled data assets from source data.

## Performance notes

- Screens are constructed lazily on first visit (not all 13 at startup) -- only Home builds eagerly.
- All background schedulers (azan, alarms, voice clock) poll on 10-15s timers, not per-second; the only 1s
  timers are the live countdown on the Home screen (paused via `hideEvent` while another page is showing)
  and the optional taskbar speed meter (only runs at all if that setting is enabled).
- No telemetry, no background network polling beyond features you explicitly use (Dua/Hadith content and
  prayer-time/azan data are fully offline; only Nearby Mosques and Qur'an recitation touch the network, and
  only when you open those screens).

## Microsoft Store readiness

Already in place: settings/cache live under `%LOCALAPPDATA%\MuslimDesk` (the sandboxed-writable location
Store apps are expected to use), no admin rights required (the auto-start registration is a per-user
`HKCU\...\Run` key, not a system-level change), and an MIT `LICENSE`.

Still needed before submission: the Store requires an **MSIX package**, not a raw PyInstaller `.exe` --
that means adding a signed `AppxManifest.xml` (app identity, capabilities, tile assets) and packaging with
`makeappx`/`MSIX Packaging Tool`, plus a code-signing certificate. That's a separate packaging step layered
on top of this build, not a code change -- happy to set it up when you're ready to submit.

---

Developed by Engr. Maw. Khandaker Marsus
