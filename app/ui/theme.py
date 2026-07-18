"""Color palette lifted from lib/core/theme/app_colors.dart (same brand
colors as the Android app) + a QSS stylesheet builder for light/dark mode."""
from __future__ import annotations

from dataclasses import dataclass

from app.ui.spin_arrows import spin_arrow_qss


@dataclass(frozen=True)
class Palette:
    primary_green: str
    secondary_green: str
    light_green: str
    background: str
    ink: str
    ink_light: str
    muted_text: str
    card: str
    border: str
    coral_accent: str
    sun_gold: str
    sidebar_bg: str
    error: str


LIGHT = Palette(
    primary_green="#42A866",
    secondary_green="#4CAF50",
    light_green="#DDEEDB",
    background="#EAF7FF",
    ink="#0B2C4D",
    ink_light="#64748B",
    muted_text="#7B8BA3",
    card="#FFFFFF",
    border="#E5EEF7",
    coral_accent="#FF8B73",
    sun_gold="#FFC46B",
    sidebar_bg="#0B2C4D",
    error="#D32F2F",
)

DARK = Palette(
    primary_green="#42A866",
    secondary_green="#81C784",
    light_green="#103821",
    background="#07111F",
    ink="#F8FAFC",
    ink_light="#CBD5E1",
    muted_text="#94A3B8",
    card="#0F1B2D",
    border="#26374F",
    coral_accent="#FF8B73",
    sun_gold="#FFC46B",
    sidebar_bg="#071D33",
    error="#EF5350",
)


def stylesheet(p: Palette, ui_font: str | None = None) -> str:
    font_stack = "'Segoe UI', 'HindSiliguri', sans-serif"
    if ui_font:
        font_stack = f"'{ui_font}', {font_stack}"
    return f"""
    QWidget {{
        background-color: {p.background};
        color: {p.ink};
        font-family: {font_stack};
        font-size: 13px;
    }}
    QMainWindow {{ background-color: {p.background}; }}

    QLabel, QCheckBox, QRadioButton {{ background-color: transparent; }}

    /* Qt switches QAbstractSpinBox/QCheckBox to CSS-rendered mode as soon as
       any property is set on them via stylesheet -- without explicit
       subcontrol rules below, the spin step-buttons can shrink to a
       near-unclickable sliver and the checkbox indicator can render
       invisible. These rules keep both fully usable and visible. */
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px; height: 16px;
        border: 1.5px solid {p.ink_light};
        border-radius: 4px;
        background-color: {p.card};
    }}
    QRadioButton::indicator {{ border-radius: 8px; }}
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {p.primary_green}; }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {p.primary_green};
        border-color: {p.primary_green};
    }}

    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border; subcontrol-position: top right;
        width: 20px; height: 13px; border-left: 1px solid {p.border};
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border; subcontrol-position: bottom right;
        width: 20px; height: 13px; border-left: 1px solid {p.border};
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {p.light_green};
    }}
    {spin_arrow_qss(p.ink)}

    #Sidebar {{
        background-color: {p.sidebar_bg};
        color: white;
    }}
    #Sidebar QPushButton {{
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 10px;
        background-color: transparent;
        color: #DCE7F0;
        font-size: 13px;
        font-weight: 600;
    }}
    #Sidebar QPushButton:hover {{
        background-color: rgba(255,255,255,0.08);
    }}
    #Sidebar QPushButton:checked {{
        background-color: {p.primary_green};
        color: white;
    }}
    #SidebarTitle {{
        color: white;
        font-size: 17px;
        font-weight: 800;
        padding: 18px 16px 6px 16px;
    }}
    #SidebarFooter {{
        color: rgba(255,255,255,0.45);
        font-size: 10px;
        padding: 10px 8px;
    }}

    #Card {{
        background-color: {p.card};
        border: 1px solid {p.border};
        border-radius: 16px;
    }}
    #HeroCard {{
        background-color: {p.card};
        border: 1px solid {p.border};
        border-radius: 22px;
    }}

    QLabel#Heading {{ font-size: 20px; font-weight: 800; color: {p.ink}; }}
    QLabel#SubHeading {{ font-size: 11px; color: {p.muted_text}; }}
    QLabel#SectionTitle {{ font-size: 15px; font-weight: 800; color: {p.ink}; }}
    QLabel#Muted {{ color: {p.muted_text}; font-size: 11px; }}
    QLabel#PrayerName {{ font-size: 28px; font-weight: 800; color: {p.ink}; }}
    QLabel#Arabic {{ font-size: 22px; color: {p.ink}; }}

    QPushButton {{
        background-color: {p.primary_green};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 700;
    }}
    QPushButton:hover {{ background-color: {p.secondary_green}; }}
    QPushButton:disabled {{ background-color: {p.border}; color: {p.muted_text}; }}
    QPushButton#Ghost {{
        background-color: transparent;
        color: {p.ink};
        border: 1px solid {p.border};
    }}
    QPushButton#Ghost:hover {{ background-color: {p.light_green}; }}
    QPushButton#Ghost:checked {{
        background-color: {p.primary_green};
        color: white;
        border-color: {p.primary_green};
    }}

    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {p.card};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 6px 10px;
        color: {p.ink};
    }}
    QSpinBox, QDoubleSpinBox {{ padding-right: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {p.card};
        color: {p.ink};
        selection-background-color: {p.primary_green};
        selection-color: white;
    }}

    QListWidget, QTreeWidget {{
        background-color: {p.card};
        border: 1px solid {p.border};
        border-radius: 12px;
        outline: none;
    }}
    QListWidget::item, QTreeWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {p.border};
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {p.light_green};
        color: {p.ink};
    }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ width: 10px; background: transparent; }}
    QScrollBar::handle:vertical {{ background: {p.border}; border-radius: 5px; min-height: 24px; }}

    QTabWidget::pane {{ border: 1px solid {p.border}; border-radius: 12px; }}
    QTabBar::tab {{
        background: {p.card}; padding: 8px 16px; margin-right: 4px;
        border-top-left-radius: 8px; border-top-right-radius: 8px;
        color: {p.muted_text}; font-weight: 700;
    }}
    QTabBar::tab:selected {{ background: {p.primary_green}; color: white; }}

    QProgressBar {{
        border: none; border-radius: 8px; background: {p.border}; height: 14px;
        text-align: center; color: {p.ink};
    }}
    QProgressBar::chunk {{ background-color: {p.coral_accent}; border-radius: 8px; }}
    """
