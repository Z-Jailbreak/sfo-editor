"""
BaseMenu - Common base class for all sub-menus.

Provides shared UI components and functionality:
- Top bar with back button, title, and icon
- Translation helper (text())
- Navigation back to main menu
- Style for back button
"""

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
import qtawesome as qta


# Shared style for the rectangular "Back to main menu" button used in sub-menus
BACK_TO_MAIN_STYLE = """
    QPushButton#backToMainButton {
        background-color: #2d2d2d;
        border: 2px solid #3c3c3c;
        border-radius: 12px;
        text-align: left;
        margin-bottom: 2px;
    }
    QPushButton#backToMainButton:hover {
        background-color: #3c3c3c;
        border: 2px solid #0078d4;
    }
"""


class BaseMenu(QWidget):
    """Base widget for all feature sub-menus.

    Handles the common top bar pattern used by Modify SFO, Configurations,
    Settings, and Help menus. Subclasses should call add_top_bar_to_layout()
    in their setup_ui() to include the standardized header.
    """

    def __init__(self, parent=None, title_key="", icon_name="", icon_color="white"):
        super().__init__(parent)
        self.main_window = parent
        self.title_key = title_key          # Translation key for the title
        self.icon_name = icon_name          # FontAwesome icon name (e.g., "fa5s.wrench")
        self.icon_color = icon_color        # Icon color (hex or name)
        self.submenu_title = None           # QLabel for the title (set in setup_top_bar)
        self.setup_top_bar()

    def text(self, key, default=""):
        """Get translated text for a key from the main window's texts dict."""
        texts = getattr(self.main_window, "texts", None) or {}
        return texts.get(key, default)

    def setup_top_bar(self):
        """Build the standard top bar: back button, centered title+icon, dummy spacer."""
        top_container = QWidget()
        top_container.setFixedHeight(50)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # BACK BUTTON (left)
        back_button = QPushButton("\u2190")  # Left arrow
        back_button.setObjectName("backButton")
        back_button.setFixedSize(50, 50)
        back_button.setStyleSheet(self.back_button_style())
        back_button.clicked.connect(self.go_back)

        top_layout.addWidget(back_button)
        top_layout.addStretch()

        # TITLE + ICON (center)
        title_container = QHBoxLayout()
        title_container.setSpacing(10)

        if self.icon_name:
            title_icon = QLabel()
            fa_icon = qta.icon(self.icon_name, color=self.icon_color)
            title_icon.setPixmap(fa_icon.pixmap(QSize(30, 30)))
            title_container.addWidget(title_icon)

        self.submenu_title = QLabel(self.text(self.title_key, ""))
        self.submenu_title.setAlignment(Qt.AlignCenter)
        self.submenu_title.setObjectName("submenuTitle")
        self.submenu_title.setFont(QFont("Arial", 20, QFont.Bold))
        self.submenu_title.setStyleSheet("color: white;")
        self.submenu_title.setProperty("text_key", self.title_key)

        title_container.addWidget(self.submenu_title)
        title_container.addStretch()

        top_layout.addLayout(title_container)
        top_layout.addStretch()

        # DUMMY WIDGET (right) - balances the back button visually
        dummy = QWidget()
        dummy.setFixedSize(50, 50)
        top_layout.addWidget(dummy)

        top_container.setLayout(top_layout)

        # Blue underline separator
        underline = QFrame()
        underline.setObjectName("underline")
        underline.setFixedHeight(2)
        underline.setStyleSheet("background-color: #0078d4;")

        self.top_container = top_container
        self.underline = underline

    def back_button_style(self):
        """QSS stylesheet for the circular back button."""
        return """
            QPushButton#backButton {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
            QPushButton#backButton:hover {
                background-color: #3c3c3c;
                border: 2px solid #0078d4;
            }
            QPushButton#backButton:pressed {
                background-color: #0078d4;
            }
        """

    def go_back(self):
        """Navigate back to the main menu via the main window."""
        if self.main_window:
            self.main_window.go_back_to_main()

    def retranslate_title(self):
        """Update the title label when language changes."""
        if self.submenu_title:
            self.submenu_title.setText(self.text(self.title_key, ""))

    def add_top_bar_to_layout(self, layout):
        """Add the top bar widgets to a parent layout (call from subclass setup_ui)."""
        layout.addWidget(self.top_container)
        layout.addWidget(self.underline)
        layout.addSpacing(1)

    def make_back_to_main_button(self, slot=None, text_key="back_to_main"):
        """Create the standard rectangular 'Back to main menu' button.

        Used in sub-menus (Settings, Help) to return to their main list view.

        Args:
            slot: Callback to connect (default: self.show_main_menu).
            text_key: Translation key for the button text.

        Returns:
            Configured QPushButton instance.
        """
        if slot is None:
            slot = self.show_main_menu

        back_to_main = QPushButton()
        back_to_main.setObjectName("backToMainButton")
        back_to_main.setMinimumHeight(50)
        back_to_main.setStyleSheet(BACK_TO_MAIN_STYLE)

        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(20, 15, 20, 15)
        back_layout.setSpacing(15)

        back_icon = QLabel()
        back_fa_icon = qta.icon("fa5s.arrow-left", color="white")
        back_icon.setPixmap(back_fa_icon.pixmap(QSize(28, 28)))
        back_icon.setStyleSheet("background: transparent;")

        back_text = QLabel(self.text(text_key, "Volver al menú principal"))
        back_text.setFont(QFont("Arial", 13, QFont.Bold))
        back_text.setStyleSheet("color: white; background: transparent;")

        back_layout.addWidget(back_icon)
        back_layout.addWidget(back_text)
        back_layout.addStretch()

        back_to_main.setLayout(back_layout)
        back_to_main.clicked.connect(slot)
        return back_to_main

    def show_main_menu(self):
        """Default implementation - subclasses should override."""
        pass