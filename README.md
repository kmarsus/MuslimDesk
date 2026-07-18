# MuslimDesk — Free Open Source Islamic Prayer Times & Azan App for Windows

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)
![Framework](https://img.shields.io/badge/Framework-PySide6-purple.svg)
![Privacy](https://img.shields.io/badge/privacy-offline--first-brightgreen.svg)

**MuslimDesk** is a free, open-source Windows desktop application for Muslims. It brings accurate **prayer times (Salah/Namaz)**, automatic **Azan (Adhan) reminders**, the **Holy Qur'an**, **daily Azkar and Duas**, **Hijri calendar**, **Qibla direction**, a **Tasbih counter**, and a **nearby mosque finder** to the Windows desktop.

The application runs quietly in the system tray, calculates prayer times fully offline, and can automatically play the Azan for the five daily prayers.

MuslimDesk is designed as a desktop Islamic companion similar in purpose to popular mobile prayer-time applications, while remaining free, open source, privacy-friendly, and optimized for Windows.

It is a companion project to the [IOM Daily Azkar](https://github.com/kmarsus/app-iom-daily-azkar) Android application and is built with Python and PySide6.

## Releases

The latest version is available from the GitHub Releases page:

https://github.com/kmarsus/MuslimDesk/releases

Open the latest release and check the **Assets** section for the Windows installer, portable application, and checksum files.

## Main Features

- Accurate daily prayer times
- Fajr, Sunrise, Dhuhr, Asr, Maghrib, and Isha schedules
- Automatic Azan playback
- Multiple prayer calculation methods
- Hanafi and standard Asr calculation options
- Country and city selection
- Manual latitude and longitude support
- Automatic location-based prayer-time calculation
- Fully offline prayer-time calculation
- Custom adjustment for individual prayer times
- User-selectable Azan audio
- Optional foreground notification when Azan begins
- System tray operation
- Start automatically with Windows
- Windows dark and light theme support
- Daily Azkar and Duas
- Reading-count indicators for Azkar
- Next and previous navigation between Duas
- Holy Qur'an reading section
- Qur'an filtering and search
- Hijri calendar
- Qibla direction finder
- Tasbih counter
- Nearby mosque finder
- Bengali and English interface support
- Privacy-friendly design
- No advertisements
- No unnecessary tracking

## Prayer Times

MuslimDesk calculates prayer times based on the selected location and calculation method.

Supported prayer entries include:

- Fajr
- Sunrise
- Dhuhr
- Asr
- Maghrib
- Isha

Users may select a country and city, provide custom coordinates, choose an appropriate calculation method, and manually adjust prayer times where necessary.

Prayer-time settings are available from the application settings section.

Mouse-wheel changes may be disabled on sensitive time-setting fields to prevent accidental modification.

## Azan Notifications

MuslimDesk can automatically play the Azan when a prayer time begins.

Available Azan-related options may include:

- Enable or disable Azan for each prayer
- Select a built-in Azan
- Upload a custom Azan MP3 file
- Show the notification window above other windows
- Display a reminder to stop work and prepare for Salah
- Enable or disable automatic application actions during Azan
- Configure startup and notification behavior

A notification message may remind users:

> Azan is being called. Please pause your work, respond to the Muazzin, and prepare for Salah. Once the Azan has begun, giving priority to Salah over other work is the duty of a believer.

## Daily Azkar and Duas

The Daily Azkar section includes Islamic remembrances and authentic Duas.

Features may include:

- Arabic text
- Bengali translation
- English interface support
- Reading-count instructions
- Examples such as one time, three times, or another recommended count
- Next and previous navigation
- Completion tracking
- Morning and evening Azkar
- Selected Duas from the Qur'an and Hadith

The original Arabic and Bengali Dua content remains available even when the application interface is switched to English.

## Holy Qur'an

The Qur'an section may include:

- Surah list
- Arabic text
- Bengali translation
- Search and filtering
- Bookmarking
- Reading progress
- Selected Surahs and Ayahs
- Offline access

## Hijri Calendar

The Hijri calendar section may display:

- Current Hijri date
- Gregorian date
- Islamic months
- Important Islamic dates
- Optional local Hijri-date adjustment

Because moon sighting may differ by location, the application may allow users to adjust the Hijri date manually.

## Qibla Direction

The Qibla section helps users identify the direction of the Ka'bah based on their selected location or coordinates.

Accuracy may depend on:

- Correct latitude and longitude
- Device orientation
- Available Windows sensor support
- Manually selected location

## Tasbih Counter

The Tasbih counter provides a simple digital counter for Dhikr.

Possible controls include:

- Increase count
- Reset count
- Select a target
- Save the current count
- Choose common Dhikr phrases

## Nearby Mosque Finder

The mosque finder may help users locate nearby mosques using their selected location.

Internet access may be required only for map-based or online nearby-mosque results. Core prayer-time calculation remains available offline.

## Privacy

MuslimDesk is designed with privacy in mind.

The application does not need to inspect personal files or monitor browsing activity.

Core prayer-time calculation can work without an internet connection.

Depending on the enabled features, internet access may be used for:

- Nearby mosque search
- Map services
- Update checking
- Optional online Qur'an content
- Optional location lookup

Users may review the source code to understand how data is handled.

## Installation

Visit the GitHub Releases page:

https://github.com/kmarsus/MuslimDesk/releases

Then:

1. Open the latest release.
2. Expand the **Assets** section.
3. Select the appropriate Windows package.
4. Save the file to your computer.
5. Run the installer or portable application.
6. Complete the initial location and prayer-time settings.

Python is not required when using a packaged Windows release.

## Windows SmartScreen Notice

MuslimDesk may initially display a Microsoft Defender SmartScreen warning if the Windows executable is unsigned or has not yet established sufficient reputation.

Users may:

- Review the source code
- Verify the published checksum
- Build the application from source
- Download packages only from the official GitHub Releases page

A future digitally signed version may display a verified publisher name.

## Run from Source

### Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Git
- PySide6
- Other dependencies listed in `requirements.txt`

Clone the repository:

```powershell
git clone https://github.com/kmarsus/MuslimDesk.git
cd MuslimDesk
