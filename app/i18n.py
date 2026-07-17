"""Minimal EN/BN string table + a QObject-based signal so widgets can
refresh their text when the user switches language at runtime."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

_STRINGS: dict[str, dict[str, str]] = {
    "app_title": {"en": "MuslimDesk", "bn": "মুসলিমডেস্ক"},
    "nav_home": {"en": "Home", "bn": "হোম"},
    "nav_prayer_times": {"en": "Prayer Times", "bn": "নামাজের সময়"},
    "nav_daily_azkar": {"en": "Daily Azkar", "bn": "দৈনিক আযকার"},
    "nav_dua": {"en": "Dua & Hadith", "bn": "দোয়া ও হাদিস"},
    "nav_asmaul_husna": {"en": "Asmaul Husna", "bn": "আসমাউল হুসনা"},
    "nav_quran": {"en": "Al-Quran", "bn": "আল-কুরআন"},
    "nav_hijri": {"en": "Hijri Calendar", "bn": "হিজরি ক্যালেন্ডার"},
    "nav_qibla": {"en": "Qibla Direction", "bn": "কিবলা দিক"},
    "nav_tasbih": {"en": "Tasbih Counter", "bn": "তাসবীহ কাউন্টার"},
    "nav_alarm": {"en": "Alarm Clock", "bn": "অ্যালার্ম ঘড়ি"},
    "nav_mosques": {"en": "Nearby Mosques", "bn": "কাছের মসজিদ"},
    "detect_location": {"en": "Detect my location", "bn": "আমার অবস্থান শনাক্ত করুন"},
    "use_these_coordinates": {"en": "Use these coordinates", "bn": "এই স্থানাঙ্ক ব্যবহার করুন"},
    "search_radius": {"en": "Search radius", "bn": "অনুসন্ধান পরিসীমা"},
    "search_mosques": {"en": "Search", "bn": "খুঁজুন"},
    "location_detect_failed": {"en": "Could not detect location automatically. Enter coordinates manually below.",
                                "bn": "স্বয়ংক্রিয়ভাবে অবস্থান শনাক্ত করা যায়নি। নিচে ম্যানুয়ালি স্থানাঙ্ক দিন।"},
    "mosque_location_hint": {"en": "Detect your location automatically, or enter coordinates manually.",
                              "bn": "স্বয়ংক্রিয়ভাবে আপনার অবস্থান শনাক্ত করুন, অথবা ম্যানুয়ালি স্থানাঙ্ক দিন।"},
    "mosque_search_failed": {"en": "Could not reach the map service. Check your internet connection and try again.",
                              "bn": "ম্যাপ সার্ভিসে পৌঁছানো যায়নি। ইন্টারনেট সংযোগ পরীক্ষা করে আবার চেষ্টা করুন।"},
    "no_mosques_found": {"en": "No mosques found in this radius. Try a larger radius.", "bn": "এই পরিসীমায় কোনো মসজিদ পাওয়া যায়নি। বড় পরিসীমা চেষ্টা করুন।"},
    "mosques_found": {"en": "{n} mosques found", "bn": "{n}টি মসজিদ পাওয়া গেছে"},
    "nav_settings": {"en": "Settings", "bn": "সেটিংস"},
    "nav_about": {"en": "About", "bn": "সম্পর্কে"},

    # Alarm
    "add_alarm": {"en": "+ Add Alarm", "bn": "+ অ্যালার্ম যোগ করুন"},
    "edit_alarm": {"en": "Edit Alarm", "bn": "অ্যালার্ম সম্পাদনা"},
    "alarm_time": {"en": "Time", "bn": "সময়"},
    "alarm_label": {"en": "Label (optional)", "bn": "লেবেল (ঐচ্ছিক)"},
    "repeat_days": {"en": "Repeat on", "bn": "যেসব দিনে বাজবে"},
    "every_day": {"en": "Every day", "bn": "প্রতিদিন"},
    "alarm_sound": {"en": "Sound", "bn": "শব্দ"},
    "shutdown_on_ring": {"en": "Shut down PC when this alarm rings", "bn": "এই অ্যালার্ম বাজলে পিসি বন্ধ করুন"},
    "shutdown_delay": {"en": "Shutdown countdown (seconds)", "bn": "শাটডাউন কাউন্টডাউন (সেকেন্ড)"},
    "delete": {"en": "Delete", "bn": "মুছে ফেলুন"},
    "no_alarms": {"en": "No alarms yet. Add one to get started.", "bn": "এখনো কোনো অ্যালার্ম নেই। শুরু করতে একটি যোগ করুন।"},
    "stop": {"en": "Stop", "bn": "বন্ধ করুন"},
    "cancel_shutdown": {"en": "Cancel Shutdown", "bn": "শাটডাউন বাতিল করুন"},
    "shutdown_countdown": {"en": "Shutting down in {seconds}s...", "bn": "{seconds} সেকেন্ডে বন্ধ হবে..."},
    "shutdown_cancelled": {"en": "Shutdown cancelled.", "bn": "শাটডাউন বাতিল করা হয়েছে।"},

    # Home
    "current_prayer": {"en": "Current", "bn": "চলমান ওয়াক্ত"},
    "next_prayer_in": {"en": "{remaining} until {next}", "bn": "{next} পর্যন্ত বাকি {remaining}"},
    "todays_prayer_times": {"en": "Today's Prayer Times", "bn": "আজকের নামাজের সময়সূচী"},
    "quick_actions": {"en": "Quick Actions", "bn": "দ্রুত অ্যাক্সেস"},

    # Prayer names
    "prayer_fajr": {"en": "Fajr", "bn": "ফজর"},
    "prayer_sunrise": {"en": "Sunrise", "bn": "সূর্যোদয়"},
    "prayer_dhuhr": {"en": "Dhuhr", "bn": "যোহর"},
    "prayer_asr": {"en": "Asr", "bn": "আসর"},
    "prayer_maghrib": {"en": "Maghrib", "bn": "মাগরিব"},
    "prayer_isha": {"en": "Isha", "bn": "এশা"},

    # Prayer times screen
    "location": {"en": "Location", "bn": "অবস্থান"},
    "select_city": {"en": "Select city", "bn": "শহর নির্বাচন করুন"},
    "manual_location": {"en": "Manual (lat/lon)", "bn": "নিজে নির্ধারণ করুন (অক্ষাংশ/দ্রাঘিমাংশ)"},
    "calc_method": {"en": "Calculation method", "bn": "হিসাব পদ্ধতি"},
    "madhab": {"en": "Asr Madhab", "bn": "আসরের মাযহাব"},
    "hanafi": {"en": "Hanafi", "bn": "হানাফী"},
    "shafi": {"en": "Shafi", "bn": "শাফেয়ী"},
    "azan_settings": {"en": "Azan Settings", "bn": "আজানের সেটিংস"},
    "azan_enabled": {"en": "Play azan", "bn": "আজান বাজবে"},
    "azan_voice": {"en": "Azan voice", "bn": "আজানের কণ্ঠস্বর"},
    "preview": {"en": "Preview", "bn": "প্রিভিউ"},
    "upload_sound": {"en": "Upload your own sound...", "bn": "নিজের শব্দ আপলোড করুন..."},
    "latitude": {"en": "Latitude", "bn": "অক্ষাংশ"},
    "longitude": {"en": "Longitude", "bn": "দ্রাঘিমাংশ"},
    "timezone_offset": {"en": "Timezone offset (UTC)", "bn": "টাইমজোন অফসেট (UTC)"},
    "save": {"en": "Save", "bn": "সংরক্ষণ করুন"},
    "manual_adjustment": {"en": "Manual Adjustment", "bn": "ম্যানুয়াল সমন্বয়"},
    "manual_adjustment_caption": {
        "en": "Shift a prayer time by a few minutes to match your local mosque's "
              "announced schedule. Default is 0 (the originally calculated time).",
        "bn": "স্থানীয় মসজিদের ঘোষিত সময়সূচীর সাথে মিলাতে নামাজের সময় কয়েক মিনিট এদিক-ওদিক করুন। "
              "ডিফল্ট ০ (মূল হিসাবকৃত সময়)।",
    },

    # Azkar / Dua
    "search": {"en": "Search...", "bn": "খুঁজুন..."},
    "morning_azkar": {"en": "Morning & Evening Azkar", "bn": "সকাল সন্ধ্যার আযকার"},
    "self_rukaiya": {"en": "Self Ruqyah", "bn": "সেলফ রুকইয়াহ"},
    "reference": {"en": "Reference", "bn": "রেফারেন্স"},
    "rules": {"en": "Rules", "bn": "নিয়ম"},
    "benefit_hadith": {"en": "Benefit / Hadith", "bn": "ফযীলত / হাদিস"},
    "next": {"en": "Next", "bn": "পরবর্তী"},
    "categories": {"en": "Categories", "bn": "বিষয়সমূহ"},
    "loading": {"en": "Loading...", "bn": "লোড হচ্ছে..."},
    "offline_no_data": {"en": "No internet connection and no cached data yet.",
                         "bn": "ইন্টারনেট সংযোগ নেই এবং কোনো ক্যাশ করা তথ্যও নেই।"},

    # Asmaul Husna
    "ninety_nine_names": {"en": "The 99 Names of Allah", "bn": "আল্লাহর ৯৯টি নাম"},

    # Quran
    "surah_list": {"en": "Surahs", "bn": "সূরাসমূহ"},
    "continue_reading": {"en": "Continue reading", "bn": "পড়া চালিয়ে যান"},
    "verses": {"en": "verses", "bn": "আয়াত"},
    "arabic_text": {"en": "Arabic", "bn": "আরবি"},
    "translation": {"en": "Translation", "bn": "অনুবাদ"},
    "recitation": {"en": "Recitation (Mishary Alafasy)", "bn": "তিলাওয়াত (মিশারী আলাফাসি)"},
    "go_to_bookmark": {"en": "Go to Bookmark", "bn": "বুকমার্কে যান"},

    # Hijri
    "hijri_today": {"en": "Today", "bn": "আজ"},
    "upcoming_events": {"en": "Upcoming Islamic Days", "bn": "আসন্ন ইসলামিক দিবস"},
    "days_left": {"en": "in {n} days", "bn": "{n} দিন বাকি"},
    "today_label": {"en": "Today", "bn": "আজ"},
    "hijri_offset_label": {"en": "Date adjustment (days)", "bn": "তারিখ সমন্বয় (দিন)"},

    # Qibla
    "qibla_bearing": {"en": "Qibla bearing from North", "bn": "উত্তর থেকে কিবলার দিক"},
    "qibla_distance": {"en": "Distance to Kaaba", "bn": "কাবা শরীফের দূরত্ব"},
    "qibla_note": {"en": "Point the top of your screen to this compass "
                         "bearing (use a real compass) to face the Qibla.",
                   "bn": "কিবলামুখী হতে আপনার স্ক্রিনের উপরের দিকটি এই কম্পাস দিকে "
                         "নির্দেশ করুন (একটি প্রকৃত কম্পাস ব্যবহার করুন)।"},

    # Tasbih
    "tasbih_target": {"en": "Target", "bn": "লক্ষ্য"},
    "reset": {"en": "Reset", "bn": "রিসেট"},

    # Settings
    "language": {"en": "Language", "bn": "ভাষা"},
    "theme": {"en": "Theme", "bn": "থিম"},
    "dark_mode": {"en": "Dark mode", "bn": "ডার্ক মোড"},
    "arabic_font": {"en": "Arabic font", "bn": "আরবি ফন্ট"},
    "start_minimized": {"en": "Start minimized to tray", "bn": "ট্রেতে মিনিমাইজড অবস্থায় শুরু করুন"},
    "show_speed_tray": {"en": "Show internet speed in taskbar", "bn": "টাস্কবারে ইন্টারনেট গতি দেখান"},
    "voice_clock": {"en": "Voice Clock", "bn": "ভয়েস ক্লক"},
    "voice_clock_enable": {"en": "Announce the time out loud", "bn": "জোরে সময় ঘোষণা করুন"},
    "voice_clock_interval": {"en": "Every", "bn": "প্রতি"},
    "test": {"en": "Test", "bn": "পরীক্ষা করুন"},
    "azan_behavior": {"en": "Azan Behavior", "bn": "আজানের আচরণ"},
    "close_browsers_on_azan": {"en": "Close web browsers when Azan starts", "bn": "আজান শুরু হলে ওয়েব ব্রাউজার বন্ধ করুন"},
    "close_browsers_caption": {
        "en": "Off by default. When enabled, closes running browsers (Chrome, Edge, Firefox, etc.) a few "
              "seconds after Azan starts, giving you time to cancel. Unsaved work in open tabs may be lost.",
        "bn": "ডিফল্টভাবে বন্ধ থাকে। চালু করলে আজান শুরুর কয়েক সেকেন্ড পর চলমান ব্রাউজার (Chrome, Edge, Firefox ইত্যাদি) "
              "বন্ধ হয়ে যাবে, বাতিল করার জন্য সময় দেওয়া হবে। খোলা ট্যাবের সংরক্ষণ না করা কাজ হারাতে পারে।",
    },
    "close_browsers_delay": {"en": "Countdown before closing (seconds)", "bn": "বন্ধ হওয়ার আগে কাউন্টডাউন (সেকেন্ড)"},
    "close_now": {"en": "Close Now", "bn": "এখনই বন্ধ করুন"},
    "cancel": {"en": "Cancel", "bn": "বাতিল"},
    "closing_browsers_countdown": {"en": "Closing web browsers in {seconds}s...", "bn": "{seconds} সেকেন্ডে ওয়েব ব্রাউজার বন্ধ হবে..."},
    "azan_playing_title": {"en": "Azan", "bn": "আজান"},
    "azan_reminder_text": {
        "en": "The Azan is being called. Pause your work, respond to the Mu'adhdhin, and prepare for Salah.",
        "bn": "আজান দেওয়া হচ্ছে। আপনার কাজ থামান, মুয়াজ্জিনের জবাব দিন এবং সালাতের জন্য প্রস্তুত হোন।",
    },
    "minimize": {"en": "Minimize", "bn": "মিনিমাইজ"},
    "close": {"en": "Close", "bn": "বন্ধ করুন"},
    "developed_by": {"en": "Developed by Engr. Maw. Khandaker Marsus", "bn": "ডেভেলপার: Engr. Maw. Khandaker Marsus"},

    # About
    "about_text": {
        "en": "MuslimDesk is a Windows companion to the IOM Daily Azkar Android app -- "
              "daily azkar, 5x daily azan, Quran, Asmaul Husna, Hijri calendar, Qibla "
              "direction, and a tasbih counter, all running offline in the background.",
        "bn": "মুসলিমডেস্ক হলো IOM Daily Azkar অ্যান্ড্রয়েড অ্যাপের উইন্ডোজ সংস্করণ -- "
              "দৈনিক আযকার, দিনে ৫ বার আজান, কুরআন, আসমাউল হুসনা, হিজরি ক্যালেন্ডার, "
              "কিবলা দিক এবং তাসবীহ কাউন্টার, সবকিছু অফলাইনে ব্যাকগ্রাউন্ডে চলে।",
    },
    "version": {"en": "Version", "bn": "সংস্করণ"},

    # Tray
    "tray_show": {"en": "Show MuslimDesk", "bn": "মুসলিমডেস্ক দেখান"},
    "tray_exit": {"en": "Exit", "bn": "প্রস্থান"},
    "azan_notif_title": {"en": "{prayer} — time for prayer", "bn": "{prayer} এর সময় হয়েছে"},
}


class Translator(QObject):
    language_changed = Signal(str)

    def __init__(self, language: str = "bn") -> None:
        super().__init__()
        self._lang = language

    @property
    def lang(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> None:
        if lang != self._lang:
            self._lang = lang
            self.language_changed.emit(lang)

    def t(self, key: str, **kwargs) -> str:
        entry = _STRINGS.get(key)
        if entry is None:
            return key
        text = entry.get(self._lang, entry.get("en", key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text


translator = Translator()
