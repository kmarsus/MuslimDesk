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
    "open_in_maps": {"en": "Click to open in Google Maps", "bn": "গুগল ম্যাপে খুলতে ক্লিক করুন"},
    "nav_settings": {"en": "Settings", "bn": "সেটিংস"},
    "nav_about": {"en": "About", "bn": "সম্পর্কে"},
    "nav_pc_clean": {"en": "PC Clean", "bn": "পিসি ক্লিন"},
    "nav_whiteboard": {"en": "Whiteboard", "bn": "হোয়াইটবোর্ড"},

    # Whiteboard
    "whiteboard_tool_pen": {"en": "Pen", "bn": "কলম"},
    "whiteboard_tool_line": {"en": "Line", "bn": "লাইন"},
    "whiteboard_tool_arrow": {"en": "Arrow", "bn": "তীর"},
    "whiteboard_tool_rectangle": {"en": "Rectangle", "bn": "আয়তক্ষেত্র"},
    "whiteboard_tool_ellipse": {"en": "Circle / Ellipse", "bn": "বৃত্ত / ডিম্বাকৃতি"},
    "whiteboard_custom_color": {"en": "Custom Color", "bn": "কাস্টম রং"},
    "whiteboard_pen_width": {"en": "Pen size", "bn": "কলমের আকার"},
    "whiteboard_eraser": {"en": "Eraser", "bn": "ইরেজার"},
    "whiteboard_undo": {"en": "Undo", "bn": "পূর্বাবস্থা"},
    "whiteboard_clear": {"en": "Clear", "bn": "সাফ করুন"},
    "whiteboard_save": {"en": "Save as image", "bn": "ছবি হিসেবে সংরক্ষণ করুন"},
    "whiteboard_fullscreen": {"en": "Fullscreen", "bn": "পূর্ণ স্ক্রিন"},
    "whiteboard_exit_fullscreen": {"en": "Exit Fullscreen (Esc)", "bn": "পূর্ণ স্ক্রিন থেকে বের হন (Esc)"},

    # PC Clean
    "pc_clean_heading": {"en": "PC Clean", "bn": "পিসি ক্লিন"},
    "pc_clean_caption": {"en": "Free up space by clearing temporary files. Browser cache and the Recycle Bin are only cleared if you tick them and press Clean.",
                          "bn": "অস্থায়ী ফাইল মুছে জায়গা খালি করুন। ব্রাউজার ক্যাশে এবং রিসাইকেল বিন কেবল আপনি টিক দিয়ে ক্লিন চাপলেই মোছা হবে।"},
    "pc_clean_windows_temp": {"en": "Windows Temp files", "bn": "উইন্ডোজ টেম্প ফাইল"},
    "pc_clean_chrome_cache": {"en": "Google Chrome cache", "bn": "গুগল ক্রোম ক্যাশে"},
    "pc_clean_edge_cache": {"en": "Microsoft Edge cache", "bn": "মাইক্রোসফট এজ ক্যাশে"},
    "pc_clean_firefox_cache": {"en": "Firefox cache", "bn": "ফায়ারফক্স ক্যাশে"},
    "pc_clean_clean_selected": {"en": "Clean Selected", "bn": "নির্বাচিত পরিষ্কার করুন"},
    "pc_clean_recycle_bin": {"en": "Empty Recycle Bin", "bn": "রিসাইকেল বিন খালি করুন"},
    "pc_clean_recycle_bin_caption": {"en": "This permanently deletes everything currently in the Recycle Bin -- it cannot be undone.",
                                      "bn": "এটি রিসাইকেল বিনে থাকা সবকিছু স্থায়ীভাবে মুছে দেবে -- এটি পূর্বাবস্থায় ফেরানো যাবে না।"},
    "pc_clean_empty_recycle_bin_btn": {"en": "Empty Recycle Bin", "bn": "রিসাইকেল বিন খালি করুন"},
    "pc_clean_confirm_recycle_bin": {"en": "Permanently empty the Recycle Bin? This cannot be undone.",
                                      "bn": "রিসাইকেল বিন স্থায়ীভাবে খালি করবেন? এটি ফেরানো যাবে না।"},
    "pc_clean_nothing_selected": {"en": "Select at least one item to clean.", "bn": "পরিষ্কার করতে অন্তত একটি আইটেম নির্বাচন করুন।"},
    "pc_clean_freed": {"en": "{name}: {size} freed", "bn": "{name}: {size} মুক্ত হয়েছে"},
    "pc_clean_recycle_bin_emptied": {"en": "Recycle Bin emptied.", "bn": "রিসাইকেল বিন খালি করা হয়েছে।"},
    "pc_clean_cleaning": {"en": "Cleaning...", "bn": "পরিষ্কার করা হচ্ছে..."},
    "pc_clean_done_message": {"en": "{size} freed! Your PC should feel faster now.",
                               "bn": "{size} মুক্ত হয়েছে! আপনার পিসি এখন আরও দ্রুত মনে হবে।"},

    # Alarm
    "add_alarm": {"en": "+ Add Alarm", "bn": "+ অ্যালার্ম যোগ করুন"},
    "edit_alarm": {"en": "Edit Alarm", "bn": "অ্যালার্ম সম্পাদনা"},
    "alarm_time": {"en": "Time", "bn": "সময়"},
    "alarm_label": {"en": "Label (optional)", "bn": "লেবেল (ঐচ্ছিক)"},
    "repeat_days": {"en": "Repeat on", "bn": "যেসব দিনে বাজবে"},
    "every_day": {"en": "Every day", "bn": "প্রতিদিন"},
    "alarm_sound": {"en": "Sound", "bn": "শব্দ"},
    "default_alarm_sound": {"en": "Default Alarm Sound", "bn": "ডিফল্ট অ্যালার্ম সাউন্ড"},
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
    "morning_azkar": {"en": "Hefazoter Amol", "bn": "হেফাজতের আমল"},
    "self_rukaiya": {"en": "Tibbe Nabawi", "bn": "তিব্বে নববী"},
    "reference": {"en": "Reference", "bn": "রেফারেন্স"},
    "rules": {"en": "Rules", "bn": "নিয়ম"},
    "benefit_hadith": {"en": "Benefit / Hadith", "bn": "ফযীলত / হাদিস"},
    "next": {"en": "Next", "bn": "পরবর্তী"},
    "tier_high_title": {"en": "Level 1 (General Protection)", "bn": "প্রাথমিক স্তর (সাধারণ নিরাপত্তা)"},
    "tier_medium_title": {"en": "Level 2 (Special Protection)", "bn": "দ্বিতীয় স্তর (বিশেষ নিরাপত্তা)"},
    "tier_low_title": {"en": "Level 3 (Advanced Protection)", "bn": "তৃতীয় স্তর (উচ্চমানের নিরাপত্তা)"},
    "mashallah": {"en": "MashaAllah!", "bn": "মাশাআল্লাহ!"},
    "completed_tier_message": {
        "en": 'You have successfully completed the duas of the "{tier}" level.',
        "bn": 'আপনি সফলভাবে "{tier}" পর্যায়ের দোয়াগুলো সম্পন্ন করেছেন।',
    },
    "now_starting_tier": {"en": "Now starting: {tier}", "bn": "এখন শুরু হচ্ছে: {tier}"},
    "continue_btn": {"en": "Continue", "bn": "চালিয়ে যান"},
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
    "go_to_bookmark": {"en": "★ Go to Bookmark", "bn": "★ বুকমার্কে যান"},
    "bookmark": {"en": "☆ Bookmark", "bn": "☆ বুকমার্ক করুন"},
    "bookmarked": {"en": "★ Bookmarked", "bn": "★ বুকমার্ক করা হয়েছে"},
    "play": {"en": "▶ Play", "bn": "▶ চালান"},
    "pause": {"en": "⏸ Pause", "bn": "⏸ থামান"},

    # Hijri
    "hijri_today": {"en": "Today", "bn": "আজ"},
    "upcoming_events": {"en": "Upcoming Islamic Days", "bn": "আসন্ন ইসলামিক দিবস"},
    "days_left": {"en": "in {n} days", "bn": "{n} দিন বাকি"},
    "today_label": {"en": "Today", "bn": "আজ"},
    "hijri_offset_label": {"en": "Date adjustment (days)", "bn": "তারিখ সমন্বয় (দিন)"},
    "siyam_short": {"en": "Siyam", "bn": "সিয়াম"},
    "siyam_tooltip": {"en": "Recommended (sunnah) voluntary fasting day", "bn": "সুন্নাত নফল রোজার দিন"},
    "legend_holiday": {"en": "Friday (holiday)", "bn": "শুক্রবার (সাপ্তাহিক ছুটি)"},
    "legend_siyam": {"en": "Mon/Thu -- Siyam", "bn": "সোম/বৃহঃ -- সিয়াম"},
    "legend_event": {"en": "Islamic day", "bn": "ইসলামিক দিবস"},

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
    "edit_tasbih_target": {"en": "Tasbih Target", "bn": "তাসবীহ লক্ষ্য"},
    "tasbih_name_placeholder": {"en": "e.g. SubhanAllah", "bn": "যেমনঃ সুবহানাল্লাহ"},
    "add_tasbih_target": {"en": "+ Add Target", "bn": "+ লক্ষ্য যোগ করুন"},
    "reset_all": {"en": "Reset All", "bn": "সব রিসেট করুন"},
    "tasbih_targets_title": {"en": "My Targets", "bn": "আমার লক্ষ্যসমূহ"},
    "all_targets_completed": {"en": "🎉 All active targets completed! Add more or reset.",
                               "bn": "🎉 সব সক্রিয় লক্ষ্য সম্পন্ন হয়েছে! আরও যোগ করুন অথবা রিসেট করুন।"},
    "tasbih_tap_hint": {"en": "🖱️ Click the button or ⌨️ press Space to count",
                         "bn": "🖱️ বাটনে ক্লিক করুন অথবা ⌨️ স্পেসবার চাপুন — দুইভাবেই গণনা হবে"},
    "active": {"en": "Active", "bn": "সক্রিয়"},
    "completed": {"en": "Completed", "bn": "সম্পন্ন"},
    "edit": {"en": "Edit", "bn": "সম্পাদনা"},

    # Settings
    "language": {"en": "Language", "bn": "ভাষা"},
    "theme": {"en": "Theme", "bn": "থিম"},
    "dark_mode": {"en": "Dark mode", "bn": "ডার্ক মোড"},
    "arabic_font": {"en": "Arabic font", "bn": "আরবি ফন্ট"},
    "ui_font": {"en": "Interface font (Bangla/English)", "bn": "ইন্টারফেস ফন্ট (বাংলা/ইংরেজি)"},
    "start_minimized": {"en": "Start minimized to tray", "bn": "ট্রেতে মিনিমাইজড অবস্থায় শুরু করুন"},
    "show_speed_tray": {"en": "Show internet speed in taskbar", "bn": "টাস্কবারে ইন্টারনেট গতি দেখান"},
    "show_clock_overlay": {"en": "Show floating clock on screen", "bn": "স্ক্রিনে ভাসমান ঘড়ি দেখান"},
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
        "bn": "আজান হচ্ছে। অনুগ্রহ করে কাজ থামিয়ে মুয়াজ্জিনের জবাব দিন এবং সালাতের প্রস্তুতি নিন। আজান শেষ হলে সব কাজের চেয়ে সালাতকে প্রাধান্য দেওয়াই একজন মুমিনের কর্তব্য।",
    },
    "azan_hadith_text": {
        "en": "On the Day of Judgment, Allah will first take account of prayer. If the prayer is sound, "
              "the rest of one's deeds will be sound; if it is corrupt, all deeds will be corrupt.",
        "bn": "কেয়ামতের দিন আল্লাহ প্রথমে নামাজের হিসাব নেবেন। যদি নামাজ ঠিক থাকে, তবে বাকি কাজও ঠিক থাকবে; "
              "আর যদি নামাজ নষ্ট হয়, তবে সব কাজই নষ্ট হবে।",
    },
    "azan_hadith_ref": {"en": "Sunan al-Tirmidhi, Hadith 413", "bn": "সুনানে তিরমিজি, হাদিস: ৪১৩"},
    "azan_volume_temp_hint": {"en": "Adjusts volume for this Azan only -- resets to full next time",
                               "bn": "শুধু এই আজানের জন্য ভলিউম পরিবর্তন করবে -- পরের আজানে আবার পূর্ণ ভলিউমে ফিরে যাবে"},
    "azan_message_label": {"en": "Azan reminder message", "bn": "আজানের রিমাইন্ডার বার্তা"},
    "reset_default": {"en": "Reset to default", "bn": "ডিফল্টে ফিরুন"},
    "minimize": {"en": "Minimize", "bn": "মিনিমাইজ"},
    "close": {"en": "Close", "bn": "বন্ধ করুন"},
    "developed_by": {
        "en": 'Developed by Engr. Maw. Khandaker Marsus &middot; <a href="https://marsus.com.bd/">marsus.com.bd</a>',
        "bn": 'ডেভেলপার: Engr. Maw. Khandaker Marsus &middot; <a href="https://marsus.com.bd/">marsus.com.bd</a>',
    },

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
