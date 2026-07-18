from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.i18n import translator
from app.paths import icon_path
from app.ui.widgets.card import Card

APP_VERSION = "1.0.5"
REPO_URL = "https://github.com/kmarsus/MuslimDesk"


class AboutView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.heading = QLabel()
        self.heading.setObjectName("Heading")
        layout.addWidget(self.heading)

        self.card = Card(margins=24, spacing=12)

        logo = QLabel()
        pix = QPixmap(str(icon_path("logo.png")))
        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(72, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(logo)

        title = QLabel("MuslimDesk")
        title.setObjectName("Heading")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(title)

        self.version_label = QLabel()
        self.version_label.setObjectName("Muted")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(self.version_label)

        self.about_text_label = QLabel()
        self.about_text_label.setWordWrap(True)
        self.about_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(self.about_text_label)

        link = QLabel(f'<a href="{REPO_URL}">{REPO_URL}</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card.addWidget(link)

        self.credit_label = QLabel()
        self.credit_label.setObjectName("Muted")
        self.credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credit_label.setOpenExternalLinks(True)
        self.card.addWidget(self.credit_label)

        layout.addWidget(self.card)
        layout.addStretch(1)

        translator.language_changed.connect(lambda *_: self.retranslate())
        self.retranslate()

    def retranslate(self) -> None:
        self.heading.setText(translator.t("nav_about"))
        self.version_label.setText(f"{translator.t('version')} {APP_VERSION}")
        self.about_text_label.setText(translator.t("about_text"))
        self.credit_label.setText(translator.t("developed_by"))
