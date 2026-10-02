import importlib
import math
import os
import platform
import sys

import qtawesome as qta
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from functions.language_manager import (
    check_and_create_config,
    get_saved_language,
    load_all_texts,
    update_ui_texts,
)
from ui.language_manager_menu import get_language


# Main application window
class MainWindow(QMainWindow):
    """Main window of the SFO Save Editor application.

    Manages the primary UI structure:
    - Header with title
    - Main menu grid with feature buttons
    - Stacked widget for sub-menus (Modify SFO, Configs, Help, Settings)
    - Language switching and translation system
    """

    def __init__(self, config_file):
        super().__init__()

        self.config_file = config_file
        # Path to the platform-specific SFO binary (sfo / sfo.exe)
        self.sfo_command = get_sfo_command()
        # Current translation texts (flat dict: key -> translated string)
        self.texts = {}
        # Cache for dynamically loaded UI module classes
        self._ui_classes = {}

        # Definition of main menu buttons: key, icon, module, color, disabled state
        self.buttons_info = [
            {
                "key": "modify_sfo",
                "icon": "fa5s.file-signature",
                "module_name": "sfo_menu",
                "icon_color": "#FFFFFF",
                "disabled": False,
            },
            {
                "key": "configs",
                "icon": "fa5s.wrench",
                "module_name": "configs_menu",
                "icon_color": "#FFFFFF",
                "disabled": False,
            },
            {
                "key": "help",
                "icon": "fa5s.question-circle",
                "module_name": "help_menu",
                "icon_color": "#FFFFFF",
                "disabled": False,
            },
            {
                "key": "settings",
                "icon": "fa5s.cog",
                "module_name": "settings_menu",
                "icon_color": "#FFFFFF",
                "disabled": False,
            },
        ]

        self.texts = self.load_texts()
        self.setup_ui()
        self.setup_styles()
        self.setup_stacked_widgets()

    def load_ui_class(self, module_name):
        """Dynamically import a UI module and return its main class.

        Uses importlib to support PyInstaller frozen executables where
        os.listdir doesn't work. Caches the result for performance.

        Args:
            module_name: Name of the module in ui/ (e.g., "sfo_menu")

        Returns:
            The widget class (e.g., SfoMenu) or None if not found.
        """
        if module_name in self._ui_classes:
            return self._ui_classes[module_name]

        # Convert snake_case module name to PascalCase class name
        class_name = "".join(word.capitalize() for word in module_name.split("_"))
        menu_class = None

        try:
            module = importlib.import_module(f"ui.{module_name}")
            menu_class = getattr(module, class_name, None)
            if menu_class is None:
                print(f"Module ui.{module_name} has no class {class_name}")
        except ModuleNotFoundError as e:
            # Expected when the module itself doesn't exist
            if e.name != f"ui.{module_name}":
                print(f"Error loading module {module_name}: {e}")
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")

        self._ui_classes[module_name] = menu_class
        return menu_class

    def available_buttons(self):
        """Return only buttons whose UI module exists and can be loaded."""
        return [
            info
            for info in self.buttons_info
            if self.load_ui_class(info["module_name"]) is not None
        ]

    def load_texts(self):
        """Load translation texts for the current language.

        Uses Spanish as base language, then overlays the selected language
        so untranslated keys fall back to Spanish instead of being empty.

        Returns:
            Flat dict mapping translation keys to strings.
        """
        lang = get_saved_language(self.config_file) or "en"
        texts = load_all_texts("es")
        if lang != "es":
            texts.update(load_all_texts(lang))
        return texts

    def apply_language(self):
        """Reload translations and apply to all widgets in the window."""
        self.texts = self.load_texts()
        update_ui_texts(self.centralWidget(), self.texts)

        # Call retranslate() on each sub-menu if it exists
        for widget in self.subui.values():
            retranslate = getattr(widget, "retranslate", None)
            if callable(retranslate):
                retranslate()

    def setup_ui(self):
        """Build the main window UI: header, main menu grid, and exit button."""
        self.setWindowTitle("SFO Save Editor")
        self.setFixedSize(800, 600)
        # Only show close and minimize buttons
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # HEADER: title + underline
        self.header_container = QWidget()
        self.header_container.setObjectName("headerContainer")
        self.header_container.setFixedHeight(80)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 0)
        header_layout.setSpacing(5)
        self.header_container.setLayout(header_layout)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")
        self.title_label.setProperty("text_key", "title")

        underline = QFrame()
        underline.setObjectName("underline")
        underline.setFixedHeight(2)

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(underline)

        # Stacked widget holds main screen + sub-menus
        self.stacked_widget = QStackedWidget()

        # MAIN SCREEN: grid of feature buttons
        self.main_screen = QWidget()
        main_screen_layout = QVBoxLayout()
        main_screen_layout.setContentsMargins(40, 30, 40, 10)
        main_screen_layout.setSpacing(20)

        buttons_container = QWidget()
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(20)
        buttons_grid.setContentsMargins(0, 0, 0, 0)

        self.menu_buttons = []

        total = len(self.buttons_info)
        cols = min(4, max(1, math.ceil(math.sqrt(total))))
        rows = math.ceil(total / cols)
        last_count = total - (rows - 1) * cols

        # Create all buttons defined in buttons_info
        for i, button_info in enumerate(self.buttons_info):
            key = button_info["key"]
            icon_name = button_info["icon"]
            icon_color = button_info.get("icon_color", "white")

            button = QPushButton()
            button.setObjectName("menuButton")
            button.setFixedSize(150, 150)
            button.setProperty("button_key", key)

            layout = QVBoxLayout()
            layout.setSpacing(5)
            layout.setContentsMargins(0, 0, 0, 0)

            icon_widget = QLabel()
            icon_widget.setAlignment(Qt.AlignCenter)
            icon_widget.setObjectName("buttonIcon")

            fa_icon = qta.icon(icon_name, color=icon_color)
            pixmap = fa_icon.pixmap(QSize(65, 65))
            icon_widget.setPixmap(pixmap)

            text_label = QLabel()
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setObjectName("buttonText")
            text_label.setFont(QFont("Arial", 14, QFont.Bold))
            text_label.setProperty("text_key", key)

            layout.addStretch()
            layout.addWidget(icon_widget)
            layout.addWidget(text_label)
            layout.addStretch()
            button.setLayout(layout)

            disabled = button_info.get("disabled", False)
            module_missing = self.load_ui_class(button_info["module_name"]) is None

            if disabled or module_missing:
                button.setEnabled(False)
            else:
                button.clicked.connect(lambda _, k=key: self.show_submenu(k))

            row = i // cols
            pos = i % cols
            offset = cols - last_count if row == rows - 1 else 0
            buttons_grid.addWidget(button, row, pos + offset)

            self.menu_buttons.append(button)

        buttons_grid.setAlignment(Qt.AlignCenter)
        buttons_container.setLayout(buttons_grid)

        main_screen_layout.addWidget(buttons_container)
        main_screen_layout.addStretch(1)

        # EXIT BUTTON
        exit_button = QPushButton()
        exit_button.setObjectName("exitButton")
        exit_button.setFixedHeight(52)

        exit_layout = QHBoxLayout()
        exit_layout.setSpacing(15)
        exit_layout.setContentsMargins(20, 0, 20, 0)

        exit_icon = QLabel()
        exit_icon.setAlignment(Qt.AlignCenter)
        exit_icon.setObjectName("exitIcon")

        fa_exit_icon = qta.icon("fa5s.sign-out-alt", color="white")
        exit_icon.setPixmap(fa_exit_icon.pixmap(QSize(36, 36)))

        self.exitText = QLabel()
        self.exitText.setAlignment(Qt.AlignCenter)
        self.exitText.setObjectName("exitText")
        self.exitText.setFont(QFont("Arial", 16, QFont.Bold))
        self.exitText.setProperty("text_key", "exit")

        exit_layout.addWidget(exit_icon)
        exit_layout.addWidget(self.exitText)
        exit_layout.addStretch()

        exit_button.setLayout(exit_layout)
        exit_button.clicked.connect(self.close)

        exit_container = QWidget()
        exit_layout_container = QHBoxLayout()
        exit_layout_container.addStretch()
        exit_layout_container.addWidget(exit_button)
        exit_layout_container.addStretch()
        exit_container.setLayout(exit_layout_container)

        main_screen_layout.addWidget(exit_container)

        self.main_screen.setLayout(main_screen_layout)
        self.stacked_widget.addWidget(self.main_screen)

        main_layout.addWidget(self.header_container)
        main_layout.addWidget(self.stacked_widget)

    def setup_stacked_widgets(self):
        """Instantiate all available sub-menus and add them to the stack."""
        self.subui = {}

        for info in self.available_buttons():
            menu_class = self.load_ui_class(info["module_name"])
            if menu_class is None:
                continue

            try:
                widget = menu_class(self)
            except Exception as e:
                print(f"Error instantiating {info['module_name']}: {e}")
                continue

            self.subui[info["key"]] = widget
            self.stacked_widget.addWidget(widget)

    def show_submenu(self, key):
        """Switch to a sub-menu, hiding the main header."""
        if key in self.subui:
            self.header_container.hide()
            self.stacked_widget.setCurrentWidget(self.subui[key])

    def go_back_to_main(self):
        """Return to the main menu, showing the header."""
        self.header_container.show()
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def setup_styles(self):
        """Apply the global QSS stylesheet for the main window."""
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }

            QLabel#title, QLabel#submenuTitle {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }

            #underline { background-color: #0078d4; }

            QPushButton#menuButton {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 12px;
            }

            QPushButton#menuButton:hover {
                background-color: #3c3c3c;
                border: 2px solid #0078d4;
            }

            QPushButton#menuButton:pressed {
                background-color: #0078d4;
            }

            QPushButton#menuButton:disabled {
                background-color: #1e1e1e;
                border: 2px solid #2d2d2d;
            }

            QLabel#buttonIcon {
                color: #ffffff;
                min-height: 48px;
                min-width: 48px;
            }

            QLabel#buttonText {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }

            QPushButton#exitButton {
                background-color: #2d2d2d;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }

            QPushButton#exitButton:hover {
                background-color: #3c3c3c;
                border: 2px solid #0078d4;
            }

            QPushButton#exitButton:pressed {
                background-color: #0078d4;
            }

            QLabel#exitIcon {
                color: #ffffff;
            }

            QLabel#exitText {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
        """)


# Helper functions
def get_sfo_command():
    """Return the path to the platform-specific SFO binary.

    The binary is located in source/sfo_app/ next to this script.
    """
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfo_app")

    if platform.system() == "Linux":
        return os.path.join(folder, "sfo")
    elif platform.system() == "Windows":
        return os.path.join(folder, "sfo.exe")


def main():
    """Application entry point: initialize Qt, load config, show window."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "icon_sfoeditor.ico"
    )
    app.setWindowIcon(QIcon(icon_path))

    # Dark palette for Fusion style
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    config_file = check_and_create_config()
    get_language(config_file)

    window = MainWindow(config_file)
    window.apply_language()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
